import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    """Konfiguracja aplikacji oparta na Pydantic v2."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App Info
    APP_NAME: str = "RegisLite GodMode"
    VERSION: str = "5.1.2"
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    WORKSPACE_DIR: Path = BASE_DIR / "workspace"

    # Security & AI
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    AI_MODEL: str = "gpt-4o-mini"

    # Limits
    MAX_FILE_SIZE_MB: int = 50
    MAX_ITERATIONS: int = 5

@lru_cache
def get_settings() -> Settings:
    return Settings()
