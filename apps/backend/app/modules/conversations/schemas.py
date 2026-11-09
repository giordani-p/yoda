"""Schemas da API do módulo. Devem espelhar contracts/openapi/openapi.yaml."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from app.shared.schemas import ApiSchema


class Conversation(ApiSchema):
    id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class ConversationPage(ApiSchema):
    items: list[Conversation]
    next_cursor: str | None


class Message(ApiSchema):
    id: UUID
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime


class MessagePage(ApiSchema):
    items: list[Message]
    next_cursor: str | None
