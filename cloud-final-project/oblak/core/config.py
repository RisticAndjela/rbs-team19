from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Oblak"
    database_url: str = "sqlite:///./oblak.db"
    storage_root: Path = Path("./.storage/functions")
    max_archive_bytes: int = 2_000_000
    max_requirements_lines: int = 40
    execution_timeout_seconds: int = 5
    max_stdout_bytes: int = 20_000
    enable_clamav: bool = False
    clamav_command: str = "clamscan"
    enable_llm_analysis: bool = True
    llm_provider: str = "mock"

    model_config = SettingsConfigDict(env_prefix="OBLAK_", env_file=".env")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    return settings
