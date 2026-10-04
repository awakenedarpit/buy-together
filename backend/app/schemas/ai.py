"""Pydantic schemas for AI extraction contracts."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class ExtractedItem(BaseModel):
    """Structured representation of an individual extracted purchase item."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Normalized singular name of the item (e.g. 'notebook', 'pen')",
    )
    variant: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional modifier or specification (e.g. 'blue', 'ruled', 'A4')",
    )
    quantity: int = Field(
        default=1,
        ge=1,
        description="Positive integer quantity requested (must be >= 1)",
    )
    unit: str = Field(
        default="piece",
        min_length=1,
        max_length=50,
        description="Standard unit of measure (e.g. 'piece', 'packet', 'kg', 'box')",
    )

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if not cleaned:
            raise ValueError("Item name cannot be blank or only whitespace")
        return cleaned

    @field_validator("variant")
    @classmethod
    def clean_variant(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        cleaned = v.strip().lower()
        return cleaned if cleaned else None

    @field_validator("unit")
    @classmethod
    def clean_unit(cls, v: str) -> str:
        cleaned = v.strip().lower()
        return cleaned if cleaned else "piece"


class ExtractionResult(BaseModel):
    """Container for the complete result of an AI item extraction invocation."""

    items: List[ExtractedItem] = Field(
        default_factory=list,
        description="List of validated, structured items extracted from the message",
    )
    raw_response: Optional[str] = Field(
        default=None,
        description="Raw output string from the model/provider before parsing",
    )
