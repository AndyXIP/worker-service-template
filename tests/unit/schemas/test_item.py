from uuid import uuid4

import pytest
from pydantic import ValidationError

from schemas.item import ItemCreatePayload, ItemDeletePayload


def test_item_create_payload_accepts_valid_data() -> None:
    payload = ItemCreatePayload(name="Widget", description="A widget", price=9.99)

    assert payload.name == "Widget"
    assert payload.price == 9.99


def test_item_create_payload_rejects_non_positive_price() -> None:
    with pytest.raises(ValidationError):
        ItemCreatePayload(name="Widget", price=0)


def test_item_create_payload_requires_name() -> None:
    with pytest.raises(ValidationError):
        ItemCreatePayload(price=9.99)


def test_item_delete_payload_requires_item_id() -> None:
    payload = ItemDeletePayload(item_id=uuid4())

    assert payload.item_id is not None
