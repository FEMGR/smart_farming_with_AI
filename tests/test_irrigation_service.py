from datetime import date, timedelta

from app.models.soil_condition import SoilCondition
from app.services.irrigation_service import _needs_watering_with_soil


def test_schedule_watering(plant):
    plant.last_watered = date.today() - timedelta(days=5)

    assert _needs_watering_with_soil(plant, None) is True


def test_no_watering_interval(plant):
    plant.watering_interval_days = None

    assert _needs_watering_with_soil(plant, None) is False


def test_future_last_watered(plant):
    plant.last_watered = date.today() + timedelta(days=5)

    assert _needs_watering_with_soil(plant, None) is False


def test_bulk_watering_updates_plants(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    plant = client.post("/plants/", json={"name": "BulkPlant"}, headers=headers).json()

    client.get("/irrigation/needs-water", headers=headers)

    client.post("/irrigation/water-all", headers=headers)

    plants = client.get("/plants/", headers=headers).json()

    updated = next(p for p in plants if p["id"] == plant["id"])

    assert updated["last_watered"] is not None


def test_sensor_dry(sensor_plant):
    soil = SoilCondition(moisture=10)

    assert _needs_watering_with_soil(sensor_plant, soil) is True


def test_sensor_wet(sensor_plant):
    soil = SoilCondition(moisture=80)

    assert _needs_watering_with_soil(sensor_plant, soil) is False


def test_use_sensor_disabled(plant):
    plant.use_sensor = False
    plant.last_watered = date.today()

    assert _needs_watering_with_soil(plant, None) is False


def test_sensor_enabled_null_moisture(sensor_plant):
    soil = SoilCondition(moisture=None)

    assert _needs_watering_with_soil(sensor_plant, soil) is True


# sensor enabled but no data ever recorded
def test_sensor_enabled_no_data_fallback(sensor_plant):
    assert _needs_watering_with_soil(sensor_plant, None) is True


def test_moisture_exact_threshold(sensor_plant):
    soil = SoilCondition(moisture=30)  # threshold

    assert _needs_watering_with_soil(sensor_plant, soil) is False


def test_irrigation_handles_many_plants(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    for i in range(50):
        client.post("/plants/", json={"name": f"Plant{i}"}, headers=headers)
    response = client.get("/irrigation/needs-water", headers=headers)
    assert response.status_code == 200
