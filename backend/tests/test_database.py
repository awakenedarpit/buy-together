"""Database models and cascade integrity test suite."""

from decimal import Decimal
import pytest
from sqlalchemy.orm import Session
from backend.app.models.user import User, UserRole
from backend.app.models.message import Message
from backend.app.models.request_item import RequestItem, ItemStatus
from backend.app.core.security import hash_password


def test_user_creation_and_query(db_session: Session) -> None:
    """Test user model persistence, default fields, and retrieval."""
    user = User(
        name="John Doe",
        email="john@example.com",
        password_hash=hash_password("Secret123!"),
        role=UserRole.MEMBER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.role == UserRole.MEMBER
    assert user.created_at is not None
    assert user.updated_at is not None


def test_cascade_delete_integrity(db_session: Session) -> None:
    """Verify that deleting a user cascades and deletes associated messages and items."""
    user = User(
        name="Jane Doe",
        email="jane@example.com",
        password_hash=hash_password("Secret123!"),
        role=UserRole.MEMBER,
    )
    db_session.add(user)
    db_session.commit()

    message = Message(
        user_id=user.id,
        text="bhai 2 notebooks",
    )
    db_session.add(message)
    db_session.commit()

    item = RequestItem(
        user_id=user.id,
        message_id=message.id,
        name="notebook",
        variant=None,
        quantity=2,
        unit="piece",
        unit_price=Decimal("45.50"),
        status=ItemStatus.PENDING,
    )
    db_session.add(item)
    db_session.commit()

    # Verify entities exist
    assert db_session.query(Message).filter_by(user_id=user.id).count() == 1
    assert db_session.query(RequestItem).filter_by(user_id=user.id).count() == 1

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Verify cascade deletion
    assert db_session.query(Message).filter_by(user_id=user.id).count() == 0
    assert db_session.query(RequestItem).filter_by(user_id=user.id).count() == 0


def test_message_deletion_preserves_request_items(db_session: Session) -> None:
    """Verify that deleting a message does NOT delete associated request items (SET NULL)."""
    user = User(
        name="Alex Smith",
        email="alex@example.com",
        password_hash=hash_password("Secret123!"),
        role=UserRole.MEMBER,
    )
    db_session.add(user)
    db_session.commit()

    message = Message(
        user_id=user.id,
        text="3 pens",
    )
    db_session.add(message)
    db_session.commit()

    item = RequestItem(
        user_id=user.id,
        message_id=message.id,
        name="pen",
        variant=None,
        quantity=3,
        unit="piece",
        status=ItemStatus.PENDING,
    )
    db_session.add(item)
    db_session.commit()

    # Delete message
    db_session.delete(message)
    db_session.commit()

    # Item must still exist for the user
    surviving_item = db_session.query(RequestItem).filter_by(id=item.id).first()
    assert surviving_item is not None
    assert surviving_item.user_id == user.id
    assert surviving_item.name == "pen"

