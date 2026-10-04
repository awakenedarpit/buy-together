"""Authentication and Role-Based Access Control test suite."""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.api.deps import require_role
from backend.app.models.user import UserRole
from fastapi import Depends


# Register a temporary test route to verify require_role
@app.get("/api/v1/test-manager-only")
def _manager_only_handler(current_user=Depends(require_role(UserRole.MANAGER))):
    return {"message": "Welcome Manager", "user_id": current_user.id}


def test_register_user_success(client: TestClient) -> None:
    """Test successful user registration with valid data."""
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "password": "StrongPassword123!",
        "role": "MEMBER",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert data["role"] == "MEMBER"
    assert "password" not in data
    assert "password_hash" not in data
    assert "id" in data


def test_register_user_duplicate_email(client: TestClient) -> None:
    """Test that registering an existing email returns 400 Bad Request."""
    payload = {
        "name": "Alice Duplicate",
        "email": "alice_dup@example.com",
        "password": "StrongPassword123!",
        "role": "MEMBER",
    }
    first_resp = client.post("/api/v1/auth/register", json=payload)
    assert first_resp.status_code == 201

    second_resp = client.post("/api/v1/auth/register", json=payload)
    assert second_resp.status_code == 400
    assert "already exists" in second_resp.json()["detail"].lower()


def test_register_user_weak_password(client: TestClient) -> None:
    """Test that passwords shorter than 8 characters fail validation with 422."""
    payload = {
        "name": "Short Pass User",
        "email": "short@example.com",
        "password": "short",
        "role": "MEMBER",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient) -> None:
    """Test successful user login returning valid JWT access token."""
    reg_payload = {
        "name": "Bob Login",
        "email": "bob@example.com",
        "password": "CorrectPassword123!",
        "role": "MEMBER",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_payload = {
        "email": "bob@example.com",
        "password": "CorrectPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "bob@example.com"


def test_login_wrong_password(client: TestClient) -> None:
    """Test login rejection when password does not match stored hash."""
    reg_payload = {
        "name": "Charlie Login",
        "email": "charlie@example.com",
        "password": "CorrectPassword123!",
        "role": "MEMBER",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "charlie@example.com", "password": "WrongPassword999!"},
    )
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()


def test_login_nonexistent_user(client: TestClient) -> None:
    """Test login rejection for unknown email."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "SomePassword123!"},
    )
    assert response.status_code == 401


def test_read_current_user_me(client: TestClient, member_token: str) -> None:
    """Test GET /api/v1/auth/me returns current user profile with valid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testmember@example.com"
    assert data["role"] == "MEMBER"


def test_read_current_user_unauthorized(client: TestClient) -> None:
    """Test GET /api/v1/auth/me rejects request when Authorization header is missing."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_read_current_user_invalid_token(client: TestClient) -> None:
    """Test GET /api/v1/auth/me rejects forged/tampered JWT tokens."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.jwt.token.here"},
    )
    assert response.status_code == 401


def test_role_based_access_control(
    client: TestClient, member_token: str, manager_token: str
) -> None:
    """Test RBAC: Member is forbidden from accessing manager route; Manager is allowed."""
    # Member attempts to access manager route -> 403 Forbidden
    member_resp = client.get(
        "/api/v1/test-manager-only",
        headers={"Authorization": f"Bearer {member_token}"},
    )
    assert member_resp.status_code == 403
    assert "not permitted" in member_resp.json()["detail"].lower()

    # Manager attempts to access manager route -> 200 OK
    manager_resp = client.get(
        "/api/v1/test-manager-only",
        headers={"Authorization": f"Bearer {manager_token}"},
    )
    assert manager_resp.status_code == 200
    assert manager_resp.json()["message"] == "Welcome Manager"
