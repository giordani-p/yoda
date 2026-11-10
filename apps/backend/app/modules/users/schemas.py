"""Schemas da API do módulo. Devem espelhar contracts/openapi/openapi.yaml."""

from uuid import UUID

from pydantic import Field

from app.shared.schemas import ApiSchema


class LoginRequest(ApiSchema):
    email: str = Field(min_length=1, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


class User(ApiSchema):
    id: UUID
    email: str
    name: str
