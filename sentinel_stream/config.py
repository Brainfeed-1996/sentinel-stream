from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration.

    Values can be provided via environment variables using the prefix
    ``SENTINEL_STREAM__`` (double-underscore nesting style).
    """

    model_config = SettingsConfigDict(
        env_prefix="SENTINEL_STREAM__",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # General
    environment: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Paths
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    sqlite_path: Path = Field(default_factory=lambda: Path("data") / "sentinel_stream.db")
    audit_log_path: Path = Field(default_factory=lambda: Path("data") / "audit.jsonl")

    # Rules
    rules_path: Path = Field(default_factory=lambda: Path("rules") / "default.yml")

    # Collector
    host: str | None = None
    max_files: int = 2000

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8080


def load_settings() -> Settings:
    return Settings()
