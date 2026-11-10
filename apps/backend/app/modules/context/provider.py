"""Montagem do contexto enviado ao modelo.

No P1 o contexto tem as instruções do sistema e as mensagens recentes da conversa. A interface
`ContextProvider` é o ponto de extensão para resumo (P2) e memória (P3).
"""

from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Literal, Protocol
from uuid import UUID

from app.modules.conversations import ConversationService

# Versão das instruções do sistema em uso (arquivo em instructions/<versão>.md).
INSTRUCTIONS_VERSION = "v1"
_INSTRUCTIONS_DIR = Path(__file__).parent / "instructions"


@dataclass(frozen=True)
class ContextMessage:
    role: Literal["user", "assistant"]
    content: str


@dataclass(frozen=True)
class ModelContext:
    instructions: str
    instructions_version: str
    messages: list[ContextMessage]


class ContextProvider(Protocol):
    async def build_context(self, conversation_id: UUID, user_id: UUID) -> ModelContext: ...


@cache
def load_instructions(version: str = INSTRUCTIONS_VERSION) -> str:
    return (_INSTRUCTIONS_DIR / f"{version}.md").read_text(encoding="utf-8").strip()


class ConversationContextProvider:
    """Instruções do sistema + as últimas `recent_limit` mensagens da conversa."""

    def __init__(self, conversations: ConversationService, recent_limit: int) -> None:
        self.conversations = conversations
        self.recent_limit = recent_limit

    async def build_context(self, conversation_id: UUID, user_id: UUID) -> ModelContext:
        recent = await self.conversations.recent_messages(
            user_id, conversation_id, self.recent_limit
        )
        return ModelContext(
            instructions=load_instructions(),
            instructions_version=INSTRUCTIONS_VERSION,
            messages=[ContextMessage(role=m.role, content=m.content) for m in recent],
        )
