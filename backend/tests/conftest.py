"""Pytest configuration and isolated database test fixtures."""

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import Base, get_db
from backend.app.core.security import create_access_token
from backend.app.models.user import User, UserRole

# Create an in-memory SQLite database for isolated test execution
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all database tables for test session and tear down after completion."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Yield a transactional database session rolled back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a FastAPI TestClient instance overriding the get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def member_token(db_session: Session) -> str:
    """Generate a valid JWT bearer token for a standard member user."""
    from backend.app.core.security import hash_password
    user = User(
        name="Test Member",
        email="testmember@example.com",
        password_hash=hash_password("Password123!"),
        role=UserRole.MEMBER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token(subject=user.id, email=user.email, role=user.role.value)


@pytest.fixture
def manager_token(db_session: Session) -> str:
    """Generate a valid JWT bearer token for a manager user."""
    from backend.app.core.security import hash_password
    user = User(
        name="Test Manager",
        email="testmanager@example.com",
        password_hash=hash_password("ManagerPass123!"),
        role=UserRole.MANAGER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return create_access_token(subject=user.id, email=user.email, role=user.role.value)
