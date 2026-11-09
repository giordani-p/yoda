from uuid import UUID, uuid4

import pytest
from httpx2 import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.models import ConversationRecord
from app.modules.users.models import UserRecord
from tests.modules.conversations.conftest import add_messages, login_as

pytestmark = pytest.mark.anyio

URL = "/api/v1/conversations"


async def _create(client: AsyncClient) -> dict:
    response = await client.post(URL)
    assert response.status_code == 201
    return response.json()


async def test_create_and_get_conversation(owner_client: AsyncClient) -> None:
    created = await _create(owner_client)

    assert created["title"] is None
    assert set(created) == {"id", "title", "createdAt", "updatedAt"}

    fetched = await owner_client.get(f"{URL}/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == created


async def test_list_conversations_most_recent_first_with_cursor(
    owner_client: AsyncClient,
) -> None:
    ids = [(await _create(owner_client))["id"] for _ in range(5)]

    first = (await owner_client.get(URL, params={"limit": 2})).json()
    second = (
        await owner_client.get(URL, params={"limit": 2, "cursor": first["nextCursor"]})
    ).json()
    third = (
        await owner_client.get(URL, params={"limit": 2, "cursor": second["nextCursor"]})
    ).json()

    listed = [c["id"] for page in (first, second, third) for c in page["items"]]
    assert listed == list(reversed(ids))
    assert third["nextCursor"] is None


async def test_list_conversations_without_more_pages_has_null_cursor(
    owner_client: AsyncClient,
) -> None:
    await _create(owner_client)

    page = (await owner_client.get(URL)).json()

    assert len(page["items"]) == 1
    assert page["nextCursor"] is None


async def test_conversations_are_isolated_by_user(
    client: AsyncClient, owner: UserRecord, other_user: UserRecord
) -> None:
    login_as(client, owner)
    conversation = await _create(client)

    login_as(client, other_user)
    listed = (await client.get(URL)).json()["items"]
    fetched = await client.get(f"{URL}/{conversation['id']}")
    messages = await client.get(f"{URL}/{conversation['id']}/messages")
    deleted = await client.delete(f"{URL}/{conversation['id']}")

    assert listed == []
    assert fetched.status_code == 404
    assert fetched.json()["error"]["code"] == "NOT_FOUND"
    assert messages.status_code == 404
    assert deleted.status_code == 404


async def test_delete_is_soft_and_hides_conversation(
    owner_client: AsyncClient, db_session: AsyncSession
) -> None:
    conversation = await _create(owner_client)

    response = await owner_client.delete(f"{URL}/{conversation['id']}")

    assert response.status_code == 204
    assert (await owner_client.get(URL)).json()["items"] == []
    assert (await owner_client.get(f"{URL}/{conversation['id']}")).status_code == 404
    assert (await owner_client.get(f"{URL}/{conversation['id']}/messages")).status_code == 404
    assert (await owner_client.delete(f"{URL}/{conversation['id']}")).status_code == 404
    record = await db_session.scalar(
        select(ConversationRecord).where(ConversationRecord.id == UUID(conversation["id"]))
    )
    assert record is not None
    assert record.deleted_at is not None


async def test_list_messages_newest_page_in_chronological_order(
    owner_client: AsyncClient, db_session: AsyncSession
) -> None:
    conversation = await _create(owner_client)
    await add_messages(db_session, UUID(conversation["id"]), 5)
    url = f"{URL}/{conversation['id']}/messages"

    latest = (await owner_client.get(url, params={"limit": 2})).json()
    older = (
        await owner_client.get(url, params={"limit": 2, "cursor": latest["nextCursor"]})
    ).json()
    oldest = (
        await owner_client.get(url, params={"limit": 2, "cursor": older["nextCursor"]})
    ).json()

    assert [m["content"] for m in latest["items"]] == ["mensagem 3", "mensagem 4"]
    assert [m["content"] for m in older["items"]] == ["mensagem 1", "mensagem 2"]
    assert [m["content"] for m in oldest["items"]] == ["mensagem 0"]
    assert oldest["nextCursor"] is None
    assert [m["role"] for m in latest["items"]] == ["assistant", "user"]
    assert set(latest["items"][0]) == {"id", "role", "content", "createdAt"}


async def test_list_messages_of_empty_conversation(owner_client: AsyncClient) -> None:
    conversation = await _create(owner_client)

    page = (await owner_client.get(f"{URL}/{conversation['id']}/messages")).json()

    assert page == {"items": [], "nextCursor": None}


@pytest.mark.parametrize(
    "params",
    [{"cursor": "not-a-cursor"}, {"limit": 0}, {"limit": 101}],
    ids=["invalid-cursor", "limit-too-small", "limit-too-large"],
)
async def test_invalid_pagination_returns_422(owner_client: AsyncClient, params: dict) -> None:
    response = await owner_client.get(URL, params=params)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_invalid_conversation_id_returns_422(owner_client: AsyncClient) -> None:
    response = await owner_client.get(f"{URL}/not-a-uuid")

    assert response.status_code == 422


async def test_unknown_conversation_returns_404(owner_client: AsyncClient) -> None:
    response = await owner_client.get(f"{URL}/{uuid4()}")

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("POST", ""),
        ("GET", ""),
        ("GET", "/{id}"),
        ("DELETE", "/{id}"),
        ("GET", "/{id}/messages"),
    ],
)
async def test_routes_require_authentication(client: AsyncClient, method: str, path: str) -> None:
    response = await client.request(method, URL + path.format(id=uuid4()))

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"
