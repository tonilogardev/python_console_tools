from __future__ import annotations

import pathlib
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings(env_file: Optional[pathlib.Path] = None) -> Settings:
    if env_file:
        return Settings(_env_file=env_file)
    return Settings()
