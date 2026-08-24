import json

import boto3

from app.config import settings

_s3 = boto3.client("s3", region_name=settings.aws_region)


def _fetch_current_pointer() -> dict:
    response = _s3.get_object(Bucket=settings.ai_schema_bucket, Key="schema/current.json")
    return json.loads(response["Body"].read())


def _fetch_schema(key: str) -> dict:
    response = _s3.get_object(Bucket=settings.ai_schema_bucket, Key=key)
    return json.loads(response["Body"].read())


def _load_schema() -> dict:
    pointer = _fetch_current_pointer()
    return _fetch_schema(pointer["key"])


# Built once, lazily, on first use — held in memory for the life of this
# process, same pattern as app/pdf_qa.py's PdfIndex. The schema barely
# changes and a fresh process (redeploy) naturally picks up the latest
# version, so no in-process refresh timer for now.
_schema: dict | None = None


def get_schema() -> dict:
    global _schema
    if _schema is None:
        _schema = _load_schema()
    return _schema
