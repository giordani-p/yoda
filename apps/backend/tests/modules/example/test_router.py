from fastapi.testclient import TestClient

URL = "/api/v1/examples"


def test_create_and_get_example(client: TestClient) -> None:
    created = client.post(URL, json={"name": "First", "description": "Desc"})

    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "First"
    assert body["description"] == "Desc"
    assert "createdAt" in body

    fetched = client.get(f"{URL}/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_list_examples(client: TestClient) -> None:
    client.post(URL, json={"name": "A"})
    client.post(URL, json={"name": "B"})

    response = client.get(URL)

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == ["A", "B"]


def test_get_missing_example_returns_error_envelope(client: TestClient) -> None:
    response = client.get(f"{URL}/999")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_invalid_payload_returns_error_envelope(client: TestClient) -> None:
    response = client.post(URL, json={"name": ""})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"]
