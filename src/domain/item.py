from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from domain.errors import NotFoundError


class Item(BaseModel):
    """The item domain entity, independent of API transport shape."""

    id: UUID
    name: str
    description: str | None = None
    price: float
    created_at: datetime


class ItemNotFoundError(NotFoundError):
    def __init__(self, item_id: UUID) -> None:
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")
