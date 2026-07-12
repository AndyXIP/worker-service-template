import time
from collections.abc import Awaitable, Callable
from typing import Any

import structlog

from core.errors import DeliveryOutcome, classify_error
from core.queue import MessageQueue

Handler = Callable[[dict[str, Any]], Awaitable[None]]

logger = structlog.get_logger("dispatch")


async def process_one(
    queue: MessageQueue,
    dead_letter_queue: MessageQueue,
    handlers: dict[str, Handler],
    max_delivery_attempts: int,
) -> None:
    """Pulls exactly one message off `queue` and dispatches it to the handler
    registered for its type, then acks (logs success), retries (republishes
    with `attempt` incremented), or dead-letters it.

    Split out from `run_forever` so tests can drive one message at a time
    instead of running an infinite loop.
    """
    message = await queue.get()
    structlog.contextvars.bind_contextvars(
        message_id=str(message.id), message_type=message.type, attempt=message.attempt
    )
    start = time.perf_counter()
    handler = handlers.get(message.type)
    try:
        if handler is None:
            raise LookupError(f"no handler registered for message type {message.type!r}")
        await handler(message.payload)
    except Exception as exc:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        if handler is None:
            logger.error(
                "message_dead_lettered", reason="unknown_message_type", duration_ms=duration_ms
            )
            await dead_letter_queue.publish(message)
        else:
            outcome, reason = classify_error(exc, message.attempt, max_delivery_attempts)
            if outcome is DeliveryOutcome.RETRY:
                logger.warning("message_retrying", reason=reason, duration_ms=duration_ms)
                await queue.publish(message.model_copy(update={"attempt": message.attempt + 1}))
            else:
                logger.error("message_dead_lettered", reason=reason, duration_ms=duration_ms)
                await dead_letter_queue.publish(message)
    else:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info("message_processed", duration_ms=duration_ms)
    finally:
        structlog.contextvars.clear_contextvars()


async def run_forever(  # pragma: no cover - thin loop wrapper; process_one is the tested unit
    queue: MessageQueue,
    dead_letter_queue: MessageQueue,
    handlers: dict[str, Handler],
    max_delivery_attempts: int,
) -> None:
    while True:
        await process_one(queue, dead_letter_queue, handlers, max_delivery_attempts)
