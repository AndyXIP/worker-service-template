from fastapi.testclient import TestClient

from health import create_health_app


def test_health_returns_200() -> None:
    client = TestClient(create_health_app())

    response = client.get("/utils/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
