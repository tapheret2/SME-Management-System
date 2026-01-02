import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.services.auth import hash_password


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(scope="function")
def admin_user(db):
    """Create an admin user for testing."""
    user = User(
        email="admin@test.com",
        hashed_password=hash_password("password123"),
        full_name="Test Admin",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def staff_user(db):
    """Create a staff user for testing."""
    user = User(
        email="staff@test.com",
        hashed_password=hash_password("password123"),
        full_name="Test Staff",
        role=UserRole.STAFF,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    """Get auth token for admin user."""
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def staff_token(client, staff_user):
    """Get auth token for staff user."""
    response = client.post("/api/auth/login", json={
        "email": "staff@test.com",
        "password": "password123"
    })
    return response.json()["access_token"]


def auth_header(token: str):
    """Create authorization header."""
    return {"Authorization": f"Bearer {token}"}
