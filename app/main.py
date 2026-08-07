import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.db import run_query
from app.llm import finish_trace, generate_answer, generate_sql, start_trace
from app.schema_context import render_schema_context
from app.sql_guardrails import SqlValidationError, validate_and_prepare, validate_tenant_id
from app.webhooks import report_ai_credit_usage

app = FastAPI(title="Learnostic Assistant")


class AskRequest(BaseModel):
    question: str
    tenant_id: int


class Table(BaseModel):
    columns: list[str]
    rows: list[list[str]]


class AskResponse(BaseModel):
    answer: str
    sql: str
    table: Table | None = None


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


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
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
        report_ai_credit_usage(request.tenant_id, total_cost_usd)
        return AskResponse(answer=reasoning, sql="")

    try:
        validated_sql = validate_and_prepare(generated_sql)
    except SqlValidationError as exc:
        finish_trace(trace, sql=generated_sql, answer=f"[rejected sql] {exc}")
        report_ai_credit_usage(request.tenant_id, total_cost_usd)
        raise HTTPException(status_code=422, detail=f"Generated query rejected: {exc}") from exc

    try:
        rows = run_query(tenant_schema, validated_sql)
    except (pymysql.err.OperationalError, OSError) as exc:
        # TODO: this leaks driver/connection internals in the response body —
        # fine while debugging locally, but switch to the generic message
        # before this is reachable from anywhere but localhost.
        finish_trace(trace, sql=validated_sql, answer=f"[db error] {exc}")
        report_ai_credit_usage(request.tenant_id, total_cost_usd)
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach the database replica: {exc}",
        ) from exc

    answer, answer_cost_usd = generate_answer(request.question, validated_sql, rows, trace=trace)
    total_cost_usd += answer_cost_usd
    finish_trace(trace, sql=validated_sql, answer=answer)
    report_ai_credit_usage(request.tenant_id, total_cost_usd)

    return AskResponse(answer=answer, sql=validated_sql, table=_build_table(rows))
