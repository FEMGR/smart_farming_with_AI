# tests/test_notification.py

from datetime import date, timedelta

from app.services.irrigation_service import get_plants_needing_water


def test_notification_created(db, plant):
    plant.last_watered = date.today() - timedelta(days=5)
    db.commit()

    result = get_plants_needing_water(db, plant.user_id)

    assert len(result) == 1


def test_notification_not_duplicated(db, plant):
    plant.last_watered = date.today() - timedelta(days=5)
    db.commit()

    first = get_plants_needing_water(db, plant.user_id)
    second = get_plants_needing_water(db, plant.user_id)

    assert len(first) == len(second)


def test_notification_created_for_thirsty_plant(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    # Create plant that needs water
    client.post("/plants/", json={"name": "DryPlant"}, headers=headers)

    client.get("/irrigation/needs-water", headers=headers)

    notif = client.get("/notifications", headers=headers).json()

    assert any("needs watering" in n["message"] for n in notif)

def test_notification_removed_after_watering(client, token):
    headers = {"Authorization": f"Bearer {token}"}

    plant = client.post("/plants/", json={"name": "DryPlant"}, headers=headers).json()

    client.get("/irrigation/needs-water", headers=headers)

    client.post(f"/irrigation/water/{plant['id']}", headers=headers)

    notif = client.get("/notifications", headers=headers).json()

    assert not any(n["plant_id"] == plant["id"] for n in notif)
