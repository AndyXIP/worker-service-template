from uuid import UUID

from pydantic import BaseModel, Field


class ItemCreatePayload(BaseModel):
    """Payload for an `item.create` message."""

    name: str = Field(examples=["Widget"])
    description: str | None = Field(default=None, examples=["A widget for demonstration purposes"])
    price: float = Field(gt=0, examples=[9.99])


class ItemDeletePayload(BaseModel):
    """Payload for an `item.delete` message."""

    item_id: UUID
