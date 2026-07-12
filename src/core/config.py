from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "worker-service-template"
    environment: Literal["local", "staging", "production"] = "local"
    log_level: str = "INFO"
    debug: bool = False
    port: int = 8000  # health server bind port; matches Dockerfile's $PORT
    max_delivery_attempts: int = 3  # attempts before a message is dead-lettered


@lru_cache
def get_settings() -> Settings:
    return Settings()
