#tests/fixtures/user_fixtures.py


import pytest
import uuid


@pytest.fixture
def user_token(client):
    email = f"test_{uuid.uuid4()}@example.com"
    password = "test12345"

    # Register
    client.post("/auth/register", json={
        "email": email,
        "password": password
    })

    # Login
    response = client.post("/auth/login", data={
        "username": email,
        "password": password
    })

    return response.json()["access_token"]
