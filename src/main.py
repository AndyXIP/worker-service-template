from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import health, items
from core.config import get_settings
from core.errors import register_exception_handlers
from core.logging import RequestLoggingMiddleware, configure_logging
from repositories.item import InMemoryItemRepository

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info("starting_up", app_name=settings.app_name, environment=settings.environment)
    yield
    # No real resources to release here (no DB pool, no HTTP clients) - this
    # is where that teardown would go once the service acquires any.
    logger.info("shutting_down")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.item_repository = InMemoryItemRepository()

    register_exception_handlers(app)
    app.add_middleware(RequestLoggingMiddleware)

    if settings.cors_origins:
        # allow_credentials=True means the browser will send cookies/auth headers
        # on cross-origin requests from these origins. Keep allow_methods and
        # allow_headers scoped to what this service actually needs - copying
        # "*" wildcards here alongside allow_credentials is a common footgun
        # once real auth is wired in. Widen only if a specific method/header
        # is genuinely required.
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PATCH", "DELETE"],
            allow_headers=["Authorization", "Content-Type"],
        )

    app.include_router(health.router)
    app.include_router(items.router)

    return app


app = create_app()
