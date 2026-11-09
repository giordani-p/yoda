"""Schemas da API do módulo. Devem espelhar contracts/openapi/openapi.yaml."""

from typing import Annotated, Literal

from pydantic import Field, RootModel, field_validator

from app.core.exceptions import ErrorDetail
from app.modules.conversations import Message
from app.shared.schemas import ApiSchema

MESSAGE_MAX_LENGTH = 10_000


class SendMessageRequest(ApiSchema):
    content: str = Field(min_length=1, max_length=MESSAGE_MAX_LENGTH)

    @field_validator("content")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message content must not be blank.")
        return value


class UserMessageEvent(ApiSchema):
    type: Literal["message.user"]
    message: Message


class MessageDeltaEvent(ApiSchema):
    type: Literal["message.delta"]
    text: str


class MessageCompletedEvent(ApiSchema):
    type: Literal["message.completed"]
    message: Message


class MessageErrorEvent(ApiSchema):
    type: Literal["message.error"]
    error: ErrorDetail


class MessageStreamEvent(
    RootModel[
        Annotated[
            UserMessageEvent | MessageDeltaEvent | MessageCompletedEvent | MessageErrorEvent,
            Field(discriminator="type"),
        ]
    ]
):
    """`data` de cada evento SSE do envio de mensagem, discriminado pelo campo `type`."""
