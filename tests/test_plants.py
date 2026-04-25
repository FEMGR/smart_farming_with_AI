import pytest
import uuid
from fastapi.testclient import TestClient
from main import app # Replace 'main' with your actual entry file name

'''
def get_auth_token(client):
    unique_email = f"test_{uuid.uuid4()}@example.com"
    paswd = "test123"

    # Register user
    client.post(
        "/auth/register",
        json={
            "email": unique_email,
            "password": paswd
        }
    )

    # Login user
    response = client.post(
        "/auth/login",
        data={
            "username": unique_email,
            "password": paswd
        }
    )
    # Safety check: if this fails, response.json() is a dict (safe for logging)
    assert response.status_code == 200, f"Login failed: {response.text}"

    return response.json()["access_token"]


def test_create_plant(client):
    token = get_auth_token(client)

    response = client.post(
        "/plants",
        json={
            "name": "Tomato",
            "species_name": "Solanum lycopersicum",
            "location": "Greenhouse"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200


def test_get_plants(client):
    token = get_auth_token(client)

    response = client.get(
        "/plants",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

'''

'''
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def token(client):
    """Registers a unique user and returns an auth token string."""
    unique_email = f"test_{uuid.uuid4()}@example.com"
    paswd = "test12345"

    # 1. Register User (JSON)
    client.post(
        "/auth/register",
        json={"email": unique_email, "password": paswd}
    )

    # 2. Login User (Form Data)
    # MUST use 'data=' and 'username' for OAuth2 compliance
    response = client.post(
        "/auth/login",
        data={
            "username": unique_email,
            "password": paswd
        }
    )

    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]

'''


# tests/test_plants.py

def test_get_plants(client, token):
    """Test retrieving plants using the token fixture."""
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/plants/", headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    # If list is not empty, validate structure
    if data:
        assert "id" in data[0]
        assert "name" in data[0]


def test_create_plant(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    plant_data = {
        "name": "Nasturtium",  # High-confidence name
        "environment_type": "indoor"
    }

    response = client.post("/plants/", json=plant_data, headers=headers)
    assert response.status_code in [200, 201]

    data = response.json()

    # If the AI works, it should be perenual
    assert data["data_source"] == "perenual"
    assert data["name"] == "Nasturtium"


def test_get_plants_unauthorized(client):
    """
    Ensure endpoint rejects requests without token.
    """
    response = client.get("/plants/")

    assert response.status_code == 401

def test_create_and_get_plants(client, token):
    """
    Ensure created plant appears in list.
    """
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/plants/", json={
        "name": "TestPlant",
        "environment_type": "indoor",
        "is_synced": True,
        "data_source": "test"
    }, headers=headers)

    response = client.get("/plants/", headers=headers)

    data = response.json()

    assert any(p["name"] == "TestPlant" for p in data)


from tests.utils.test_helpers import create_test_location


def test_create_plant_with_location(client, token):
    """
    Test that a plant can be linked to a location.
    """
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Create location
    location = create_test_location(client, token)
    location_id = location["id"]

    # Step 2: Create plant linked to that location
    plant_data = {
        "name": "Linked Plant",
        "environment_type": "indoor",
        "is_synced": True,
        "data_source": "test",
        "location_id": location_id   # key relationship
    }

    response = client.post("/plants/", json=plant_data, headers=headers)

    assert response.status_code in [200, 201]

    data = response.json()

    # Validate relationship
    assert data["location_id"] == location_id


def test_create_plant_invalid_location(client, token):
    """
    Should fail if location does not exist.
    """
    headers = {"Authorization": f"Bearer {token}"}

    plant_data = {
        "name": "Bad Plant",
        "environment_type": "indoor",
        "is_synced": True,
        "data_source": "test",
        "location_id": 999999  # fake ID
    }

    response = client.post("/plants/", json=plant_data, headers=headers)

    assert response.status_code in [400, 404]

def test_create_plant_wrong_user_location(client, create_user):
    """
    User should NOT use another user's location.
    """
    token_a = create_user()
    token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates location
    location = client.post(
        "/locations/",
        json={"name": "Private Location"},
        headers=headers_a
    ).json()

    # User B tries to use it
    response = client.post(
        "/plants/",
        json={
            "name": "Hack Plant",
            "species_name": "Test",
            "environment_type": "indoor",
            "is_synced": True,
            "data_source": "test",
            "location_id": location["id"]
        },
        headers=headers_b
    )

    assert response.status_code in [403, 404]


def test_delete_location_blocked_if_has_plants(client, token):
    """
    Deleting a location with plants should be blocked.
    """
    headers = {"Authorization": f"Bearer {token}"}

    # Create location
    loc = client.post("/locations/", json={
        "name": "Temp Location"
    }, headers=headers).json()

    # Create plant linked to location
    client.post("/plants/", json={
        "name": "Temp Plant",
        "species_name": "Test",
        "environment_type": "indoor",
        "is_synced": True,
        "data_source": "test",
        "location_id": loc["id"]
    }, headers=headers)

    # Attempt delete
    response = client.delete(f"/locations/{loc['id']}", headers=headers)

    assert response.status_code == 400


def test_create_plant_with_ai_linking(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    plant_data = {
        "name": "Nasturtium",  # Use 'name' for the search query
        "environment_type": "outdoor"
    }

    response = client.post("/plants/", json=plant_data, headers=headers)
    assert response.status_code == 200 # Should pass now



