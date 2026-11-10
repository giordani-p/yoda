from uuid import UUID, uuid4

import pytest
from httpx2 import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.modules.conversations.models import ConversationRecord, MessageRecord
from app.modules.users.models import UserRecord
from tests.helpers import login_as, parse_sse
from tests.modules.assistant.conftest import FakeLLMProvider
from tests.modules.conversations.conftest import add_messages

pytestmark = pytest.mark.anyio


async def _conversation(client: AsyncClient) -> str:
    return (await client.post("/api/v1/conversations")).json()["id"]


def _stream_url(conversation_id: str) -> str:
    return f"/api/v1/conversations/{conversation_id}/messages/stream"


async def _send(client: AsyncClient, conversation_id: str, content: str) -> list[dict]:
    response = await client.post(_stream_url(conversation_id), json={"content": content})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    return parse_sse(response.text)


async def _messages(db_session: AsyncSession, conversation_id: str) -> list[MessageRecord]:
    return list(
        await db_session.scalars(
            select(MessageRecord)
            .where(MessageRecord.conversation_id == UUID(conversation_id))
            .order_by(MessageRecord.created_at)
        )
    )


async def test_streams_reply_and_persists_both_messages(
    owner_client: AsyncClient, db_session: AsyncSession
) -> None:
    conversation_id = await _conversation(owner_client)

    events = await _send(owner_client, conversation_id, "Olá, Yoda")

    assert [e["type"] for e in events] == [
        "message.user",
        "message.delta",
        "message.delta",
        "message.completed",
    ]
    assert events[0]["message"]["role"] == "user"
    assert events[0]["message"]["content"] == "Olá, Yoda"
    assert [e["text"] for e in events[1:3]] == ["Olá", "!"]
    assert events[3]["message"]["role"] == "assistant"
    assert events[3]["message"]["content"] == "Olá!"

    stored = await _messages(db_session, conversation_id)
    assert [(m.role, m.content) for m in stored] == [("user", "Olá, Yoda"), ("assistant", "Olá!")]
    assert (stored[1].model, stored[1].input_tokens, stored[1].output_tokens) == (
        "fake-model",
        10,
        5,
    )
    history = (await owner_client.get(f"/api/v1/conversations/{conversation_id}/messages")).json()
    assert [m["id"] for m in history["items"]] == [str(m.id) for m in stored]


async def test_first_message_sets_title_and_updates_conversation(
    owner_client: AsyncClient,
) -> None:
    conversation_id = await _conversation(owner_client)
    created = (await owner_client.get(f"/api/v1/conversations/{conversation_id}")).json()

    await _send(owner_client, conversation_id, "Planejar  viagem\npara Lisboa")
    await _send(owner_client, conversation_id, "Outra pergunta")

    updated = (await owner_client.get(f"/api/v1/conversations/{conversation_id}")).json()
    assert updated["title"] == "Planejar viagem para Lisboa"
    assert updated["updatedAt"] > created["updatedAt"]


async def test_context_has_instructions_and_recent_messages(
    owner_client: AsyncClient,
    db_session: AsyncSession,
    llm: FakeLLMProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(get_settings(), "context_recent_messages", 3)
    conversation_id = await _conversation(owner_client)
    await add_messages(db_session, UUID(conversation_id), 5)

    await _send(owner_client, conversation_id, "nova pergunta")

    context = llm.contexts[-1]
    assert context.instructions.startswith("Você é o Yoda")
    assert context.instructions_version == "v1"
    assert [(m.role, m.content) for m in context.messages] == [
        ("assistant", "mensagem 3"),
        ("user", "mensagem 4"),
        ("user", "nova pergunta"),
    ]


async def test_provider_failure_emits_error_and_keeps_only_user_message(
    owner_client: AsyncClient, db_session: AsyncSession, llm: FakeLLMProvider
) -> None:
    llm.fail_at = 1
    conversation_id = await _conversation(owner_client)

    events = await _send(owner_client, conversation_id, "Olá")

    assert [e["type"] for e in events] == ["message.user", "message.delta", "message.error"]
    assert events[-1]["error"]["code"] == "LLM_PROVIDER_ERROR"
    stored = await _messages(db_session, conversation_id)
    assert [m.role for m in stored] == ["user"]
    assert llm.closed


async def test_other_users_conversation_returns_404_before_streaming(
    client: AsyncClient, owner: UserRecord, other_user: UserRecord, db_session: AsyncSession
) -> None:
    login_as(client, owner)
    conversation_id = await _conversation(client)

    login_as(client, other_user)
    response = await client.post(_stream_url(conversation_id), json={"content": "Olá"})

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert await _messages(db_session, conversation_id) == []


async def test_deleted_conversation_returns_404(owner_client: AsyncClient) -> None:
    conversation_id = await _conversation(owner_client)
    await owner_client.delete(f"/api/v1/conversations/{conversation_id}")

    response = await owner_client.post(_stream_url(conversation_id), json={"content": "Olá"})

    assert response.status_code == 404


@pytest.mark.parametrize(
    "content", ["", "   \n ", "x" * 10_001], ids=["empty", "blank", "too-long"]
)
async def test_invalid_content_returns_422(owner_client: AsyncClient, content: str) -> None:
    conversation_id = await _conversation(owner_client)

    response = await owner_client.post(_stream_url(conversation_id), json={"content": content})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_requires_authentication(client: AsyncClient) -> None:
    response = await client.post(_stream_url(str(uuid4())), json={"content": "Olá"})

    assert response.status_code == 401


async def test_conversation_title_is_truncated(
    owner_client: AsyncClient, db_session: AsyncSession
) -> None:
    conversation_id = await _conversation(owner_client)

    await _send(owner_client, conversation_id, "a" * 80)

    record = await db_session.get(ConversationRecord, UUID(conversation_id))
    assert record is not None
    assert record.title == "a" * 59 + "…"
