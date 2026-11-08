"""Schemas da API do módulo. Devem espelhar contracts/openapi/openapi.yaml."""

from datetime import datetime

from pydantic import Field

from app.shared.schemas import ApiSchema


class ExampleCreate(ApiSchema):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class Example(ApiSchema):
    id: int
    name: str
    description: str | None
    created_at: datetime


class ExampleList(ApiSchema):
    items: list[Example]
