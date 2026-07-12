from uuid import uuid4

from fastapi.testclient import TestClient


def test_full_item_lifecycle(client: TestClient, auth_headers: dict[str, str]) -> None:
    create_response = client.post(
        "/items",
        json={"name": "Widget", "description": "A widget", "price": 9.99},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Widget"
    assert created["price"] == 9.99
    item_id = created["id"]

    list_response = client.get("/items")
    assert list_response.status_code == 200
    assert any(item["id"] == item_id for item in list_response.json())

    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == item_id

    patch_response = client.patch(f"/items/{item_id}", json={"price": 14.99}, headers=auth_headers)
    assert patch_response.status_code == 200
    assert patch_response.json()["price"] == 14.99
    assert patch_response.json()["name"] == "Widget"

    delete_response = client.delete(f"/items/{item_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    after_delete_response = client.get(f"/items/{item_id}")
    assert after_delete_response.status_code == 404


def test_get_missing_item_returns_404_envelope(client: TestClient) -> None:
    response = client.get(f"/items/{uuid4()}")

    assert response.status_code == 404
    body = response.json()
    assert body["error"]["type"] == "not_found"


def test_create_item_without_token_returns_401_envelope(client: TestClient) -> None:
    response = client.post("/items", json={"name": "Widget", "price": 9.99})

    assert response.status_code == 401
    body = response.json()
    assert body["error"]["type"] == "authentication_error"


def test_create_item_with_token_succeeds(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post("/items", json={"name": "Widget", "price": 9.99}, headers=auth_headers)

    assert response.status_code == 201
