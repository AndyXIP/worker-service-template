from core.queue import InMemoryMessageQueue
from main import _seed_sample_messages, build_handlers
from repositories.item import InMemoryItemRepository
from services.item import ItemService


def test_build_handlers_registers_known_message_types() -> None:
    handlers = build_handlers(ItemService(InMemoryItemRepository()))

    assert set(handlers) == {"item.create", "item.delete"}


async def test_seed_sample_messages_publishes_a_create_and_a_delete() -> None:
    queue = InMemoryMessageQueue()

    await _seed_sample_messages(queue)

    first = await queue.get()
    second = await queue.get()
    assert {first.type, second.type} == {"item.create", "item.delete"}
