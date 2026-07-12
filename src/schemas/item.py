from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(examples=["Widget"])
    description: str | None = Field(default=None, examples=["A widget for demonstration purposes"])
    price: float = Field(gt=0, examples=[9.99])


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, examples=["Widget"])
    description: str | None = Field(default=None, examples=["A widget for demonstration purposes"])
    price: float | None = Field(default=None, gt=0, examples=[14.99])


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
