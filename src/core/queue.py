import asyncio
from typing import Any, Protocol
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A unit of work moving through the queue.

    `attempt` starts at 1 and is incremented by the dispatch loop on retry -
    handlers never touch it directly.
    """

    id: UUID = Field(default_factory=uuid4)
    type: str
    payload: dict[str, Any]
    attempt: int = 1


class MessageQueue(Protocol):  # pragma: no cover
    """Queue abstraction the dispatch loop and handlers depend on.

    Swap `InMemoryMessageQueue` for a real broker client (SQS, Redis Streams,
    RabbitMQ, ...) satisfying this Protocol - nothing above this layer
    changes, exactly like `ItemRepository`.
    """

    async def publish(self, message: Message) -> None: ...

    async def get(self) -> Message: ...


class InMemoryMessageQueue:
    """`asyncio.Queue`-backed reference implementation.

    Process-local and non-persistent: it only holds messages published from
    within this same process, and everything is lost on restart. Fine for
    examples/tests/local dev; swap in a real broker (see `MessageQueue`)
    before relying on this for anything that needs to survive a restart or
    be published to from another process.
    """

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Message] = asyncio.Queue()

    async def publish(self, message: Message) -> None:
        await self._queue.put(message)

    async def get(self) -> Message:
        return await self._queue.get()
