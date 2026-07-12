from uuid import UUID

from fastapi.testclient import TestClient


def test_response_includes_request_id_header(client: TestClient) -> None:
    response = client.get("/items")

    assert response.status_code == 200
    request_id = response.headers["x-request-id"]
    assert UUID(request_id)


def test_each_request_gets_a_distinct_request_id(client: TestClient) -> None:
    first = client.get("/items").headers["x-request-id"]
    second = client.get("/items").headers["x-request-id"]

    assert first != second
