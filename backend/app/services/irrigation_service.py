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
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from app.models.soil_condition import SoilCondition
from app.services import notification_service
from app.models.notification import Notification
from app.models.plant import Plant

# ===============================
# CONFIG (sample thresholds)
# ===============================
MOISTURE_THRESHOLD = 30  # below = dry

def _get_thirsty_plants(db: Session, user_id: int):
    plants = db.query(Plant).filter(Plant.user_id == user_id).all()
    plant_ids = [p.id for p in plants]

    if not plant_ids:
        return []

    # Subquery: get latest timestamp per plant
    subquery = db.query(
        SoilCondition.plant_id,
        func.max(SoilCondition.recorded_at).label("max_time")
    ).filter(
        SoilCondition.plant_id.in_(plant_ids)
    ).group_by(SoilCondition.plant_id).subquery()

    # Join to get full row of latest soil condition
    latest_soils = db.query(SoilCondition).join(
        subquery,
        and_(
            SoilCondition.plant_id == subquery.c.plant_id,
            SoilCondition.recorded_at == subquery.c.max_time
        )
    ).all()

    # Build lookup map
    soil_map = {s.plant_id: s for s in latest_soils}

    # Filter thirsty plants using preloaded soil data
    result = []

    for plant in plants:
        soil = soil_map.get(plant.id)

        if _needs_watering_with_soil(plant, soil):
            result.append(plant)

    return result

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
def _needs_watering_with_soil(plant: Plant, soil: SoilCondition | None) -> bool:
    # SENSOR MODE
    if plant.use_sensor and soil and soil.moisture is not None:
        return float(soil.moisture) < MOISTURE_THRESHOLD

    # SCHEDULE MODE
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
    thirsty_plants = _get_thirsty_plants(db, user_id)
    plant_ids = [p.id for p in thirsty_plants]

    existing_notifications = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.type == "irrigation",
        Notification.plant_id.in_(plant_ids)
    ).all()
    notification_map = {n.plant_id: n for n in existing_notifications}

    result = []

    for plant in thirsty_plants:
        existing_notification = notification_map.get(plant.id)
        print(f"Processing plant {plant.id}")

        if not existing_notification:
            notification_service.create_notification(
                db=db,
                user_id=user_id,
                plant=plant,
                message=f"Plant '{plant.name}' needs watering"
            )

        result.append({
            "plant_id": plant.id,
            "name": plant.name,
            "last_watered": plant.last_watered,
            "watering_interval_days": plant.watering_interval_days,
            "use_sensor": plant.use_sensor,
            "needs_water": True
        })
    db.commit()
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
    plants = _get_thirsty_plants(db, user_id)

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

