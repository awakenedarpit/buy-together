"""Pytest configuration and shared test fixtures."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Create a FastAPI TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client
