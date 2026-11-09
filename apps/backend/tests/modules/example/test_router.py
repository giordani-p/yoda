import pytest
from httpx2 import AsyncClient

pytestmark = pytest.mark.anyio

URL = "/api/v1/examples"


async def test_create_and_get_example(client: AsyncClient) -> None:
    created = await client.post(URL, json={"name": "First", "description": "Desc"})

    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "First"
    assert body["description"] == "Desc"
    assert "createdAt" in body

    fetched = await client.get(f"{URL}/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


async def test_list_examples(client: AsyncClient) -> None:
    await client.post(URL, json={"name": "A"})
    await client.post(URL, json={"name": "B"})

    response = await client.get(URL)

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == ["A", "B"]


async def test_get_missing_example_returns_error_envelope(client: AsyncClient) -> None:
    response = await client.get(f"{URL}/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


async def test_invalid_payload_returns_error_envelope(client: AsyncClient) -> None:
    response = await client.post(URL, json={"name": ""})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"]
