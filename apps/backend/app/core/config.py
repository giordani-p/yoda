"""Configurações da aplicação, lidas de variáveis de ambiente."""

from functools import lru_cache
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Chave usada só em desenvolvimento local. Fora de `development`, AUTH_SECRET_KEY é obrigatória.
DEV_AUTH_SECRET_KEY = "dev-only-insecure-secret-key-change-me"
MIN_AUTH_SECRET_KEY_LENGTH = 32


class Settings(BaseSettings):
    # .env da raiz do repositório, relativo a apps/backend (onde os comandos rodam).
    # No Docker o arquivo não existe e as variáveis vêm do docker-compose.
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    app_name: str = "yoda"
    app_env: str = "development"
    app_debug: bool = False

    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "postgresql+psycopg://app:change-me@localhost:5432/app"

    auth_secret_key: str = DEV_AUTH_SECRET_KEY
    auth_token_ttl_hours: int = 168
    # True quando a aplicação for servida por HTTPS.
    auth_cookie_secure: bool = False

    @model_validator(mode="after")
    def _check_auth_secret_key(self) -> Self:
        if len(self.auth_secret_key) < MIN_AUTH_SECRET_KEY_LENGTH:
            raise ValueError(
                f"AUTH_SECRET_KEY must have at least {MIN_AUTH_SECRET_KEY_LENGTH} characters."
            )
        if self.app_env != "development" and self.auth_secret_key == DEV_AUTH_SECRET_KEY:
            raise ValueError("AUTH_SECRET_KEY must be set outside the development environment.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
