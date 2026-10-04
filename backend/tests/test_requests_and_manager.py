"""Unit and Integration Tests for Member Requests CRUD and Manager Aggregation Endpoints."""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.user import User, UserRole
from backend.app.models.message import Message
from backend.app.models.request_item import RequestItem, ItemStatus
from backend.app.core.security import create_access_token


@pytest.fixture
def member_user(db_session: Session) -> User:
    user = User(
        email="member1@example.com",
        name="Alice Member",
        password_hash="fakehash",
        role=UserRole.MEMBER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_member_user(db_session: Session) -> User:
    user = User(
        email="member2@example.com",
        name="Bob Member",
        password_hash="fakehash",
        role=UserRole.MEMBER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def manager_user(db_session: Session) -> User:
    user = User(
        email="manager@example.com",
        name="Carol Manager",
        password_hash="fakehash",
        role=UserRole.MANAGER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def member_token(member_user: User) -> str:
    return create_access_token(subject=member_user.id, email=member_user.email, role=member_user.role.value)


@pytest.fixture
def other_token(other_member_user: User) -> str:
    return create_access_token(subject=other_member_user.id, email=other_member_user.email, role=other_member_user.role.value)


@pytest.fixture
def manager_token(manager_user: User) -> str:
    return create_access_token(subject=manager_user.id, email=manager_user.email, role=manager_user.role.value)



def test_member_crud_and_idor_protection(
    client: TestClient,
    db_session: Session,
    member_user: User,
    other_member_user: User,
    member_token: str,
    other_token: str,
):
    msg = Message(user_id=member_user.id, text="bhai 2 notebook")
    db_session.add(msg)
    db_session.commit()

    item = RequestItem(
        message_id=msg.id,
        user_id=member_user.id,
        name="notebook",
        quantity=2,
        unit="piece",
        status=ItemStatus.PENDING,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    # 1. Member lists personal items
    res = client.get("/api/v1/requests", headers={"Authorization": f"Bearer {member_token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "notebook"
    assert data[0]["quantity"] == 2

    # 2. Member updates their own item
    res = client.patch(
        f"/api/v1/requests/{item.id}",
        json={"quantity": 5, "variant": "ruled"},
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert res.status_code == 200
    assert res.json()["quantity"] == 5
    assert res.json()["variant"] == "ruled"

    # 3. IDOR test: other member tries to update Alice's item -> 403 Forbidden
    res = client.patch(
        f"/api/v1/requests/{item.id}",
        json={"quantity": 99},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403

    # 4. IDOR test: other member tries to delete Alice's item -> 403 Forbidden
    res = client.delete(
        f"/api/v1/requests/{item.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403

    # 5. Member deletes their own item
    res = client.delete(
        f"/api/v1/requests/{item.id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert res.status_code == 204

    # Verify deleted
    res = client.get("/api/v1/requests", headers={"Authorization": f"Bearer {member_token}"})
    assert len(res.json()) == 0


def test_manager_views_and_dynamic_aggregation(
    client: TestClient,
    db_session: Session,
    member_user: User,
    other_member_user: User,
    member_token: str,
    manager_token: str,
):
    # Member creates item 1: 2 notebooks
    it1 = RequestItem(
        user_id=member_user.id,
        name="notebook",
        variant=None,
        quantity=2,
        unit="piece",
        status=ItemStatus.PENDING,
    )
    # Other member creates item 2: 3 notebooks
    it2 = RequestItem(
        user_id=other_member_user.id,
        name="notebook",
        variant=None,
        quantity=3,
        unit="piece",
        status=ItemStatus.PENDING,
    )
    # Other member creates item 3: 1 blue pen
    it3 = RequestItem(
        user_id=other_member_user.id,
        name="pen",
        variant="blue",
        quantity=1,
        unit="piece",
        status=ItemStatus.PENDING,
    )
    db_session.add_all([it1, it2, it3])
    db_session.commit()

    # 1. Non-manager blocked from manager endpoints
    res = client.get("/api/v1/manager/requests", headers={"Authorization": f"Bearer {member_token}"})
    assert res.status_code == 403

    # 2. Manager views all requests
    res = client.get("/api/v1/manager/requests", headers={"Authorization": f"Bearer {manager_token}"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3

    # 3. Manager views combined requirements
    res = client.get("/api/v1/manager/combined", headers={"Authorization": f"Bearer {manager_token}"})
    assert res.status_code == 200
    combined = res.json()
    assert len(combined["items"]) == 2  # notebook (sum 5) and pen (sum 1)

    notebook_group = next(i for i in combined["items"] if i["name"] == "notebook")
    assert notebook_group["total_quantity"] == 5
    assert notebook_group["request_count"] == 2
    assert "Alice Member" in notebook_group["member_names"]
    assert "Bob Member" in notebook_group["member_names"]

    # 4. Manager sets price on item
    res = client.patch(
        f"/api/v1/manager/requests/{it1.id}/price",
        json={"unit_price": 50.0},
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert res.status_code == 200
    assert float(res.json()["unit_price"]) == 50.0
    assert float(res.json()["total_price"]) == 100.0  # 50 * 2
