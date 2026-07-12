"""Stubbed bearer-token authentication.

Demonstrates the `Depends`-based wiring pattern a route uses to require
authentication, without committing to a real verification scheme or
identity provider. `get_current_principal` only checks that *some* bearer
token was supplied - it does not verify a signature, expiry, or issuer.
Replace `_authenticate` with real verification (JWT signature/expiry check,
an introspection call to your identity provider, etc.) before relying on
this for anything that matters.
"""

from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from domain.errors import AppError

# auto_error=False so a missing header raises our own AuthenticationError
# (and gets the standard error envelope) instead of FastAPI's default
# 403 "Not authenticated" response.
_bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticationError(AppError):
    """Raised when a request is missing or carries an invalid bearer token."""

    def __init__(self, message: str = "Missing or invalid authentication token") -> None:
        super().__init__(message)


@dataclass(frozen=True)
class Principal:
    """The authenticated caller. A stub: carries only the raw token."""

    token: str


def _authenticate(token: str) -> Principal:
    # STUB: accepts any non-empty bearer token as valid. Swap this for real
    # verification before this dependency guards anything real.
    return Principal(token=token)


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> Principal:
    if credentials is None or not credentials.credentials:
        raise AuthenticationError
    return _authenticate(credentials.credentials)
