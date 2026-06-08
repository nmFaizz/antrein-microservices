from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str

    # Service identity (used by tracing/logging/observability).
    PROJECT_NAME: str = "Queue Service"
    SERVICE_VERSION: str = "1.0.0"

    # Integration with menu-preorder-service (queue -> preorder callback).
    # All optional: when PREORDER_SERVICE_URL is unset the callback is a no-op.
    PREORDER_SERVICE_URL: str | None = None
    SECRET_KEY: str | None = None  # shared HS256 secret for the admin JWT
    SERVICE_ACCOUNT_ID: str = "00000000-0000-0000-0000-000000000000"


settings = Settings()
