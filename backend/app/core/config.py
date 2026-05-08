"""
Application configuration loaded from environment variables.
Uses pydantic-settings for type-safe config with .env file support.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env from project root (three levels up from this file:
# config.py → core/ → app/ → backend/ → project root)
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    """Global application settings, auto-loaded from .env file."""

    # ── Database ──
    DATABASE_URL: str

    # ── App ──
    APP_ENV: str = "development"

    # ── CORS ──
    CORS_ORIGINS: str = "http://localhost:5173"

    # ── OpenRouter ──
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "google/gemini-2.0-flash-001"

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached singleton for app settings."""
    return Settings()
