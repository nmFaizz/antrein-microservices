import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from uuid import UUID

from app.main import app
from app.db.database import get_session
from app.auth.dependencies import get_current_user, require_admin
from app.menu.models import Menu
from app.preorder.models import Preorder, PreorderItem

# Setup an in-memory SQLite database for testing
DATABASE_URL = "sqlite://"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

class MockAuth:
    def __init__(self):
        # Default user payload matching token decode structure
        self.user = {"user_id": UUID("11111111-1111-1111-1111-111111111111"), "role": "user"}
        self.admin = {"user_id": UUID("22222222-2222-2222-2222-222222222222"), "role": "admin"}
        self.current_user = self.user

    def get_current_user(self):
        return self.current_user

    def require_admin(self):
        from fastapi import HTTPException, status
        if self.current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return self.current_user

# Global mock auth instance to easily switch roles in tests
mock_auth = MockAuth()

@pytest.fixture(name="session")
def session_fixture():
    # Create tables in the testing database
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Clean up tables after test is done
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session
    
    # Override FastAPI dependencies
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = mock_auth.get_current_user
    app.dependency_overrides[require_admin] = mock_auth.require_admin
    
    with TestClient(app) as client:
        yield client
    
    # Clean up overrides after test
    app.dependency_overrides.clear()

@pytest.fixture(name="mock_auth_service")
def mock_auth_service_fixture():
    return mock_auth
