"""Token Pydantic Schemas

Defines schemas for JWT authorization tokens and response payloads.
"""

from typing import Optional
from pydantic import BaseModel
from backend.app.schemas.user import UserOut


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
