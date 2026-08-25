import json
import math

import boto3

from app.config import settings

_bedrock_runtime = boto3.client("bedrock-runtime", region_name=settings.bedrock_region)

TITAN_EMBED_MODEL_ID = "amazon.titan-embed-text-v2:0"


def embed_text(text: str) -> list[float]:
    response = _bedrock_runtime.invoke_model(
        modelId=TITAN_EMBED_MODEL_ID,
        body=json.dumps({"inputText": text}),
    )
    return json.loads(response["body"].read())["embedding"]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
