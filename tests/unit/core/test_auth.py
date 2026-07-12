import pytest
from fastapi.security import HTTPAuthorizationCredentials

from core.auth import AuthenticationError, get_current_principal


def test_get_current_principal_accepts_any_nonempty_token() -> None:
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")

    principal = get_current_principal(credentials)

    assert principal.token == "test-token"


def test_get_current_principal_missing_credentials_raises() -> None:
    with pytest.raises(AuthenticationError):
        get_current_principal(None)
