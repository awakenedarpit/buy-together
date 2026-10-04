"""Member Request Items CRUD API Router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.request_item import RequestItem, ItemStatus
from backend.app.schemas.message import RequestItemOut
from backend.app.schemas.request import RequestItemUpdate
from backend.app.core.logging import logger

router = APIRouter(tags=["requests"])


@router.get(
    "/requests",
    response_model=List[RequestItemOut],
    summary="List authenticated member's request items",
)
@router.get(
    "/requests/my",
    response_model=List[RequestItemOut],
    include_in_schema=False,
)
def get_my_requests(
    status_filter: Optional[ItemStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[RequestItemOut]:
    """Retrieve personal request items submitted by the current member."""
    query = db.query(RequestItem).filter(RequestItem.user_id == current_user.id)
    if status_filter:
        query = query.filter(RequestItem.status == status_filter)
    items = query.order_by(RequestItem.created_at.desc()).all()
    return [RequestItemOut.model_validate(it) for it in items]


@router.patch(
    "/requests/{item_id}",
    response_model=RequestItemOut,
    summary="Update personal request item",
)
@router.put(
    "/requests/{item_id}",
    response_model=RequestItemOut,
    include_in_schema=False,
)
def update_request_item(
    item_id: int,
    payload: RequestItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RequestItemOut:
    """Update personal item properties with strict ownership verification."""
    item = db.query(RequestItem).filter(RequestItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request item with id {item_id} not found.",
        )

    # Ownership enforcement (IDOR protection)
    if item.user_id != current_user.id:
        logger.warning(
            f"Unauthorized item update attempt: User {current_user.id} tried to edit item {item_id} owned by {item.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this item.",
        )

    if payload.name is not None:
        item.name = payload.name.strip().lower()
    if payload.variant is not None:
        item.variant = payload.variant.strip().lower() if payload.variant.strip() else None
    if payload.quantity is not None:
        item.quantity = payload.quantity
    if payload.unit is not None:
        item.unit = payload.unit.strip().lower()

    db.commit()
    db.refresh(item)
    return RequestItemOut.model_validate(item)


@router.delete(
    "/requests/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete personal request item",
)
def delete_request_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete personal request item with strict ownership verification."""
    item = db.query(RequestItem).filter(RequestItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request item with id {item_id} not found.",
        )

    # Ownership enforcement (IDOR protection)
    if item.user_id != current_user.id:
        logger.warning(
            f"Unauthorized item deletion attempt: User {current_user.id} tried to delete item {item_id} owned by {item.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this item.",
        )

    db.delete(item)
    db.commit()
    return None
