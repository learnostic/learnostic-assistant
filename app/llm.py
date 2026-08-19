import json

from anthropic import AnthropicBedrockMantle

from app.config import settings

client = AnthropicBedrockMantle(aws_region=settings.bedrock_region)


def _init_langfuse():
    try:
        from langfuse import Langfuse

        if settings.langfuse_base_url and settings.langfuse_secret_key and settings.langfuse_public_key:
            langfuse_client = Langfuse(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_base_url,
            )
            print("[Langfuse] Tracing client initialized", flush=True)
            return langfuse_client
    except Exception as exc:
        print(f"[Langfuse] Failed to initialize tracing client: {exc}", flush=True)
    return None


_langfuse = _init_langfuse()


def start_trace(question: str, tenant_id: str):
    if not _langfuse:
        return None
    return _langfuse.trace(
        name="ask",
        user_id=tenant_id,
        input={"question": question, "tenant_id": tenant_id},
    )


def finish_trace(trace, sql: str, answer: str) -> None:
    if not trace:
        return
    trace.update(output={"sql": sql, "answer": answer})
    _langfuse.flush()

SQL_SYSTEM_PROMPT = """\
You translate staff questions about students into a single read-only SQL \
query for a MySQL 8 database.

Rules:
- Only ever produce a SELECT statement. Never write, update, delete, or \
  modify data or schema.
- Only reference the tables and columns listed below. Do not invent tables \
  or columns.
- Do not schema-qualify table names — the caller selects the tenant's \
  database via the connection, not via the query.
- Use MySQL syntax only. Do NOT use functions from other databases — most \
  importantly, MySQL has no DATE_TRUNC(); use DATE_FORMAT(col, '%Y-%m-%d'), \
  YEAR(col), MONTH(col), or DATE_SUB(CURDATE(), INTERVAL n DAY/MONTH) \
  instead. Quote reserved-word column names (e.g. `start`, `end`) with \
  backticks.
- If the question cannot be answered with these tables, return an empty \
  string for "sql" and explain why in "reasoning".
- Use the foreign key relationships listed below for JOINs. Do not invent a \
  join column that isn't listed — if two tables you need aren't connected by \
  a listed relationship (possibly via an intermediate table), say so in \
  "reasoning" instead of guessing a join.
- "status"-type columns are integers, not strings. Never write \
  `status = 'active'` or `status = 'pending'` — MySQL will silently coerce \
  an unrecognized string to 0 instead of erroring, giving a confidently \
  wrong answer. Always use the numeric code from the status reference below, \
  e.g. `status = 1`. If a status word in the question doesn't map cleanly to \
  one of the listed codes, say so in "reasoning" instead of guessing.
- More generally: many other integer columns across these tables are also \
  coded/enum-like (type, method, difficulty, etc.) but aren't documented \
  below. Never guess what a numeric code means for a column that isn't in \
  the status reference — filter on it only if the question gives you the \
  actual number, otherwise say in "reasoning" that the code mapping isn't \
  known.
- When the question filters on a name or any other attribute that isn't \
  guaranteed unique (first_name, last_name, school, etc.), do NOT collapse \
  the result into a single aggregate — that silently combines different \
  people into one misleading number. Instead, include identifying columns \
  (first_name, last_name, email, or similar human-readable attributes) in \
  the SELECT list and GROUP BY them, so each matching person's result stays \
  separate. Only aggregate freely when filtering by a column that is \
  actually unique per person (e.g. student id).
- Never include an `id` column, or any other primary/foreign key id (e.g. \
  student_id, invoice_id), in the SELECT list — these are internal database \
  identifiers with no meaning to staff. Use them freely in WHERE/JOIN/EXISTS \
  clauses, just never put them in the output columns. Use human-readable \
  columns (name, email, date, status label, etc.) instead when the result \
  needs to identify a row.

{schema}

Respond with ONLY a JSON object of the form:
{{"sql": "<the query, or empty string>", "reasoning": "<one sentence>"}}
No markdown, no code fences, no text before or after the JSON.
"""


def _parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())


# Claude Sonnet 5 pricing per 1M tokens (Bedrock matches first-party rates).
SONNET_5_INPUT_COST_PER_1M_USD = 3.0
SONNET_5_OUTPUT_COST_PER_1M_USD = 15.0


def _calc_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * SONNET_5_INPUT_COST_PER_1M_USD
        + output_tokens * SONNET_5_OUTPUT_COST_PER_1M_USD
    ) / 1_000_000


def generate_sql(question: str, schema_context: str, trace=None) -> tuple[str, str, float]:
    generation = None
    if trace:
        generation = trace.generation(
            name="generate-sql",
            model=settings.bedrock_model_id,
            input=question,
        )

    # schema_context is identical on every request (same 89 tables regardless
    # of tenant/question) — cache it so we're not re-paying for ~17K chars of
    # schema text on every single call.
    response = client.messages.create(
        model=settings.bedrock_model_id,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": SQL_SYSTEM_PROMPT.format(schema=schema_context),
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": question}],
    )
    text = next(block.text for block in response.content if block.type == "text")
    parsed = _parse_json_response(text)
    cost_usd = _calc_cost(response.usage.input_tokens, response.usage.output_tokens)

    if generation:
        generation.end(
            output=parsed,
            usage={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens,
                "unit": "TOKENS",
            },
        )

    return parsed["sql"], parsed["reasoning"], cost_usd


def generate_answer(question: str, sql: str, rows: list[dict], trace=None) -> tuple[str, float]:
    generation = None
    if trace:
        generation = trace.generation(
            name="generate-answer",
            model=settings.bedrock_model_id,
            input={"question": question, "sql": sql, "row_count": len(rows)},
        )

    response = client.messages.create(
        model=settings.bedrock_model_id,
        max_tokens=1024,
        system=(
            "You turn SQL query results into a short, plain-English answer "
            "for Learnostic staff. Be direct and concise. If the result set "
            "is empty, say so plainly. Respond in plain text only — no "
            "markdown, no **bold**, no bullet points, no headers. This is "
            "rendered as-is, not through a markdown parser.\n\n"
            "If the rows contain more than one distinct person (e.g. "
            "several students sharing a first name), do NOT state one "
            "combined number as if it were about a single person. List "
            "each person with their own result, then ask which one the "
            "staff member meant — e.g. \"There are 3 students named Ali: "
            "Ali Bindrai (12 lessons), Ali Mathani (7 lessons), Ali Farag "
            "(3 lessons). Which one did you mean?\""
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"SQL run: {sql}\n\n"
                    f"Results (JSON): {json.dumps(rows, default=str)}"
                ),
            }
        ],
    )
    answer = next(block.text for block in response.content if block.type == "text")
    cost_usd = _calc_cost(response.usage.input_tokens, response.usage.output_tokens)

    if generation:
        generation.end(
            output=answer,
            usage={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens,
                "unit": "TOKENS",
            },
        )

    return answer, cost_usd


ANSWER_JSON_SYSTEM_PROMPT = """\
You turn SQL query results into a structured answer for Learnostic staff.

Respond with ONLY a JSON object of this exact form:
{"summary": "<one short plain-English sentence>", "empty": <true|false>, \
"ambiguous": <true|false>}

Rules:
- If the result set is empty, set "empty": true.
- If the rows contain more than one distinct person (e.g. several students \
  sharing a first name), set "ambiguous": true and phrase "summary" as a \
  clarifying question referencing the rows (e.g. "There are 3 students \
  named Ali — did you mean one of these?"), since the caller renders the \
  underlying rows alongside your summary for the user to pick from. Do not \
  collapse them into one combined number.
- Otherwise set "ambiguous": false.
- No markdown, no code fences, no text before or after the JSON object.
"""


def generate_answer_json(question: str, sql: str, rows: list[dict], trace=None) -> tuple[dict, float]:
    generation = None
    if trace:
        generation = trace.generation(
            name="generate-answer-json",
            model=settings.bedrock_model_id,
            input={"question": question, "sql": sql, "row_count": len(rows)},
        )

    response = client.messages.create(
        model=settings.bedrock_model_id,
        max_tokens=1024,
        system=ANSWER_JSON_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"SQL run: {sql}\n\n"
                    f"Results (JSON): {json.dumps(rows, default=str)}"
                ),
            }
        ],
    )
    text = next(block.text for block in response.content if block.type == "text")
    answer = _parse_json_response(text)
    cost_usd = _calc_cost(response.usage.input_tokens, response.usage.output_tokens)

    if generation:
        generation.end(
            output=answer,
            usage={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens,
                "unit": "TOKENS",
            },
        )

    return answer, cost_usd


MAX_HISTORY_TURNS = 10


def generate_pdf_answer(
    question: str,
    context_pages: list[str],
    history: list[dict] | None = None,
    trace=None,
) -> tuple[str, float]:
    generation = None
    if trace:
        generation = trace.generation(
            name="generate-pdf-answer",
            model=settings.bedrock_model_id,
            input={"question": question, "page_count": len(context_pages)},
        )

    context = "\n\n---\n\n".join(context_pages)

    # History is held by the caller (not persisted here) and just replayed as
    # prior turns so a follow-up like "yes, Tuesday at 3" still has context.
    prior_turns = [
        {"role": turn["role"], "content": turn["content"]}
        for turn in (history or [])[-MAX_HISTORY_TURNS:]
    ]

    response = client.messages.create(
        model=settings.bedrock_model_id,
        max_tokens=1024,
        system=(
            "You are speaking directly with a lead (a prospective customer) "
            "who asked a question. The excerpts below are internal reference "
            "material describing how our team approaches this topic — they "
            "exist to inform your understanding, not to be quoted or pasted "
            "back. Using your understanding of the excerpts, answer the "
            "lead's question in your own words, the way a knowledgeable staff "
            "member would explain it in conversation. Never mention the "
            "excerpts, documents, or internal materials, and never copy their "
            "wording verbatim. If the excerpts don't give you enough to "
            "answer confidently, say so plainly instead of guessing. After "
            "answering, end with one short sentence that naturally invites "
            "the lead to book an assessment and visit the center — tailor it "
            "to the specific topic they asked about (e.g. an answer about "
            "how assessments work should nudge them to book one and see it "
            "firsthand) rather than using a generic, repeated pitch.\n\n"
            "If the lead asks to book an assessment, ask which date and time "
            "works for them. Once they give you a date and time, confirm the "
            "assessment is booked for that date and time — do not ask for "
            "any other details. Respond in plain text only — no markdown, "
            "no **bold**, no bullet points, no headers."
        ),
        messages=[
            *prior_turns,
            {
                "role": "user",
                "content": f"Document excerpts:\n\n{context}\n\nQuestion: {question}",
            },
        ],
    )
    answer = next(block.text for block in response.content if block.type == "text")
    cost_usd = _calc_cost(response.usage.input_tokens, response.usage.output_tokens)

    if generation:
        generation.end(
            output=answer,
            usage={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": response.usage.input_tokens + response.usage.output_tokens,
                "unit": "TOKENS",
            },
        )

    return answer, cost_usd
