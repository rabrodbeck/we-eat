import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup a clean in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the databas session dependency with the test database session
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check():
    """Verify that the API health check endpoint returns 200 OK."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_create_and_get_diners():
    """Verify that we can create a diner profile and retrieve it using authentication."""
    headers = {"Authorization": "Bearer mock-user123"}

    # 1. Create a diner profile
    diner_payload = {"name": "Olivia", "dislikes": ["pizza"], "is_active": True}
    response = client.post("/api/diners", json=diner_payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Olivia"

    # 2. Retrieve diner profiles
    response = client.get("/api/diners", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Head of Family"
    assert response.json()[1]["name"] == "Olivia"