# tests/utils/test_helpers.py

from app.models.plant import Plant


def create_test_plant_db(db, user_id=1, use_sensor=False):
    plant = Plant(
        name="Test Plant",
        species_id=1,
        user_id=user_id,
        watering_interval_days=3,
        last_watered=None,
        use_sensor=use_sensor
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


def create_test_plant(client, token):
    """
    Helper to create a plant with authentication.
    Keeps test code clean and reusable.
    """
    return client.post(
        "/plants/",
        json={
            "name": "Test Plant",
            "species_name": "Test Species",
            "environment_type": "indoor",
            "is_synced": True,
            "source": "test"
        },
        headers={"Authorization": f"Bearer {token}"}
    )



def create_test_location(client, token):
    """
    Create a location and return its response JSON.
    """
    response = client.post(
        "/locations/",
        json={
            "name": "Test Location",
            "description": "Test Desc",
            "environment_type": "indoor"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 201]
    return response.json()
