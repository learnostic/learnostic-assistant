import json
from pathlib import Path

# Tenant DB schema + hand-written semantic descriptions, maintained directly
# in this repo (app/schema_data.json) rather than pulled from mpa-app at
# runtime. The schema changes rarely, and edits to the semantic notes
# (table/column descriptions, worked examples, domain rules) happen here —
# update app/schema_data.json by hand when the DB schema changes or a note
# needs adding.
_SCHEMA_PATH = Path(__file__).parent / "schema_data.json"

_schema: dict | None = None


def get_schema() -> dict:
    global _schema
    if _schema is None:
        _schema = json.loads(_SCHEMA_PATH.read_text())
    return _schema
