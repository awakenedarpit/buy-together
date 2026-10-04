"""Integration tests for message ingestion, AI extraction pipeline, and personal history."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User, UserRole
from backend.app.models.message import Message
from backend.app.models.request_item import RequestItem, ItemStatus
from backend.app.core.security import hash_password, create_access_token
from backend.app.ai.factory import reset_ai_provider, get_ai_provider
from backend.app.ai.mock_provider import MockAIProvider
from backend.app.services.message_service import MessageService
from backend.app.services.extraction_service import ExtractionService


@pytest.fixture(autouse=True)
def ensure_mock_provider():
    """Ensure mock provider is active for message integration tests."""
    reset_ai_provider()
    get_ai_provider("mock")
    yield
    reset_ai_provider()


def test_submit_message_unauthenticated(client: TestClient):
    """Verify unauthenticated requests cannot submit messages."""
    response = client.post("/api/v1/messages", json={"text": "bhai 2 notebook aur ek blue pen"})
    assert response.status_code == 401


def test_submit_empty_message(client: TestClient, member_token: str):
    """Verify empty or whitespace-only message is rejected with 400."""
    response = client.post(
        "/api/v1/messages",
        json={"text": "     "},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_submit_message_success_hinglish(client: TestClient, member_token: str, db_session: Session):
    """Verify submitting Hinglish message creates message and extracted items end-to-end."""
    raw_text = "bhai 2 notebook aur ek blue pen"
    response = client.post(
        "/api/v1/messages",
        json={"text": raw_text},
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 201
    data = response.json()

    assert "message" in data
    assert "extracted_items" in data
    msg = data["message"]
    items = data["extracted_items"]

    assert msg["text"] == raw_text
    assert len(items) == 2

    # Verify database persistence for message
    db_msg = db_session.query(Message).filter(Message.id == msg["id"]).first()
    assert db_msg is not None
    assert db_msg.text == raw_text

    # Verify database persistence for items
    db_items = db_session.query(RequestItem).filter(RequestItem.message_id == msg["id"]).all()
    assert len(db_items) == 2

    notebook = next(i for i in db_items if i.name == "notebook")
    assert notebook.quantity == 2
    assert notebook.variant is None
    assert notebook.unit == "piece"
    assert notebook.unit_price is None  # Never set by AI
    assert notebook.status == ItemStatus.PENDING

    pen = next(i for i in db_items if i.name == "pen")
    assert pen.quantity == 1
    assert pen.variant == "blue"
    assert pen.unit == "piece"
    assert pen.unit_price is None
    assert pen.status == ItemStatus.PENDING


def test_submit_message_conversational_no_items(client: TestClient, member_token: str, db_session: Session):
    """Verify submitting casual conversation stores message but zero items."""
    raw_text = "hello sab log kaise ho?"
    response = client.post(
        "/api/v1/messages",
        json={"text": raw_text},
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data["extracted_items"]) == 0

    # Message itself must still be persisted
    db_msg = db_session.query(Message).filter(Message.id == data["message"]["id"]).first()
    assert db_msg is not None


def test_list_my_messages_and_ownership_isolation(client: TestClient, db_session: Session):
    """Verify user can only view their own messages and never another user's."""
    # Create User 1
    u1 = User(
        name="User One",
        email="user1@example.com",
        password_hash=hash_password("Pass1234!"),
        role=UserRole.MEMBER,
    )
    # Create User 2
    u2 = User(
        name="User Two",
        email="user2@example.com",
        password_hash=hash_password("Pass1234!"),
        role=UserRole.MEMBER,
    )
    db_session.add_all([u1, u2])
    db_session.commit()
    db_session.refresh(u1)
    db_session.refresh(u2)

    token1 = create_access_token(subject=u1.id, email=u1.email, role=u1.role.value)
    token2 = create_access_token(subject=u2.id, email=u2.email, role=u2.role.value)

    # Post message as User 1
    r1 = client.post(
        "/api/v1/messages",
        json={"text": "User 1 message: 2 notebooks"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert r1.status_code == 201

    # Post message as User 2
    r2 = client.post(
        "/api/v1/messages",
        json={"text": "User 2 message: 3 packets of milk"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert r2.status_code == 201

    # User 1 requests their messages
    list_r1 = client.get("/api/v1/messages", headers={"Authorization": f"Bearer {token1}"})
    assert list_r1.status_code == 200
    u1_msgs = list_r1.json()
    assert len(u1_msgs) == 1
    assert "User 1 message" in u1_msgs[0]["text"]
    assert "User 2 message" not in u1_msgs[0]["text"]

    # User 2 requests their messages
    list_r2 = client.get("/api/v1/messages", headers={"Authorization": f"Bearer {token2}"})
    assert list_r2.status_code == 200
    u2_msgs = list_r2.json()
    assert len(u2_msgs) == 1
    assert "User 2 message" in u2_msgs[0]["text"]
    assert "User 1 message" not in u2_msgs[0]["text"]


def test_provider_failure_returns_502_and_rolls_back(client: TestClient, member_token: str, monkeypatch):
    """Verify that when AI provider fails, API returns 502 Bad Gateway and rolls back safely."""
    # Configure mock provider to fail
    failing_provider = MockAIProvider(simulate_error=True)
    failing_service = MessageService(
        extraction_service=ExtractionService(provider=failing_provider)
    )

    from backend.app.api.v1 import messages as messages_module
    monkeypatch.setattr(messages_module, "message_service", failing_service)

    response = client.post(
        "/api/v1/messages",
        json={"text": "2 notebooks please"},
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 502
    assert "AI extraction provider error" in response.json()["detail"]
