from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Nexiss API", alias="APP_NAME")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/nexiss", alias="DATABASE_URL"
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    celery_task_always_eager: bool = Field(default=False, alias="CELERY_TASK_ALWAYS_EAGER")

    jwt_secret_key: str = Field(default="replace-this-in-production", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_bucket: str = Field(default="nexiss-documents", alias="S3_BUCKET")
    s3_endpoint_url: str | None = Field(default=None, alias="S3_ENDPOINT_URL")
    s3_access_key_id: str | None = Field(default=None, alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str | None = Field(default=None, alias="S3_SECRET_ACCESS_KEY")
    s3_presign_expiry_seconds: int = Field(default=900, alias="S3_PRESIGN_EXPIRY_SECONDS")

    ocr_provider: str = Field(default="mock", alias="OCR_PROVIDER")
    ocr_timeout_seconds: int = Field(default=60, alias="OCR_TIMEOUT_SECONDS")
    textract_poll_interval_seconds: int = Field(default=2, alias="TEXTRACT_POLL_INTERVAL_SECONDS")
    textract_max_wait_seconds: int = Field(default=300, alias="TEXTRACT_MAX_WAIT_SECONDS")
    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    llm_model: str = Field(default="mock-extractor-v1", alias="LLM_MODEL")
    llm_timeout_seconds: int = Field(default=60, alias="LLM_TIMEOUT_SECONDS")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    realtime_progress_channel_prefix: str = Field(
        default="nexiss:progress", alias="REALTIME_PROGRESS_CHANNEL_PREFIX"
    )

    billing_provider: str = Field(default="disabled", alias="BILLING_PROVIDER")
    stripe_secret_key: str | None = Field(default=None, alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str | None = Field(default=None, alias="STRIPE_WEBHOOK_SECRET")

    observability_provider: str = Field(default="disabled", alias="OBSERVABILITY_PROVIDER")
    sentry_dsn: str | None = Field(default=None, alias="SENTRY_DSN")

    @property
    def database_url_sync(self) -> str:
        return self.database_url.replace("+asyncpg", "+pg8000")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
