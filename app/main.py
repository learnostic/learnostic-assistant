import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.db import run_query
from app.llm import generate_answer, generate_sql
from app.schema_context import render_schema_context
from app.sql_guardrails import SqlValidationError, validate_and_prepare, validate_tenant_id

app = FastAPI(title="Learnostic Assistant")


class AskRequest(BaseModel):
    question: str
    tenant_id: str


class AskResponse(BaseModel):
    answer: str
    sql: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        # tenant_id is already the full per-tenant database name (e.g.
        # "customer_1"), as sent by the Next.js layer — not a bare id to
        # prefix here.
        tenant_schema = validate_tenant_id(request.tenant_id)
    except SqlValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    schema_context = render_schema_context()
    generated_sql, reasoning = generate_sql(request.question, schema_context)

    if not generated_sql:
        return AskResponse(answer=reasoning, sql="")

    try:
        validated_sql = validate_and_prepare(generated_sql)
    except SqlValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Generated query rejected: {exc}") from exc

    try:
        rows = run_query(tenant_schema, validated_sql)
    except (pymysql.err.OperationalError, OSError) as exc:
        # TODO: this leaks driver/connection internals in the response body —
        # fine while debugging locally, but switch to the generic message
        # before this is reachable from anywhere but localhost.
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach the database replica: {exc}",
        ) from exc

    answer = generate_answer(request.question, validated_sql, rows)

    return AskResponse(answer=answer, sql=validated_sql)
