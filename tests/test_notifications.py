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
