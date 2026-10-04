"""User and Authentication Pydantic Schemas

Defines request validation and response serialization models for user management.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from backend.app.models.user import UserRole


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr


class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128, description="Minimum 8 characters")
    role: UserRole = Field(default=UserRole.MEMBER)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Name cannot be empty or only whitespace")
        return stripped


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserOut(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
