"""Pydantic schemas for Message endpoints and responses."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.app.models.request_item import ItemStatus


class MessageCreate(BaseModel):
    """Payload for submitting a natural language message."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language message containing purchase requests",
        examples=["bhai 2 notebook aur ek blue pen"],
    )


class RequestItemOut(BaseModel):
    """Schema for individual item outputs linked to a message."""
    id: int
    message_id: Optional[int] = None
    user_id: int
    name: str
    variant: Optional[str] = None
    quantity: int
    unit: str
    unit_price: Optional[Decimal] = None
    status: ItemStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageOut(BaseModel):
    """Schema for stored message metadata."""
    id: int
    user_id: int
    text: str
    created_at: datetime
    request_items: List[RequestItemOut] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Combined response returning stored message and newly extracted items."""
    message: MessageOut
    extracted_items: List[RequestItemOut]

    model_config = ConfigDict(from_attributes=True)
