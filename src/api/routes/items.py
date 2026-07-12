from uuid import UUID

from fastapi import APIRouter, Depends, status

from core.auth import Principal, get_current_principal
from schemas.item import ItemCreate, ItemRead, ItemUpdate
from services.item import ItemService, get_item_service

router = APIRouter(prefix="/items", tags=["items"])


# Reads are public; writes require a bearer token (see core/auth.py) - a
# stand-in for whatever read/write split your real service needs.
@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    service: ItemService = Depends(get_item_service),
    principal: Principal = Depends(get_current_principal),
) -> ItemRead:
    item = service.create_item(data)
    return ItemRead.model_validate(item)


@router.get("", response_model=list[ItemRead])
def list_items(service: ItemService = Depends(get_item_service)) -> list[ItemRead]:
    items = service.list_items()
    return [ItemRead.model_validate(item) for item in items]


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: UUID, service: ItemService = Depends(get_item_service)) -> ItemRead:
    item = service.get_item(item_id)
    return ItemRead.model_validate(item)


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: UUID,
    data: ItemUpdate,
    service: ItemService = Depends(get_item_service),
    principal: Principal = Depends(get_current_principal),
) -> ItemRead:
    item = service.update_item(item_id, data)
    return ItemRead.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: UUID,
    service: ItemService = Depends(get_item_service),
    principal: Principal = Depends(get_current_principal),
) -> None:
    service.delete_item(item_id)
