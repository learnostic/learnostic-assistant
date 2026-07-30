import httpx

from app.config import settings

FEATURE_NAME = "learnostic_assistant_chatbot"


def _webhook_url() -> str:
    if settings.app_env == "local":
        return "http://host.docker.internal:8002/webhooks/ai-credit-usage"
    if settings.app_env == "development":
        return "https://api.development.learnostic.com/webhooks/ai-credit-usage"
    if settings.app_env == "testing":
        return "https://api.testing.learnostic.com/webhooks/ai-credit-usage"
    if settings.app_env == "production":
        return "https://api.learnostic.com/webhooks/ai-credit-usage"
    raise ValueError(f"Unknown APP_ENV: {settings.app_env!r}")


def report_ai_credit_usage(tenant_id: int, cost_usd: float) -> None:
    """Best-effort notification to the Laravel backend of AI cost incurred
    for this request. Never raises — a failed usage report shouldn't fail
    the /ask response that already succeeded (or already failed for its own
    reason)."""
    try:
        response = httpx.post(
            _webhook_url(),
            json={
                "tenant_id": tenant_id,
                "tenant_name": str(tenant_id),
                "mpa_app_env": settings.app_env,
                "feature": FEATURE_NAME,
                "cost_usd": round(cost_usd, 6),
            },
            timeout=10.0,
            follow_redirects=True,
        )
        response.raise_for_status()
    except Exception as exc:
        print(f"[ai-credit-usage webhook] failed to report usage: {exc}", flush=True)
