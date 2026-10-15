from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "url-shortener-prototype"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    public_base_url: str = "http://localhost:8000"
    database_url: str = "sqlite+aiosqlite:///./shortener.db"
    redis_url: str = "redis://localhost:6379/0"
    admin_token: str = "dev-admin-token"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
