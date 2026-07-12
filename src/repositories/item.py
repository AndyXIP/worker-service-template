from typing import Protocol
from uuid import UUID

from starlette.requests import Request

from domain.item import Item, ItemNotFoundError


class ItemRepository(Protocol):  # pragma: no cover
    """Storage abstraction for `Item` entities.

    Swap `InMemoryItemRepository` for a SQL/Mongo-backed implementation
    without touching the service or API layers.
    """

    def add(self, item: Item) -> None: ...

    def get(self, item_id: UUID) -> Item: ...

    def list(self) -> list[Item]: ...

    def update(self, item: Item) -> None: ...

    def delete(self, item_id: UUID) -> None: ...


class InMemoryItemRepository:
    """Reference implementation backed by a plain dict - not thread-safe.

    API routes are `def`, not `async def`, so FastAPI runs each request in a
    threadpool and requests can genuinely interleave. Methods like `update()`
    do a check-then-set against `self._items` with no lock, so that isn't
    atomic under concurrent writes. Fine for examples/tests; swap in a real
    backend (see `ItemRepository`) before relying on this under load.
    """

    def __init__(self) -> None:
        self._items: dict[UUID, Item] = {}

    def add(self, item: Item) -> None:
        self._items[item.id] = item

    def get(self, item_id: UUID) -> Item:
        try:
            return self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(item_id) from None

    def list(self) -> list[Item]:
        return list(self._items.values())

    def update(self, item: Item) -> None:
        if item.id not in self._items:
            raise ItemNotFoundError(item.id)
        self._items[item.id] = item

    def delete(self, item_id: UUID) -> None:
        try:
            del self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(item_id) from None


def get_item_repository(request: Request) -> ItemRepository:
    """Resolves the repository from app state (see `main.create_app`).

    Storing it on `app.state` rather than a module-level singleton means each
    app instance gets its own store - handy for test isolation, since tests
    build a fresh app per test with `create_app()`.
    """
    return request.app.state.item_repository
