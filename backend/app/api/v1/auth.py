"""Authentication API Router

Handles user registration, login with JWT bearer token issuance, and authenticated user profile retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token
import os
from backend.app.models.user import User, UserRole
from backend.app.schemas.user import UserRegister, UserLogin, UserOut, DemoLoginRequest
from backend.app.schemas.token import TokenResponse
from backend.app.core.logging import logger
from backend.app.core.config import settings

DEMO_MEMBER_EMAIL = os.getenv("DEMO_MEMBER_EMAIL", settings.DEMO_MEMBER_EMAIL)
DEMO_MEMBER_PASSWORD = os.getenv("DEMO_MEMBER_PASSWORD", settings.DEMO_MEMBER_PASSWORD)
DEMO_MANAGER_EMAIL = os.getenv("DEMO_MANAGER_EMAIL", settings.DEMO_MANAGER_EMAIL)
DEMO_MANAGER_PASSWORD = os.getenv("DEMO_MANAGER_PASSWORD", settings.DEMO_MANAGER_PASSWORD)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_in: UserRegister,
    db: Session = Depends(get_db),
) -> UserOut:
    """Register a new user account with hashed password and role assignment."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    user = User(
        name=user_in.name,
        email=user_in.email.lower(),
        password_hash=hash_password(user_in.password),
        role=user_in.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)



@router.post("/login", response_model=TokenResponse)
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate credentials and issue a signed JWT access token."""
    user = db.query(User).filter(User.email == credentials.email.lower()).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id,
        email=user.email,
        role=user.role.value,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.post("/demo-login", response_model=TokenResponse)
def demo_login(
    payload: DemoLoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Seamless server-side demo authentication without client-side credentials.

    Automatically creates or reuses the dedicated demo user (MEMBER or MANAGER),
    stores/verifies hashed credentials securely on the server, and issues a standard JWT token.
    """
    if payload.role == UserRole.MANAGER:
        email = DEMO_MANAGER_EMAIL.lower()
        password = DEMO_MANAGER_PASSWORD
        name = "Demo Manager"
        target_role = UserRole.MANAGER
    else:
        email = DEMO_MEMBER_EMAIL.lower()
        password = DEMO_MEMBER_PASSWORD
        name = "Demo Member"
        target_role = UserRole.MEMBER

    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.info(f"Auto-provisioning demo user {email} with role {target_role}")
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=target_role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        if user.role != target_role:
            user.role = target_role
            db.commit()
            db.refresh(user)

    access_token = create_access_token(
        subject=user.id,
        email=user.email,
        role=user.role.value,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> UserOut:
    """Retrieve the profile of the currently authenticated user."""
    return UserOut.model_validate(current_user)


