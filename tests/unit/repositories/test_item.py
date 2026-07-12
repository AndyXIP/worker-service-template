from datetime import UTC, datetime
from uuid import uuid4

import pytest

from domain.item import Item, ItemNotFoundError
from repositories.item import InMemoryItemRepository


def make_item(**overrides: object) -> Item:
    defaults: dict[str, object] = {
        "id": uuid4(),
        "name": "Widget",
        "description": None,
        "price": 9.99,
        "created_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    return Item(**defaults)


def test_add_and_get() -> None:
    repo = InMemoryItemRepository()
    item = make_item()

    repo.add(item)

    assert repo.get(item.id) == item


def test_get_missing_raises_not_found() -> None:
    repo = InMemoryItemRepository()

    with pytest.raises(ItemNotFoundError):
        repo.get(uuid4())


def test_delete_removes_item() -> None:
    repo = InMemoryItemRepository()
    item = make_item()
    repo.add(item)

    repo.delete(item.id)

    with pytest.raises(ItemNotFoundError):
        repo.get(item.id)


def test_delete_missing_raises_not_found() -> None:
    repo = InMemoryItemRepository()

    with pytest.raises(ItemNotFoundError):
        repo.delete(uuid4())
