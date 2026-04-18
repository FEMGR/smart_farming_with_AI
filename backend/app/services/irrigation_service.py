"""
Service layer for FastAPI (Irrigation).

Key Point:
Handles business logic for irrigation processes.

Responsibilities:
- Determine irrigation needs
- Execute watering logic (manual or automated)
- Update plant or soil conditions
- Trigger related actions (e.g., notifications)

Architecture Role:
- Core logic layer for irrigation system
- Integrates plant data and environmental conditions

Layer Interaction:
- Communicates with: Models (plant, soil_condition), Database
- Called by: Routes, Workers (scheduler)

Data Flow:
Irrigation request or scheduled trigger received
        ↓
Plant and soil data retrieved
        ↓
Irrigation logic evaluated
        ↓
Database updated with results
        ↓
Optional notifications triggered
        ↓
Result returned to caller
"""

#app.services.irrigation_service.py


from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.plant import Plant
from app.models.soil_condition import SoilCondition
from app.services import notification_service
from app.models.notification import Notification

# ===============================
# CONFIG (sample thresholds)
# ===============================
MOISTURE_THRESHOLD = 30  # below = dry


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

    # SENSOR MODE
    if plant.use_sensor and soil and soil.moisture is not None:
        return float(soil.moisture) < MOISTURE_THRESHOLD

    # SCHEDULE MODE (fallback)
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
        # 1. Check if the plant currently needs water
        is_thirsty = needs_watering(db, plant)

        # 2. Check if a notification already exists
        existing_notification = db.query(Notification).filter(
            Notification.plant_id == plant.id,
            Notification.user_id == user_id,
            Notification.type == "irrigation"
        ).first()

        # CASE A: Plant is thirsty but has no notification -> CREATE ONE
        if is_thirsty and not existing_notification:
            notification_service.create_notification(
                db=db,
                user_id=user_id,
                plant=plant,
                message=f"Plant '{plant.name}' needs watering"
            )
            result.append(plant)

        # CASE B: Plant is NOT thirsty but a notification still exists -> DELETE IT
        elif not is_thirsty and existing_notification:
            db.delete(existing_notification)
            db.commit()

        # CASE C: Plant is thirsty and notification exists -> JUST ADD TO RESULT
        elif is_thirsty:
            result.append(plant)

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

    # update watering date
    plant.last_watered = date.today()

    # Find the "unwatered" notification and delete it
    db.query(Notification).filter(
        Notification.plant_id == plant.id,
        Notification.user_id == user_id,
        Notification.type == "irrigation"
    ).delete(synchronize_session=False)

    db.commit()
    db.refresh(plant)
    return plant

# ===============================
# BULK WATERING
# ===============================
def water_all_due_plants(db: Session, user_id: int):
    # This calls your earlier logic that finds thirsty plants
    plants = get_plants_needing_water(db, user_id)

    for plant in plants:
        plant.last_watered = date.today()

        # Delete the active notification for each plant
        db.query(Notification).filter(
            Notification.plant_id == plant.id,
            Notification.user_id == user_id,
            Notification.type == "irrigation"
        ).delete(synchronize_session=False)

    db.commit()
    return plants

