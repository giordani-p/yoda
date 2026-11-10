"""Cancelamento: o cliente desconecta no meio da resposta."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assistant.service import AssistantService
from app.modules.context import ConversationContextProvider
from app.modules.conversations import build_conversation_service
from app.modules.conversations.models import MessageRecord
from app.modules.users.models import UserRecord
from tests.modules.assistant.conftest import FakeLLMProvider

pytestmark = pytest.mark.anyio


async def test_disconnect_discards_partial_reply(
    db_session: AsyncSession, owner: UserRecord, llm: FakeLLMProvider
) -> None:
    conversations = build_conversation_service(db_session)
    service = AssistantService(conversations, ConversationContextProvider(conversations, 20), llm)
    conversation = await conversations.create_conversation(owner.id)
    user_message = await service.accept_user_message(owner.id, conversation.id, "Olá")

    events = service.stream_reply(owner.id, conversation.id, user_message)
    assert (await anext(events)).root.type == "message.user"
    assert (await anext(events)).root.type == "message.delta"
    await events.aclose()

    stored = await db_session.scalars(
        select(MessageRecord).where(MessageRecord.conversation_id == conversation.id)
    )
    assert [m.role for m in stored] == ["user"]
    assert llm.closed
