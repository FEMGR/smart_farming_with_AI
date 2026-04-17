# tests/test_irrigation_service.py

from datetime import date, timedelta
from app.services.irrigation_service import needs_watering


def test_schedule_watering(db, plant):
    plant.last_watered = date.today() - timedelta(days=5)
    db.commit()

    assert needs_watering(db, plant) is True


def test_sensor_dry(db, sensor_plant, dry_soil):
    assert needs_watering(db, sensor_plant) is True


def test_sensor_wet(db, sensor_plant, wet_soil):
    assert needs_watering(db, sensor_plant) is False


def test_use_sensor_disabled(db, plant):
    plant.last_watered = date.today()
    db.commit()

    assert needs_watering(db, plant) is False

#sensor enabled but no data ever recorded
def test_sensor_enabled_no_data_fallback(db, sensor_plant):
    assert needs_watering(db, sensor_plant) is True



def test_full_irrigation_flow(client, token):
    # create plant
    response = client.post(
        "/plants/",
        json={"name": "Tomato"},
        headers={"Authorization": f"Bearer {token}"}
    )
    plant_id = response.json()["id"]

    # trigger irrigation check
    response = client.get(
        "/irrigation/needs-water",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
