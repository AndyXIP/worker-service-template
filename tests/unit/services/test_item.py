from uuid import uuid4

import pytest

from domain.item import ItemNotFoundError
from repositories.item import InMemoryItemRepository
from schemas.item import ItemCreatePayload, ItemDeletePayload
from services.item import ItemService


@pytest.fixture
def service() -> ItemService:
    return ItemService(InMemoryItemRepository())


def test_create_item_generates_id_and_timestamp(service: ItemService) -> None:
    item = service.create_item(ItemCreatePayload(name="Widget", price=9.99))

    assert item.id is not None
    assert item.created_at is not None
    assert item.name == "Widget"


def test_delete_item_removes_it(service: ItemService) -> None:
    created = service.create_item(ItemCreatePayload(name="Widget", price=9.99))

    service.delete_item(ItemDeletePayload(item_id=created.id))

    with pytest.raises(ItemNotFoundError):
        service.delete_item(ItemDeletePayload(item_id=created.id))


def test_delete_item_propagates_not_found(service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError):
        service.delete_item(ItemDeletePayload(item_id=uuid4()))
