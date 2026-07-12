import pytest
from pydantic import ValidationError

from schemas.item import ItemCreate, ItemUpdate


def test_item_create_accepts_valid_data() -> None:
    item = ItemCreate(name="Widget", description="A widget", price=9.99)

    assert item.name == "Widget"
    assert item.price == 9.99


def test_item_create_rejects_non_positive_price() -> None:
    with pytest.raises(ValidationError):
        ItemCreate(name="Widget", price=0)


def test_item_create_requires_name() -> None:
    with pytest.raises(ValidationError):
        ItemCreate(price=9.99)


def test_item_update_allows_partial_data() -> None:
    update = ItemUpdate(price=12.5)

    assert update.name is None
    assert update.price == 12.5
