import re

from app.schema_context import get_allowed_tables

DEFAULT_ROW_LIMIT = 500

DISALLOWED_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "GRANT",
    "REVOKE", "CREATE", "ATTACH", "COPY", "CALL", "EXECUTE", "MERGE",
    "VACUUM", "REINDEX", "SET", "RESET",
)

TABLE_REF_RE = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)

# Matches a bare column reference (optionally table-qualified) that is NOT
# immediately followed by "(" — that exclusion is what filters out function
# names like COUNT/MAX/COALESCE without needing to hardcode a function list.
COLUMN_TOKEN_RE = re.compile(r"(?:[a-zA-Z_][a-zA-Z0-9_]*\.)?([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*\()")
STAR_PROJECTION_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\.\*")
STRING_LITERAL_RE = re.compile(r"'[^']*'|\"[^\"]*\"")
AS_ALIAS_RE = re.compile(r"\bAS\s+[a-zA-Z_][a-zA-Z0-9_]*\b", re.IGNORECASE)
LEADING_SELECT_RE = re.compile(r"^\s*SELECT\s+(DISTINCT\s+)?", re.IGNORECASE)

SELECT_LIST_IGNORE_TOKENS = {
    "distinct", "true", "false", "null",
    # CASE-expression keywords — bare tokens like "case column_list" would
    # otherwise get scanned by COLUMN_TOKEN_RE as if they were column
    # references, since they aren't followed by "(" the way a function call
    # is. This came up for real: SUM(CASE WHEN method IN (...) THEN 1 ELSE 0
    # END) got rejected because "case" wasn't allowlisted.
    "case", "when", "then", "else", "end",
}

def _allowed_columns() -> set[str]:
    # get_allowed_tables() reads from schema_source's process-lifetime cache
    # (see app/schema_source.py) — this is a cheap dict comprehension over
    # already-fetched data, not a network call, so recomputing per validation
    # call is fine.
    return {
        column.lower()
        for columns in get_allowed_tables().values()
        for column in columns
    }


class SqlValidationError(ValueError):
    pass


def validate_tenant_id(tenant_id: int) -> str:
    """tenant_id is the numeric tenant id sent by the caller. Each tenant is
    a separate MySQL database named customer_<id> (schema-per-tenant) —
    build and validate that schema name before it's used as a MySQL
    connection parameter."""
    if isinstance(tenant_id, bool) or not isinstance(tenant_id, int) or tenant_id <= 0:
        raise SqlValidationError(f"Invalid tenant id: {tenant_id!r}")
    return f"customer_{tenant_id}"


def _find_top_level_from_index(body: str) -> int:
    """Scans for the first FROM keyword outside of any parentheses, so a
    subquery in the SELECT list (e.g. a scalar subselect) doesn't get
    mistaken for the query's own FROM clause."""
    depth = 0
    for match in re.finditer(r"\(|\)|\bFROM\b", body, re.IGNORECASE):
        token = match.group(0)
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
        elif depth == 0:
            return match.start()
    raise SqlValidationError("Could not locate a top-level FROM clause")


def _validate_select_columns(body: str) -> None:
    from_index = _find_top_level_from_index(body)
    select_match = LEADING_SELECT_RE.match(body)
    column_list = body[select_match.end():from_index]

    if column_list.strip() == "*":
        raise SqlValidationError("SELECT * is not allowed — select explicit columns")
    if STAR_PROJECTION_RE.search(column_list):
        raise SqlValidationError("table.* is not allowed — select explicit columns")

    cleaned = STRING_LITERAL_RE.sub("''", column_list)
    cleaned = AS_ALIAS_RE.sub("", cleaned)

    for match in COLUMN_TOKEN_RE.finditer(cleaned):
        column = match.group(1).lower()
        if column in SELECT_LIST_IGNORE_TOKENS:
            continue
        if column not in _allowed_columns():
            raise SqlValidationError(f"Query selects a non-allowlisted column: {column}")


def validate_and_prepare(sql: str) -> str:
    stripped = sql.strip()
    if not stripped:
        raise SqlValidationError("Empty SQL")

    if "--" in stripped or "/*" in stripped:
        raise SqlValidationError("Comments are not allowed in generated SQL")

    body = stripped[:-1] if stripped.endswith(";") else stripped
    if ";" in body:
        raise SqlValidationError("Multiple statements are not allowed")

    if not re.match(r"^\s*SELECT\b", body, re.IGNORECASE):
        raise SqlValidationError("Only SELECT statements are allowed")

    for keyword in DISALLOWED_KEYWORDS:
        if re.search(rf"\b{keyword}\b", body, re.IGNORECASE):
            raise SqlValidationError(f"Disallowed keyword in query: {keyword}")

    referenced_tables = {match.lower() for match in TABLE_REF_RE.findall(body)}
    allowed_tables = {t.lower() for t in get_allowed_tables()}
    disallowed_tables = referenced_tables - allowed_tables
    if disallowed_tables:
        raise SqlValidationError(f"Query references non-allowlisted table(s): {disallowed_tables}")

    _validate_select_columns(body)

    if not re.search(r"\bLIMIT\s+\d+\b", body, re.IGNORECASE):
        body = f"{body} LIMIT {DEFAULT_ROW_LIMIT}"

    return body
