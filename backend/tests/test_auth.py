import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from app.auth import verify_token

# Define a mock FastAPI app to test the dependency in isoloation
app = FastAPI()

@app.get("/protected")
def protected_route(user = Depends(verify_token)):
    return {"message": "success", "user": user}

client = TestClient(app)

def test_missing_auth_header():
    """Verify taht requests with no auth header return a 401 error."""
    response = client.get("/protected")
    assert response.status_code == 401
    assert "Missing" in response.json()["detail"]

def test_invalid_token():
    """Verify that requests with an invalid token return a 401 error."""
    response = client.get("/protected", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]

def test_valid_mock_token():
    """Vefiry that requests with a mock-prefix token are accepted in development mode."""
    response = client.get("/protected", headers={"Authorization": "Bearer mock-user123"})
    assert response.status_code == 200
    assert response.json()["user"]["uid"] == "user123"
    assert response.json()["user"]["email"] == "mock-user123@example.com"
    