from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = Field(default="Nexiss API", alias="APP_NAME")
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development", alias="ENVIRONMENT"
    )
    API_V1_PREFIX: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/nexiss", alias="DATABASE_URL"
    )
    REDIS_URL: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    CELERY_TASK_ALWAYS_EAGER: bool = Field(default=False, alias="CELERY_TASK_ALWAYS_EAGER")

    JWT_SECRET_KEY: str = Field(default="replace-this-in-production", alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", alias="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    S3_REGION: str = Field(default="us-east-1", alias="S3_REGION")
    S3_BUCKET: str = Field(default="nexiss-documents", alias="S3_BUCKET")
    S3_ENDPOINT_URL: str | None = Field(default=None, alias="S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID: str | None = Field(default=None, alias="S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: str | None = Field(default=None, alias="S3_SECRET_ACCESS_KEY")
    S3_PRESIGN_EXPIRY_SECONDS: int = Field(default=900, alias="S3_PRESIGN_EXPIRY_SECONDS")

    OCR_PROVIDER: str = Field(default="mock", alias="OCR_PROVIDER")
    OCR_TIMEOUT_SECONDS: int = Field(default=60, alias="OCR_TIMEOUT_SECONDS")
    TEXTRACT_POLL_INTERVAL_SECONDS: int = Field(default=2, alias="TEXTRACT_POLL_INTERVAL_SECONDS")
    TEXTRACT_MAX_WAIT_SECONDS: int = Field(default=300, alias="TEXTRACT_MAX_WAIT_SECONDS")
    LLM_PROVIDER: str = Field(default="mock", alias="LLM_PROVIDER")
    LLM_MODEL: str = Field(default="mock-extractor-v1", alias="LLM_MODEL")
    LLM_TIMEOUT_SECONDS: int = Field(default=60, alias="LLM_TIMEOUT_SECONDS")
    OPENAI_API_KEY: str | None = Field(default=None, alias="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    REALTIME_PROGRESS_CHANNEL_PREFIX: str = Field(
        default="nexiss:progress", alias="REALTIME_PROGRESS_CHANNEL_PREFIX"
    )

    BILLING_PROVIDER: str = Field(default="disabled", alias="BILLING_PROVIDER")
    STRIPE_SECRET_KEY: str | None = Field(default=None, alias="STRIPE_SECRET_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = Field(default=None, alias="STRIPE_WEBHOOK_SECRET")

    OBSERVABILITY_PROVIDER: str = Field(default="disabled", alias="OBSERVABILITY_PROVIDER")
    SENTRY_DSN: str | None = Field(default=None, alias="SENTRY_DSN")

    @property
    def database_url_sync(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "+pg8000")

    # Lowercase properties for legacy code compatibility
    @property
    def app_name(self) -> str: return self.APP_NAME
    @property
    def environment(self) -> str: return self.ENVIRONMENT
    @property
    def api_v1_prefix(self) -> str: return self.API_V1_PREFIX
    @property
    def log_level(self) -> str: return self.LOG_LEVEL
    @property
    def database_url(self) -> str: return self.DATABASE_URL
    @property
    def redis_url(self) -> str: return self.REDIS_URL
    @property
    def celery_task_always_eager(self) -> bool: return self.CELERY_TASK_ALWAYS_EAGER
    @property
    def jwt_secret_key(self) -> str: return self.JWT_SECRET_KEY
    @property
    def jwt_algorithm(self) -> str: return self.JWT_ALGORITHM
    @property
    def jwt_access_token_expire_minutes(self) -> int: return self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    @property
    def s3_region(self) -> str: return self.S3_REGION
    @property
    def s3_bucket(self) -> str: return self.S3_BUCKET
    @property
    def s3_endpoint_url(self) -> str | None: return self.S3_ENDPOINT_URL
    @property
    def s3_access_key_id(self) -> str | None: return self.S3_ACCESS_KEY_ID
    @property
    def s3_secret_access_key(self) -> str | None: return self.S3_SECRET_ACCESS_KEY
    @property
    def s3_presign_expiry_seconds(self) -> int: return self.S3_PRESIGN_EXPIRY_SECONDS
    @property
    def ocr_provider(self) -> str: return self.OCR_PROVIDER
    @property
    def ocr_timeout_seconds(self) -> int: return self.OCR_TIMEOUT_SECONDS
    @property
    def textract_poll_interval_seconds(self) -> int: return self.TEXTRACT_POLL_INTERVAL_SECONDS
    @property
    def textract_max_wait_seconds(self) -> int: return self.TEXTRACT_MAX_WAIT_SECONDS
    @property
    def llm_provider(self) -> str: return self.LLM_PROVIDER
    @property
    def llm_model(self) -> str: return self.LLM_MODEL
    @property
    def llm_timeout_seconds(self) -> int: return self.LLM_TIMEOUT_SECONDS
    @property
    def openai_api_key(self) -> str | None: return self.OPENAI_API_KEY
    @property
    def openai_base_url(self) -> str: return self.OPENAI_BASE_URL
    @property
    def realtime_progress_channel_prefix(self) -> str: return self.REALTIME_PROGRESS_CHANNEL_PREFIX
    @property
    def billing_provider(self) -> str: return self.BILLING_PROVIDER
    @property
    def stripe_secret_key(self) -> str | None: return self.STRIPE_SECRET_KEY
    @property
    def stripe_webhook_secret(self) -> str | None: return self.STRIPE_WEBHOOK_SECRET
    @property
    def observability_provider(self) -> str: return self.OBSERVABILITY_PROVIDER
    @property
    def sentry_dsn(self) -> str | None: return self.SENTRY_DSN

    # AWS Aliases for specific services
    @property
    def AWS_REGION(self) -> str: return self.S3_REGION
    @property
    def AWS_ACCESS_KEY_ID(self) -> str | None: return self.S3_ACCESS_KEY_ID
    @property
    def AWS_SECRET_ACCESS_KEY(self) -> str | None: return self.S3_SECRET_ACCESS_KEY
    @property
    def AWS_S3_BUCKET(self) -> str: return self.S3_BUCKET


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
