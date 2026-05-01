# tests/test_plants.py

from tests.utils.test_helpers import create_test_location

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
        "plant_type": "flower"
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
        "plant_type": "evergreen",
        "is_synced": True,
        "data_source": "test"
    }, headers=headers)

    response = client.get("/plants/", headers=headers)

    data = response.json()

    assert any(p["name"] == "TestPlant" for p in data)

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
        "plant_type": "evergreen",
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
        "plant_type": "evergreen",
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
            "plant_type": "evergreen",
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
        "plant_type": "evergreen",
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
        "name": "Nasturtium",
        "plant_type": "flower"
    }

    response = client.post("/plants/", json=plant_data, headers=headers)
    assert response.status_code == 200 # Should pass now



