import asyncio

import structlog
import uvicorn

from consumers.dispatch import Handler, run_forever
from consumers.item import make_item_create_handler, make_item_delete_handler
from core.config import get_settings
from core.logging import configure_logging
from core.queue import InMemoryMessageQueue, Message, MessageQueue
from health import create_health_app
from repositories.item import InMemoryItemRepository
from services.item import ItemService

logger = structlog.get_logger(__name__)


def build_handlers(item_service: ItemService) -> dict[str, Handler]:
    """The handler registry - maps a message's `type` to the handler that
    processes it, the dispatch-loop equivalent of `app.include_router`."""
    return {
        "item.create": make_item_create_handler(item_service),
        "item.delete": make_item_delete_handler(item_service),
    }


async def _seed_sample_messages(queue: MessageQueue) -> None:
    """Demo-only: stands in for whatever publishes to the real broker (an
    upstream producer service, a webhook, ...) so `mise run dev` has
    something to process out of the box. Nothing outside this process can
    publish into an in-memory queue, so this goes away once a real
    `MessageQueue` implementation replaces `InMemoryMessageQueue`.
    """
    await queue.publish(
        Message(
            type="item.create",
            payload={"name": "Widget", "description": "A widget", "price": 9.99},
        )
    )
    # Demonstrates the dead-letter path: this id was never created.
    await queue.publish(
        Message(type="item.delete", payload={"item_id": "00000000-0000-0000-0000-000000000000"})
    )


async def main() -> None:  # pragma: no cover - exercised by running the process, not by tests
    settings = get_settings()
    configure_logging(settings)
    logger.info("starting_up", app_name=settings.app_name, environment=settings.environment)

    queue = InMemoryMessageQueue()
    dead_letter_queue = InMemoryMessageQueue()
    item_repository = InMemoryItemRepository()
    item_service = ItemService(item_repository)
    handlers = build_handlers(item_service)

    if settings.environment == "local":
        await _seed_sample_messages(queue)

    health_server = uvicorn.Server(
        uvicorn.Config(
            create_health_app(),
            host="0.0.0.0",
            port=settings.port,
            log_config=None,
            access_log=False,
        )
    )

    async with asyncio.TaskGroup() as tg:
        tg.create_task(health_server.serve())
        tg.create_task(
            run_forever(queue, dead_letter_queue, handlers, settings.max_delivery_attempts)
        )


if __name__ == "__main__":  # pragma: no cover - entrypoint, not exercised by tests
    asyncio.run(main())
