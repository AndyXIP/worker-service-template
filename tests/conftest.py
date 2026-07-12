import pytest

from core.queue import InMemoryMessageQueue
from repositories.item import InMemoryItemRepository


@pytest.fixture
def item_repository() -> InMemoryItemRepository:
    """Fresh in-memory item store per test."""
    return InMemoryItemRepository()


@pytest.fixture
def queue() -> InMemoryMessageQueue:
    """Fresh in-memory queue per test."""
    return InMemoryMessageQueue()


@pytest.fixture
def dead_letter_queue() -> InMemoryMessageQueue:
    """Fresh in-memory dead-letter queue per test."""
    return InMemoryMessageQueue()
