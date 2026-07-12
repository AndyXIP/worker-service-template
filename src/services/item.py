from datetime import UTC, datetime
from uuid import uuid4

from domain.item import Item
from repositories.item import ItemRepository
from schemas.item import ItemCreatePayload, ItemDeletePayload


class ItemService:
    """Business logic for items. The only layer that talks to the repository."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    def create_item(self, data: ItemCreatePayload) -> Item:
        item = Item(id=uuid4(), created_at=datetime.now(UTC), **data.model_dump())
        self._repository.add(item)
        return item

    def delete_item(self, data: ItemDeletePayload) -> None:
        self._repository.delete(data.item_id)
