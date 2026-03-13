from __future__ import annotations

import pathlib
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    log_level: str = "INFO"
    user: str | None = None
    copernicus_endpoint: str | None = None
    data_dir: str = "data"
    auth0_domain: str | None = None
    auth0_client_id: str | None = None
    auth0_audience: str | None = None
    auth0_db_connection: str = "Username-Password-Authentication"
    auth_poll_timeout: int = 600  # seconds

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_settings(env_file: Optional[pathlib.Path] = None) -> Settings:
    if env_file:
        return Settings(_env_file=env_file)
    return Settings()
