"""Pydantic schemas for Request Items and Manager views."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.app.models.request_item import ItemStatus


class RequestItemUpdate(BaseModel):
    """Payload for updating personal request item properties."""
    name: Optional[str] = Field(None, min_length=1, max_length=150)
    variant: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, ge=1)
    unit: Optional[str] = Field(None, max_length=50)


class PriceUpdate(BaseModel):
    """Payload for manager assigning a unit price."""
    unit_price: Decimal = Field(..., ge=0, description="Unit price >= 0")


class StatusUpdate(BaseModel):
    """Payload for manager updating item procurement status."""
    status: ItemStatus


class ManagerRequestItemOut(BaseModel):
    """Schema for item details enriched with member information."""
    id: int
    user_id: int
    user_name: str
    user_email: str
    name: str
    variant: Optional[str] = None
    quantity: int
    unit: str
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    status: ItemStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CombinedItemOut(BaseModel):
    """Dynamic grouped requirement across all members."""
    name: str
    variant: Optional[str] = None
    unit: str
    total_quantity: int
    unit_price: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    request_count: int
    member_names: List[str]
    status: str = "PENDING"


class FinancialSummary(BaseModel):
    """Procurement summary metrics."""
    total_items_count: int
    total_units_count: int
    grand_total_cost: Decimal


class CombinedResponse(BaseModel):
    """Consolidated purchasing report response."""
    items: List[CombinedItemOut]
    financial_summary: FinancialSummary
