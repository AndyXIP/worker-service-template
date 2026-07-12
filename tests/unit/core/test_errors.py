from pydantic import BaseModel, ValidationError

from core.errors import DeliveryOutcome, classify_error
from domain.errors import NotFoundError


class _Payload(BaseModel):
    value: int


def _make_validation_error() -> ValidationError:
    try:
        _Payload.model_validate({"value": "not-an-int"})
    except ValidationError as exc:
        return exc
    raise AssertionError("expected ValidationError")


def test_not_found_error_is_dead_lettered() -> None:
    outcome, reason = classify_error(NotFoundError("missing"), attempt=1, max_attempts=3)

    assert outcome is DeliveryOutcome.DEAD_LETTER
    assert reason == "not_found"


def test_validation_error_is_dead_lettered() -> None:
    outcome, reason = classify_error(_make_validation_error(), attempt=1, max_attempts=3)

    assert outcome is DeliveryOutcome.DEAD_LETTER
    assert reason == "validation_error"


def test_other_errors_retry_below_max_attempts() -> None:
    outcome, reason = classify_error(RuntimeError("boom"), attempt=1, max_attempts=3)

    assert outcome is DeliveryOutcome.RETRY
    assert reason == "transient_error"


def test_other_errors_dead_letter_at_max_attempts() -> None:
    outcome, reason = classify_error(RuntimeError("boom"), attempt=3, max_attempts=3)

    assert outcome is DeliveryOutcome.DEAD_LETTER
    assert reason == "max_attempts_exceeded"
