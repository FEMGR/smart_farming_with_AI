# tests/test_locations.py


def test_create_location(client, token):
    """
    Test creating a new location (authenticated).
    """
    headers = {"Authorization": f"Bearer {token}"}

    location_data = {
        "name": "Greenhouse A",
        "description": "Main greenhouse",
        "environment_type": "greenhouse",
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
    client.post("/locations/", json={"name": "User A Location"}, headers=headers_a)

    # User B fetches locations
    response = client.get("/locations/", headers=headers_b)

    data = response.json()

    # Ensure User B does NOT see User A's data
    assert all(loc["name"] != "User A Location" for loc in data)


def test_create_location_with_gps(client, token):
    """
    Test creating a new location with optional GPS coordinates (authenticated).
    """
    headers = {"Authorization": f"Bearer {token}"}

    location_data = {
        "name": "GPS Yard",
        "latitude": 37.7749,
        "longitude": -122.4194,
    }

    response = client.post("/locations/", json=location_data, headers=headers)
    assert response.status_code in [200, 201]

    data = response.json()
    assert data["name"] == location_data["name"]
    assert data["latitude"] == location_data["latitude"]
    assert data["longitude"] == location_data["longitude"]


def test_update_location_gps(client, token):
    """
    Test updating a location's GPS coordinates (authenticated).
    """
    headers = {"Authorization": f"Bearer {token}"}

    # Create location
    create_response = client.post("/locations/", json={"name": "Before GPS"}, headers=headers)
    assert create_response.status_code in [200, 201]
    loc_id = create_response.json()["id"]

    # Update with GPS
    update_data = {
        "latitude": 45.5152,
        "longitude": -122.6784,
    }
    update_response = client.patch(f"/locations/{loc_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200

    data = update_response.json()
    assert data["latitude"] == update_data["latitude"]
    assert data["longitude"] == update_data["longitude"]


def test_user_cannot_update_other_users_location(client, create_user):
    """
    Ensure user cannot update another user's location.
    """
    token_a = create_user()
    token_b = create_user()

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # User A creates a location
    create_response = client.post("/locations/", json={"name": "User A Yard"}, headers=headers_a)
    assert create_response.status_code in [200, 201]
    loc_id = create_response.json()["id"]

    # User B tries to update User A's location
    update_response = client.patch(f"/locations/{loc_id}", json={"name": "Hacked Yard"}, headers=headers_b)
    assert update_response.status_code == 404
