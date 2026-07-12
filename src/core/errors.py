from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.auth import AuthenticationError
from domain.errors import NotFoundError

logger = structlog.get_logger(__name__)


def _envelope(error_type: str, message: str, details: Any = None) -> dict[str, Any]:
    return {"error": {"type": error_type, "message": message, "details": details}}


async def _handle_validation_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=_envelope("validation_error", "Request validation failed", exc.errors()),
    )


async def _handle_not_found(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, NotFoundError)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=_envelope("not_found", exc.message),
    )


async def _handle_authentication_error(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AuthenticationError)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=_envelope("authentication_error", exc.message),
        headers={"WWW-Authenticate": "Bearer"},
    )


async def _handle_unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_envelope("internal_error", "An unexpected error occurred"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(NotFoundError, _handle_not_found)
    app.add_exception_handler(AuthenticationError, _handle_authentication_error)
    app.add_exception_handler(Exception, _handle_unhandled_exception)
