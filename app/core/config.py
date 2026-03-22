"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized configuration for the API and external services."""

    app_name: str = "agentic-client-guardian"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Logging level: DEBUG, INFO, WARNING, ERROR.",
    )
    gemini_api_key: str | None = Field(
        default=None,
        alias="GEMINI_API_KEY",
        description="API key used by the future Gemini integration.",
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash",
        alias="GEMINI_MODEL",
        description="Gemini model used for structured context interpretation.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Reuse a single settings object across the application lifecycle."""
    return Settings()
