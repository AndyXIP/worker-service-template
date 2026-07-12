from typing import Any
from uuid import uuid4

import pytest

from consumers.dispatch import Handler, process_one
from core.queue import InMemoryMessageQueue, Message
from main import build_handlers
from repositories.item import InMemoryItemRepository
from services.item import ItemService


@pytest.fixture
def handlers(item_repository: InMemoryItemRepository) -> dict[str, Handler]:
    return build_handlers(ItemService(item_repository))


async def test_item_create_message_is_processed_and_persisted(
    queue: InMemoryMessageQueue,
    dead_letter_queue: InMemoryMessageQueue,
    handlers: dict[str, Handler],
    item_repository: InMemoryItemRepository,
) -> None:
    await queue.publish(Message(type="item.create", payload={"name": "Widget", "price": 9.99}))

    await process_one(queue, dead_letter_queue, handlers, max_delivery_attempts=3)

    [item] = item_repository._items.values()
    assert item.name == "Widget"
    assert item.price == 9.99


async def test_item_delete_for_unknown_id_is_dead_lettered_without_retry(
    queue: InMemoryMessageQueue,
    dead_letter_queue: InMemoryMessageQueue,
    handlers: dict[str, Handler],
) -> None:
    missing_id = uuid4()
    await queue.publish(Message(type="item.delete", payload={"item_id": str(missing_id)}))

    await process_one(queue, dead_letter_queue, handlers, max_delivery_attempts=3)

    dead_lettered = await dead_letter_queue.get()
    assert dead_lettered.type == "item.delete"
    assert dead_lettered.attempt == 1


async def test_unknown_message_type_is_dead_lettered_without_retry(
    queue: InMemoryMessageQueue,
    dead_letter_queue: InMemoryMessageQueue,
    handlers: dict[str, Handler],
) -> None:
    await queue.publish(Message(type="item.unknown", payload={}))

    await process_one(queue, dead_letter_queue, handlers, max_delivery_attempts=3)

    dead_lettered = await dead_letter_queue.get()
    assert dead_lettered.type == "item.unknown"
    assert dead_lettered.attempt == 1


async def test_transient_failure_is_retried_then_dead_lettered(
    queue: InMemoryMessageQueue, dead_letter_queue: InMemoryMessageQueue
) -> None:
    async def flaky_handler(payload: dict[str, Any]) -> None:
        raise RuntimeError("boom")

    handlers: dict[str, Handler] = {"flaky": flaky_handler}
    await queue.publish(Message(type="flaky", payload={}))

    await process_one(queue, dead_letter_queue, handlers, max_delivery_attempts=2)
    retried = await queue.get()
    assert retried.attempt == 2

    await queue.publish(retried)
    await process_one(queue, dead_letter_queue, handlers, max_delivery_attempts=2)
    dead_lettered = await dead_letter_queue.get()
    assert dead_lettered.attempt == 2
