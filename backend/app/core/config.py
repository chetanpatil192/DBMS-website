"""Configuration management for Commerce Insights using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import List, Literal, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings resolved from environment variables or .env files."""

    model_config = SettingsConfigDict(
        env_file=(
            str(Path(__file__).resolve().parents[2] / ".env"),  # backend/.env
            str(Path(__file__).resolve().parents[3] / ".env"),  # root .env
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General Project Information
    PROJECT_NAME: str = "Commerce Insights API"
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database Configuration (MongoDB)
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "commerce_insights"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_TIMEOUT_MS: int = 5000

    # Optional Database Authentication
    MONGODB_USERNAME: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_AUTH_SOURCE: str = "admin"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, value: Union[str, List[str]]) -> List[str]:
        """Parses CORS origins from comma-separated string, JSON, or list."""
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                import json
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if item]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        elif isinstance(value, list):
            return [str(item).strip() for item in value if item]
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    @property
    def is_production(self) -> bool:
        """Helper to determine if running in production."""
        return self.ENVIRONMENT == "production"

    @property
    def is_testing(self) -> bool:
        """Helper to determine if running in testing."""
        return self.ENVIRONMENT == "testing"


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached singleton instance of application settings."""
    return Settings()
