from typing import Protocol
from uuid import UUID

from domain.item import Item, ItemNotFoundError


class ItemRepository(Protocol):  # pragma: no cover
    """Storage abstraction for `Item` entities.

    Swap `InMemoryItemRepository` for a SQL/Mongo-backed implementation
    without touching the service or consumer layers.
    """

    def add(self, item: Item) -> None: ...

    def get(self, item_id: UUID) -> Item: ...

    def delete(self, item_id: UUID) -> None: ...


class InMemoryItemRepository:
    """Reference implementation backed by a plain dict - not thread-safe, and
    reset on every restart. Fine for examples/tests; swap in a real backend
    (see `ItemRepository`) before relying on this under load."""

    def __init__(self) -> None:
        self._items: dict[UUID, Item] = {}

    def add(self, item: Item) -> None:
        self._items[item.id] = item

    def get(self, item_id: UUID) -> Item:
        try:
            return self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(item_id) from None

    def delete(self, item_id: UUID) -> None:
        try:
            del self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(item_id) from None
