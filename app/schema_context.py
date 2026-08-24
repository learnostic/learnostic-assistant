# Schema context is sourced live from S3 (see app/schema_source.py), not
# hardcoded here — mpa-app exports it fresh on every deploy via
# `php artisan mpa:export-ai-schema`, so this file can no longer drift out of
# sync with the real tenant schema the way a hand-maintained dict would.
#
# Sensitive columns (password, remember_token, secret, otp*, salary,
# national_id_number, passport_number, login_name, etc.) are stripped at
# export time on the mpa-app side (ExportAiSchema.php's $excludedColumns) —
# they never reach this process at all, not just hidden from the prompt.

from app.schema_source import get_schema


def get_allowed_tables() -> dict[str, list[str]]:
    """table -> column names. This is the security allowlist sql_guardrails.py
    validates every generated query against — not just prompt context."""
    return {
        name: [column["name"] for column in table["columns"]]
        for name, table in get_schema()["tables"].items()
    }


def render_schema_context() -> str:
    schema = get_schema()
    tables = schema["tables"]

    table_lines = []
    relationship_lines = []
    for name, table in tables.items():
        columns = ", ".join(column["name"] for column in table["columns"])
        table_lines.append(f"- {name}({columns})")

        if table.get("description"):
            table_lines.append(f"  {name}: {table['description']}")
        for column in table["columns"]:
            if column.get("description"):
                table_lines.append(f"  {name}.{column['name']}: {column['description']}")

        for fk in table.get("foreign_keys", []):
            relationship_lines.append(
                f"{name}.{fk['column']} -> {fk['references_table']}.{fk['references_column']}"
            )

    examples = schema.get("examples", {})
    example_lines = [f"- {key}: {value}" for key, value in examples.items() if isinstance(value, str)]
    ai_rules = examples.get("ai_rules", [])
    rule_lines = [f"- {rule}" for rule in ai_rules]

    sections = [
        "Tables (inline notes, where present, explain non-obvious columns "
        "including status/type codes — read them, don't guess):\n"
        + "\n".join(table_lines),
        "Foreign key relationships (use these for JOINs — do not guess a "
        "join column that isn't listed here):\n" + "\n".join(relationship_lines),
    ]
    if example_lines:
        sections.append("Worked examples (cross-table reasoning references):\n" + "\n".join(example_lines))
    if rule_lines:
        sections.append("Domain rules:\n" + "\n".join(rule_lines))

    return "\n\n".join(sections)
