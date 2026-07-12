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


def test_list_returns_all_items() -> None:
    repo = InMemoryItemRepository()
    first, second = make_item(), make_item()
    repo.add(first)
    repo.add(second)

    assert {item.id for item in repo.list()} == {first.id, second.id}


def test_update_replaces_existing_item() -> None:
    repo = InMemoryItemRepository()
    item = make_item()
    repo.add(item)

    updated = item.model_copy(update={"price": 19.99})
    repo.update(updated)

    assert repo.get(item.id).price == 19.99


def test_update_missing_raises_not_found() -> None:
    repo = InMemoryItemRepository()

    with pytest.raises(ItemNotFoundError):
        repo.update(make_item())


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
