from typing import Any

from consumers.dispatch import Handler
from schemas.item import ItemCreatePayload, ItemDeletePayload
from services.item import ItemService


def make_item_create_handler(service: ItemService) -> Handler:
    async def handle(payload: dict[str, Any]) -> None:
        service.create_item(ItemCreatePayload.model_validate(payload))

    return handle


def make_item_delete_handler(service: ItemService) -> Handler:
    async def handle(payload: dict[str, Any]) -> None:
        service.delete_item(ItemDeletePayload.model_validate(payload))

    return handle
