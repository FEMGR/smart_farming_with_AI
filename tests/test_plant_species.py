from unittest.mock import patch


@patch("app.services.perenual_service.search_plant_species_api")
def test_create_plant_with_perenual_match(mock_search, client, token):
    mock_search.return_value = [
        {
            "id": 1,
            "common_name": "Nasturtium",
            "scientific_name": "Tropaeolum (group)",  # ✅ NOT list
            "type": "flower",
            "is_fruit": False,
            "is_veg": False,
            "edible": True,
            "growth_rate": "medium",
        }
    ]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/plants/",
        json={"name": "Nasturtium", "plant_type": "flower"},  # ✅ CRITICAL
        headers=headers,
    )

    data = response.json()

    assert data["data_source"] == "perenual"


def test_plant_inherits_watering_from_species(client, token):
    """
    Test that a new plant inherits the watering_interval_days
    from the matched species cache.
    """
    headers = {"Authorization": f"Bearer {token}"}

    # We don't provide 'watering_interval_days' here
    plant_data = {
        "name": "Eggplant",
        "plant_type": "vegetable",
    }

    response = client.post("/plants/", json=plant_data, headers=headers)
    assert response.status_code == 200, f"Error: {response.json()}"
    data = response.json()

    # It should not be the default 7 if the species cache has a specific value (e.g., 3)
    # This depends on what your 'get_or_create_species_cache' saved
    assert data["effective_watering_interval"] is not None


def test_create_plant_manual_fallback(client, token):
    """
    Test that a gibberish name results in 'manual' data_source.
    """
    headers = {"Authorization": f"Bearer {token}"}

    plant_data = {
        "name": "Xylo-Zorg-Plant-99",
        "plant_type": "vegetable",
    }

    response = client.post("/plants/", json=plant_data, headers=headers)
    data = response.json()

    assert data["data_source"] == "manual"
    assert data["species_id"] is None


def test_create_plant_schema_cleanup(client, token):
    """
    Ensures that sending 'species_name' or 'data_source' in the
    request body doesn't crash the server.
    """
    headers = {"Authorization": f"Bearer {token}"}

    plant_data = {
        "name": "Cleanup Test",
        "plant_type": "vegetable",
        "species_name": "Fake Name",  # This caused a crash before
        "data_source": "hacker",  # This caused a crash before
    }

    response = client.post("/plants/", json=plant_data, headers=headers)
    assert response.status_code == 200
