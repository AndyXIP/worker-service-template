from fastapi.testclient import TestClient

from main import create_app
from repositories.item import get_item_repository


class _BrokenRepository:
    def list(self) -> list:
        raise RuntimeError("boom")


def test_post_invalid_body_returns_422_envelope(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post("/items", json={"name": "Widget", "price": -1}, headers=auth_headers)

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["type"] == "validation_error"
    assert body["error"]["details"]


def test_unhandled_exception_returns_generic_500_envelope_without_leaking_internals() -> None:
    app = create_app()
    app.dependency_overrides[get_item_repository] = lambda: _BrokenRepository()
    # ServerErrorMiddleware sends the 500 response but also re-raises the
    # original exception (so it still surfaces in server logs); tell the
    # TestClient not to propagate that re-raise so we can assert on the
    # response like a real client would see.
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/items")

    assert response.status_code == 500
    body = response.json()
    assert body["error"]["type"] == "internal_error"
    assert "boom" not in response.text
