"""Manager Procurement & Aggregation API Router."""

from collections import defaultdict
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from backend.app.core.database import get_db
from backend.app.api.deps import require_role
from backend.app.models.user import User, UserRole
from backend.app.models.request_item import RequestItem
from backend.app.schemas.request import (
    ManagerRequestItemOut,
    CombinedResponse,
    CombinedItemOut,
    FinancialSummary,
    PriceUpdate,
    StatusUpdate,
)

router = APIRouter(prefix="/manager", tags=["manager"])


@router.get(
    "/requests",
    response_model=List[ManagerRequestItemOut],
    summary="List all requests across all members (Manager view)",
)
def get_all_requests(
    current_user: User = Depends(require_role(UserRole.MANAGER)),
    db: Session = Depends(get_db),
) -> List[ManagerRequestItemOut]:
    """Retrieve all submitted member request items with user profile details."""
    items = (
        db.query(RequestItem)
        .options(joinedload(RequestItem.user))
        .order_by(RequestItem.created_at.desc())
        .all()
    )

    out = []
    for it in items:
        total_p = None
        if it.unit_price is not None:
            total_p = Decimal(str(it.unit_price)) * it.quantity

        out.append(
            ManagerRequestItemOut(
                id=it.id,
                user_id=it.user_id,
                user_name=it.user.name if it.user else "Unknown",
                user_email=it.user.email if it.user else "unknown@example.com",
                name=it.name,
                variant=it.variant,
                quantity=it.quantity,
                unit=it.unit,
                unit_price=it.unit_price,
                total_price=total_p,
                status=it.status,
                created_at=it.created_at,
            )
        )
    return out


@router.get(
    "/combined",
    response_model=CombinedResponse,
    summary="Get dynamic consolidated procurement requirements",
)
def get_combined_requirements(
    current_user: User = Depends(require_role(UserRole.MANAGER)),
    db: Session = Depends(get_db),
) -> CombinedResponse:
    """Dynamically aggregate active requirements grouped by (name, variant, unit)."""
    items = (
        db.query(RequestItem)
        .options(joinedload(RequestItem.user))
        .all()
    )

    # Grouping by key: (name.lower(), variant.lower() if variant else None, unit.lower())
    groups = defaultdict(lambda: {
        "name": "",
        "variant": None,
        "unit": "piece",
        "total_quantity": 0,
        "request_count": 0,
        "member_names": set(),
        "unit_prices": [],
        "statuses": set(),
    })

    for it in items:
        key = (it.name.strip().lower(), it.variant.strip().lower() if it.variant else None, it.unit.strip().lower())
        g = groups[key]
        g["name"] = it.name.strip().lower()
        g["variant"] = it.variant.strip().lower() if it.variant else None
        g["unit"] = it.unit.strip().lower()
        g["total_quantity"] += it.quantity
        g["request_count"] += 1
        if it.user and it.user.name:
            g["member_names"].add(it.user.name)
        if it.unit_price is not None:
            g["unit_prices"].append(Decimal(str(it.unit_price)))
        g["statuses"].add(it.status.value)

    combined_items: List[CombinedItemOut] = []
    total_units_count = 0
    grand_total_cost = Decimal("0.00")

    for g in groups.values():
        total_units_count += g["total_quantity"]
        # Use average unit price or highest unit price if set
        avg_price = None
        item_total_cost = None
        if g["unit_prices"]:
            avg_price = sum(g["unit_prices"]) / len(g["unit_prices"])
            item_total_cost = avg_price * g["total_quantity"]
            grand_total_cost += item_total_cost

        status_str = "PENDING"
        if "APPROVED" in g["statuses"] and len(g["statuses"]) == 1:
            status_str = "APPROVED"
        elif "PURCHASED" in g["statuses"] and len(g["statuses"]) == 1:
            status_str = "PURCHASED"

        combined_items.append(
            CombinedItemOut(
                name=g["name"],
                variant=g["variant"],
                unit=g["unit"],
                total_quantity=g["total_quantity"],
                unit_price=avg_price,
                total_cost=item_total_cost,
                request_count=g["request_count"],
                member_names=sorted(list(g["member_names"])),
                status=status_str,
            )
        )

    # Sort items alphabetically by name
    combined_items.sort(key=lambda x: (x.name, x.variant or ""))

    return CombinedResponse(
        items=combined_items,
        financial_summary=FinancialSummary(
            total_items_count=len(combined_items),
            total_units_count=total_units_count,
            grand_total_cost=grand_total_cost,
        ),
    )


@router.patch(
    "/requests/{item_id}/price",
    response_model=ManagerRequestItemOut,
    summary="Assign unit price to request item",
)
def update_item_price(
    item_id: int,
    payload: PriceUpdate,
    current_user: User = Depends(require_role(UserRole.MANAGER)),
    db: Session = Depends(get_db),
) -> ManagerRequestItemOut:
    """Manager sets wholesale or retail price for an item."""
    item = db.query(RequestItem).options(joinedload(RequestItem.user)).filter(RequestItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")

    item.unit_price = payload.unit_price
    db.commit()
    db.refresh(item)

    total_p = payload.unit_price * item.quantity
    return ManagerRequestItemOut(
        id=item.id,
        user_id=item.user_id,
        user_name=item.user.name if item.user else "Unknown",
        user_email=item.user.email if item.user else "unknown@example.com",
        name=item.name,
        variant=item.variant,
        quantity=item.quantity,
        unit=item.unit,
        unit_price=item.unit_price,
        total_price=total_p,
        status=item.status,
        created_at=item.created_at,
    )


@router.patch(
    "/requests/{item_id}/status",
    response_model=ManagerRequestItemOut,
    summary="Update request item procurement status",
)
def update_item_status(
    item_id: int,
    payload: StatusUpdate,
    current_user: User = Depends(require_role(UserRole.MANAGER)),
    db: Session = Depends(get_db),
) -> ManagerRequestItemOut:
    """Manager updates item status (PENDING, APPROVED, PURCHASED, REJECTED)."""
    item = db.query(RequestItem).options(joinedload(RequestItem.user)).filter(RequestItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")

    item.status = payload.status
    db.commit()
    db.refresh(item)

    total_p = Decimal(str(item.unit_price)) * item.quantity if item.unit_price else None
    return ManagerRequestItemOut(
        id=item.id,
        user_id=item.user_id,
        user_name=item.user.name if item.user else "Unknown",
        user_email=item.user.email if item.user else "unknown@example.com",
        name=item.name,
        variant=item.variant,
        quantity=item.quantity,
        unit=item.unit,
        unit_price=item.unit_price,
        total_price=total_p,
        status=item.status,
        created_at=item.created_at,
    )
