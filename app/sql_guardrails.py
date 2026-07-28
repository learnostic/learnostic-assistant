import re

from app.schema_context import ALLOWED_TABLES

DEFAULT_ROW_LIMIT = 500

DISALLOWED_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "GRANT",
    "REVOKE", "CREATE", "ATTACH", "COPY", "CALL", "EXECUTE", "MERGE",
    "VACUUM", "REINDEX", "SET", "RESET",
)

TABLE_REF_RE = re.compile(r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)", re.IGNORECASE)
TENANT_ID_RE = re.compile(r"^[a-zA-Z0-9_]+$")

# Matches a bare column reference (optionally table-qualified) that is NOT
# immediately followed by "(" — that exclusion is what filters out function
# names like COUNT/MAX/COALESCE without needing to hardcode a function list.
COLUMN_TOKEN_RE = re.compile(r"(?:[a-zA-Z_][a-zA-Z0-9_]*\.)?([a-zA-Z_][a-zA-Z0-9_]*)\b(?!\s*\()")
STAR_PROJECTION_RE = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\.\*")
STRING_LITERAL_RE = re.compile(r"'[^']*'|\"[^\"]*\"")
AS_ALIAS_RE = re.compile(r"\bAS\s+[a-zA-Z_][a-zA-Z0-9_]*\b", re.IGNORECASE)
LEADING_SELECT_RE = re.compile(r"^\s*SELECT\s+(DISTINCT\s+)?", re.IGNORECASE)

SELECT_LIST_IGNORE_TOKENS = {"distinct", "true", "false", "null"}

ALLOWED_COLUMNS = {
    column.lower()
    for columns in ALLOWED_TABLES.values()
    for column in columns
}


class SqlValidationError(ValueError):
    pass


def validate_tenant_id(tenant_id: str) -> str:
    """Tenant id is used to build the per-tenant database name passed to the
    MySQL connection — validate strictly before use even though the driver
    passes it as a connection parameter rather than interpolated SQL."""
    if not tenant_id or not TENANT_ID_RE.match(tenant_id):
        raise SqlValidationError(f"Invalid tenant id: {tenant_id!r}")
    return tenant_id


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
        if column not in ALLOWED_COLUMNS:
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
    allowed_tables = {t.lower() for t in ALLOWED_TABLES}
    disallowed_tables = referenced_tables - allowed_tables
    if disallowed_tables:
        raise SqlValidationError(f"Query references non-allowlisted table(s): {disallowed_tables}")

    _validate_select_columns(body)

    if not re.search(r"\bLIMIT\s+\d+\b", body, re.IGNORECASE):
        body = f"{body} LIMIT {DEFAULT_ROW_LIMIT}"

    return body
