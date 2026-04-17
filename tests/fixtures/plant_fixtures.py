#tests/fixtures/plant_fixtures.py


import pytest
from app.models.plant import Plant


# -------------------------
# DB LEVEL PLANT
# -------------------------
@pytest.fixture
def plant(db):
    plant = Plant(
        name="Test Plant",
        species="Test",
        user_id=1,
        watering_interval_days=3,
        last_watered=None,
        use_sensor=False
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


@pytest.fixture
def sensor_plant(db):
    plant = Plant(
        name="Sensor Plant",
        species="Test",
        user_id=1,
        watering_interval_days=3,
        last_watered=None,
        use_sensor=True
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)
    return plant


# -------------------------
# API LEVEL PLANT
# -------------------------
@pytest.fixture
def plant_api(client, user_token):
    response = client.post(
        "/plants/",
        json={
            "name": "API Plant",
            "species": "Test",
            "environment_type": "indoor"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )

    return response.json()
