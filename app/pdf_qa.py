import io

import boto3
from pypdf import PdfReader

from app.config import settings
from app.embeddings import cosine_similarity, embed_text

_s3 = boto3.client("s3", region_name=settings.aws_region)


def _fetch_pdf_bytes() -> bytes:
    response = _s3.get_object(Bucket=settings.pdf_s3_bucket, Key=settings.pdf_s3_key)
    return response["Body"].read()


def _extract_pages(pdf_bytes: bytes) -> list[str]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return [page.extract_text() or "" for page in reader.pages]


class PdfIndex:
    def __init__(self, pages: list[str], vectors: list[list[float]]):
        self.pages = pages
        self.vectors = vectors

    def retrieve(self, question: str, k: int = 5) -> list[str]:
        question_vector = embed_text(question)
        scored = [(i, cosine_similarity(question_vector, v)) for i, v in enumerate(self.vectors)]
        top_indices = sorted(i for i, _ in sorted(scored, key=lambda item: item[1], reverse=True)[:k])
        return [self.pages[i] for i in top_indices]


def _build_index() -> PdfIndex:
    # Pages that are pure images (e.g. a cover page) extract to empty text —
    # skip them rather than embedding an empty string, since they'd never be
    # a meaningful match anyway.
    pages = [text for text in _extract_pages(_fetch_pdf_bytes()) if text.strip()]
    vectors = [embed_text(text) for text in pages]
    return PdfIndex(pages, vectors)


# Built once, lazily, on first use — held in memory for the life of this
# process. Rebuilding is cheap (fetch from S3 + ~86 embedding calls), so no
# need to persist it anywhere for a single document at this scale.
_index: PdfIndex | None = None


def get_index() -> PdfIndex:
    global _index
    if _index is None:
        _index = _build_index()
    return _index
