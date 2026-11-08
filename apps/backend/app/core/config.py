"""Configurações da aplicação, lidas de variáveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env da raiz do repositório, relativo a apps/backend (onde os comandos rodam).
    # No Docker o arquivo não existe e as variáveis vêm do docker-compose.
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    app_name: str = "my-project"
    app_env: str = "development"
    app_debug: bool = False

    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "postgresql+psycopg://app:change-me@localhost:5432/app"


@lru_cache
def get_settings() -> Settings:
    return Settings()
