from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_region: str = "eu-west-1"
    bedrock_region: str = "eu-west-1"

    # Which Laravel backend environment this service's own deployment talks
    # to (local/development/testing/production) — used to pick the webhook
    # URL and reported in the ai-credit-usage payload, same as APP_ENV in the
    # assessment-analyze worker.
    app_env: str = "local"

    db_port: int = 3306

    bedrock_model_id: str = "anthropic.claude-sonnet-5"

    learnostic_readonly_db_username: str
    learnostic_readonly_db_password: str
    learnostic_db_replica_endpoint: str

    # Optional — tracing is skipped if these aren't set (see app/llm.py).
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_base_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()


class DbCredentials:
    def __init__(self, username: str, password: str, endpoint: str):
        self.username = username
        self.password = password
        self.endpoint = endpoint


db_credentials = DbCredentials(
    username=settings.learnostic_readonly_db_username,
    password=settings.learnostic_readonly_db_password,
    endpoint=settings.learnostic_db_replica_endpoint,
)
