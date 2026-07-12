from enum import Enum

from pydantic import ValidationError

from domain.errors import NotFoundError


class DeliveryOutcome(Enum):
    """What the dispatch loop should do with a message after a handler fails."""

    RETRY = "retry"
    DEAD_LETTER = "dead_letter"


def classify_error(exc: Exception, attempt: int, max_attempts: int) -> tuple[DeliveryOutcome, str]:
    """Maps a handler exception to a delivery outcome and a short reason for logging.

    `NotFoundError` and payload validation errors are permanent business
    failures - retrying changes nothing, so they go straight to the
    dead-letter queue. Anything else is treated as potentially transient and
    retried up to `max_attempts` before being dead-lettered too.
    """
    if isinstance(exc, NotFoundError):
        return DeliveryOutcome.DEAD_LETTER, "not_found"
    if isinstance(exc, ValidationError):
        return DeliveryOutcome.DEAD_LETTER, "validation_error"
    if attempt < max_attempts:
        return DeliveryOutcome.RETRY, "transient_error"
    return DeliveryOutcome.DEAD_LETTER, "max_attempts_exceeded"
