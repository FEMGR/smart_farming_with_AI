# tests/test_locations.py

def test_create_location(client, token):
    """
    Test creating a new location (authenticated).
    """
    headers = {"Authorization": f"Bearer {token}"}

    location_data = {
        "name": "Greenhouse A",
        "description": "Main greenhouse",
        "environment_type": "greenhouse"
    }

    response = client.post("/locations/", json=location_data, headers=headers)

    assert response.status_code in [200, 201]

    data = response.json()

    # Validate response matches schema
    assert data["name"] == location_data["name"]
    assert data["description"] == location_data["description"]
    assert data["environment_type"] == location_data["environment_type"]

    # Auto-generated fields (important!)
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data


def test_get_locations(client, token):
    """
    Test retrieving locations (authenticated).
    """
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/locations/", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_locations_unauthorized(client):
    """
    Ensure endpoint is protected (no token).
    """
    response = client.get("/locations/")

    assert response.status_code == 401

def test_user_cannot_access_other_users_locations(client, create_user):
    """
    Ensure user cannot access another user's locations.
    """
    token_a = create_user()
    token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates location
    client.post("/locations/", json={
        "name": "User A Location"
    }, headers=headers_a)

    # User B fetches locations
    response = client.get("/locations/", headers=headers_b)

    data = response.json()

    # Ensure User B does NOT see User A's data
    assert all(loc["name"] != "User A Location" for loc in data)
