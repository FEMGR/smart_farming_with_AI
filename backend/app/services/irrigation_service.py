from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.plant import Plant
from app.models.soil_condition import SoilCondition
from app.services import notification_service
from app.models.notification import Notification

# ===============================
# CONFIG (simple thresholds)
# ===============================
MOISTURE_THRESHOLD = 30  # below = dry (you can tune later)


# ===============================
# GET LATEST SOIL DATA
# ===============================
def get_latest_soil_condition(db: Session, plant_id: int):
    return db.query(SoilCondition).filter(
        SoilCondition.plant_id == plant_id
    ).order_by(SoilCondition.recorded_at.desc()).first()


# ===============================
# CHECK IF PLANT NEEDS WATER
# ===============================
def needs_watering(db: Session, plant: Plant) -> bool:
    """
    Hybrid logic:
    - If sensor data exists → use moisture
    - Else → fallback to schedule
    """

    soil = get_latest_soil_condition(db, plant.id)

    # 🌱 SENSOR MODE
    if plant.use_sensor and soil and soil.moisture is not None:

        return float(soil.moisture) < MOISTURE_THRESHOLD

    # 🌱 SCHEDULE MODE (fallback)
    if not plant.watering_interval_days:
        return False

    if not plant.last_watered:
        return True

    next_watering_date = plant.last_watered + timedelta(days=plant.watering_interval_days)

    return date.today() >= next_watering_date


# ===============================
# GET PLANTS NEEDING WATER
# ===============================
def get_plants_needing_water(db: Session, user_id: int):
    plants = db.query(Plant).filter(Plant.user_id == user_id).all()

    result = []

    for plant in plants:
        if needs_watering(db, plant):
            result.append(plant)

            # 🔔 AUTO CREATE NOTIFICATION (no duplicates)
            exists = notification_service.notification_exists_today(
                db, user_id, plant.id
            )

            if not exists:
                message = f"Plant '{plant.name}' needs watering"

                notification_service.create_notification(
                    db=db,
                    user_id=user_id,
                    plant=plant,
                    message=message
                )

    return result


# ===============================
# WATER PLANT
# ===============================
def water_plant(db: Session, plant_id: int, user_id: int):
    plant = db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.user_id == user_id
    ).first()

    if not plant:
        return None

    # ✅ update watering date
    plant.last_watered = date.today()

    # ✅ FIX: mark irrigation notifications as read
    db.query(Notification).filter(
        Notification.plant_id == plant.id,
        Notification.user_id == user_id,
        Notification.type == "irrigation",
        Notification.is_read == False
    ).update({"is_read": True})

    db.commit()
    db.refresh(plant)

    return plant


# ===============================
# BULK WATERING
# ===============================
def water_all_due_plants(db: Session, user_id: int):
    plants = get_plants_needing_water(db, user_id)

    for plant in plants:
        plant.last_watered = date.today()

        db.query(Notification).filter(
            Notification.plant_id == plant.id,
            Notification.user_id == user_id,
            Notification.type == "irrigation",
            Notification.is_read == False
        ).update({"is_read": True})

    db.commit()

    return plants

