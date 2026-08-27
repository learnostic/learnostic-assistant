import json
from typing import Literal

import pymysql
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from botocore.exceptions import ClientError

from app.db import run_query
from app.llm import classify_lead_status, finish_trace, generate_answer, generate_answer_json, generate_pdf_answer_stream, generate_sql, start_trace
from app.pdf_qa import get_index
from app.schema_context import render_schema_context
from app.sql_guardrails import SqlValidationError, validate_and_prepare, validate_tenant_id
from app.webhooks import report_ai_credit_usage

app = FastAPI(title="Learnostic Assistant")


class AskRequest(BaseModel):
    question: str
    tenant_id: int
    tenant_name: str


class Table(BaseModel):
    columns: list[str]
    rows: list[list[str]]


class AskResponse(BaseModel):
    answer: str
    sql: str
    table: Table | None = None


class AskJsonResponse(BaseModel):
    answer: dict
    sql: str
    table: Table | None = None


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class PdfAskRequest(BaseModel):
    question: str
    tenant_id: int
    tenant_name: str
    history: list[HistoryMessage] = []


def _build_table(rows: list[dict]) -> Table | None:
    # A single scalar (one row, one column) reads better as a sentence than
    # a table — only tabulate when there's an actual grid of data.
    if not rows or (len(rows) == 1 and len(rows[0]) == 1):
        return None
    columns = list(rows[0].keys())
    return Table(columns=columns, rows=[[str(row[col]) for col in columns] for row in rows])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _run_pipeline(request: AskRequest):
    """Shared question -> SQL -> rows pipeline used by both /ask/text and /ask/json.

    Returns (trace, sql, rows, reasoning, cost_usd). sql=="" and rows==[] mean
    no query could be generated — reasoning explains why and the caller
    should return early. Raises HTTPException on validation/db errors.
    """
    trace = start_trace(request.question, str(request.tenant_id))

    try:
        # Each tenant is a separate MySQL database named customer_<tenant_id>
        # (schema-per-tenant) — this builds and validates that schema name.
        tenant_schema = validate_tenant_id(request.tenant_id)
    except SqlValidationError as exc:
        finish_trace(trace, sql="", answer=f"[rejected tenant_id] {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    schema_context = render_schema_context()
    generated_sql, reasoning, sql_cost_usd = generate_sql(request.question, schema_context, trace=trace)
    total_cost_usd = sql_cost_usd

    if not generated_sql:
        finish_trace(trace, sql="", answer=reasoning)
        report_ai_credit_usage(request.tenant_id, request.tenant_name, total_cost_usd)
        return trace, "", [], reasoning, total_cost_usd

    try:
        validated_sql = validate_and_prepare(generated_sql)
    except SqlValidationError as exc:
        finish_trace(trace, sql=generated_sql, answer=f"[rejected sql] {exc}")
        report_ai_credit_usage(request.tenant_id, request.tenant_name, total_cost_usd)
        raise HTTPException(status_code=422, detail=f"Generated query rejected: {exc}") from exc

    try:
        rows = run_query(tenant_schema, validated_sql)
    except (pymysql.err.OperationalError, OSError) as exc:
        # TODO: this leaks driver/connection internals in the response body —
        # fine while debugging locally, but switch to the generic message
        # before this is reachable from anywhere but localhost.
        finish_trace(trace, sql=validated_sql, answer=f"[db error] {exc}")
        report_ai_credit_usage(request.tenant_id, request.tenant_name, total_cost_usd)
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach the database replica: {exc}",
        ) from exc

    return trace, validated_sql, rows, reasoning, total_cost_usd


@app.post("/ask/text", response_model=AskResponse)
def ask_text(request: AskRequest) -> AskResponse:
    trace, sql, rows, reasoning, total_cost_usd = _run_pipeline(request)

    if not sql:
        return AskResponse(answer=reasoning, sql="")

    answer, answer_cost_usd = generate_answer(request.question, sql, rows, trace=trace)
    total_cost_usd += answer_cost_usd
    finish_trace(trace, sql=sql, answer=answer)
    report_ai_credit_usage(request.tenant_id, request.tenant_name, total_cost_usd)

    return AskResponse(answer=answer, sql=sql, table=_build_table(rows))


@app.post("/ask/json", response_model=AskJsonResponse)
def ask_json(request: AskRequest) -> AskJsonResponse:
    trace, sql, rows, reasoning, total_cost_usd = _run_pipeline(request)

    if not sql:
        answer = {"summary": reasoning, "empty": True, "ambiguous": False}
        return AskJsonResponse(answer=answer, sql="")

    answer, answer_cost_usd = generate_answer_json(request.question, sql, rows, trace=trace)
    total_cost_usd += answer_cost_usd
    finish_trace(trace, sql=sql, answer=json.dumps(answer))
    report_ai_credit_usage(request.tenant_id, request.tenant_name, total_cost_usd)

    return AskJsonResponse(answer=answer, sql=sql, table=_build_table(rows))


@app.post("/ask/learnostic-documents")
def ask_pdf(request: PdfAskRequest) -> StreamingResponse:
    trace = start_trace(request.question, str(request.tenant_id))

    try:
        index = get_index()
    except ClientError as exc:
        finish_trace(trace, sql="", answer=f"[pdf index error] {exc}")
        raise HTTPException(status_code=503, detail=f"Could not load the reference document: {exc}") from exc

    relevant_pages = index.retrieve(request.question)
    history = [turn.model_dump() for turn in request.history]

    # Classified before the streamed reply starts, since the reply's tone
    # (see STATUS_GUIDANCE) depends on it — this is a real added delay
    # (a full extra model round trip) before the first token, traded for a
    # reply that actually behaves differently at each stage of the lead's
    # conversation rather than just a fixed persona.
    lead_status = classify_lead_status(request.question, history=history, trace=trace)

    def stream_answer():
        # No cost webhook for this endpoint (unlike /ask/text and
        # /ask/json) — accumulate only for the trailing Langfuse trace.
        chunks = []
        try:
            for chunk in generate_pdf_answer_stream(
                request.question,
                relevant_pages,
                history=history,
                lead_status=lead_status,
                trace=trace,
            ):
                chunks.append(chunk)
                yield chunk
        finally:
            finish_trace(trace, sql="", answer="".join(chunks))

    return StreamingResponse(stream_answer(), media_type="text/plain")
