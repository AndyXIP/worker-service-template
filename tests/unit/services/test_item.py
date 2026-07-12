from uuid import uuid4

import pytest

from domain.item import ItemNotFoundError
from repositories.item import InMemoryItemRepository
from schemas.item import ItemCreate, ItemUpdate
from services.item import ItemService


@pytest.fixture
def service() -> ItemService:
    return ItemService(InMemoryItemRepository())


def test_create_item_generates_id_and_timestamp(service: ItemService) -> None:
    item = service.create_item(ItemCreate(name="Widget", price=9.99))

    assert item.id is not None
    assert item.created_at is not None
    assert item.name == "Widget"


def test_list_items_returns_created_items(service: ItemService) -> None:
    service.create_item(ItemCreate(name="Widget", price=9.99))
    service.create_item(ItemCreate(name="Gadget", price=19.99))

    assert {item.name for item in service.list_items()} == {"Widget", "Gadget"}


def test_get_item_returns_created_item(service: ItemService) -> None:
    created = service.create_item(ItemCreate(name="Widget", price=9.99))

    assert service.get_item(created.id) == created


def test_get_item_propagates_not_found(service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError):
        service.get_item(uuid4())


def test_update_item_applies_only_provided_fields(service: ItemService) -> None:
    created = service.create_item(ItemCreate(name="Widget", description="Original", price=9.99))

    updated = service.update_item(created.id, ItemUpdate(price=15.0))

    assert updated.price == 15.0
    assert updated.name == "Widget"
    assert updated.description == "Original"


def test_update_item_propagates_not_found(service: ItemService) -> None:
    with pytest.raises(ItemNotFoundError):
        service.update_item(uuid4(), ItemUpdate(price=15.0))


def test_delete_item_removes_it(service: ItemService) -> None:
    created = service.create_item(ItemCreate(name="Widget", price=9.99))

    service.delete_item(created.id)

    with pytest.raises(ItemNotFoundError):
        service.get_item(created.id)
