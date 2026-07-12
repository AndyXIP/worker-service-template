from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import Depends

from domain.item import Item
from repositories.item import ItemRepository, get_item_repository
from schemas.item import ItemCreate, ItemUpdate


class ItemService:
    """Business logic for items. The only layer that talks to the repository."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    def create_item(self, data: ItemCreate) -> Item:
        item = Item(id=uuid4(), created_at=datetime.now(UTC), **data.model_dump())
        self._repository.add(item)
        return item

    def list_items(self) -> list[Item]:
        return self._repository.list()

    def get_item(self, item_id: UUID) -> Item:
        return self._repository.get(item_id)

    def update_item(self, item_id: UUID, data: ItemUpdate) -> Item:
        current = self._repository.get(item_id)
        updated = current.model_copy(update=data.model_dump(exclude_unset=True))
        self._repository.update(updated)
        return updated

    def delete_item(self, item_id: UUID) -> None:
        self._repository.delete(item_id)


def get_item_service(repository: ItemRepository = Depends(get_item_repository)) -> ItemService:
    return ItemService(repository)
