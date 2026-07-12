from core.queue import InMemoryMessageQueue, Message


def test_message_attempt_defaults_to_one() -> None:
    message = Message(type="item.create", payload={})

    assert message.attempt == 1


async def test_publish_then_get_returns_same_message() -> None:
    queue = InMemoryMessageQueue()
    message = Message(type="item.create", payload={"name": "Widget"})

    await queue.publish(message)

    assert await queue.get() == message


async def test_messages_are_returned_in_fifo_order() -> None:
    queue = InMemoryMessageQueue()
    first = Message(type="item.create", payload={})
    second = Message(type="item.delete", payload={})

    await queue.publish(first)
    await queue.publish(second)

    assert await queue.get() == first
    assert await queue.get() == second
