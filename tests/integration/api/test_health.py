from fastapi.testclient import TestClient


def test_health_returns_healthy(client: TestClient) -> None:
    response = client.get("/utils/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
