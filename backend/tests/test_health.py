"""Tests for the health check and metadata endpoint."""

from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient) -> None:
    """Verify that GET /api/v1/health returns 200 OK with correct schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "ai_provider" in data
    assert data["version"] == "0.1.0"
    assert "timestamp" in data
