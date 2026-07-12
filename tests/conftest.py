import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client() -> TestClient:
    """Fresh app per test - gives each test its own in-memory item store."""
    return TestClient(create_app())


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """A bearer token accepted by the stub auth dependency (see core/auth.py).

    The stub accepts any non-empty token, so the value itself is arbitrary.
    """
    return {"Authorization": "Bearer test-token"}
