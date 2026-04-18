"""
Service layer for FastAPI (Plants).

Key Point:
Handles business logic for plant management.

Responsibilities:
- Create, update, delete plants
- Enforce user ownership and access control
- Validate related entities (e.g., location)
- Interact with database models

Architecture Role:
- Core logic layer for plant operations
- Ensures separation between routes and database

Layer Interaction:
- Communicates with: Models (plant, location), Database, Core (exceptions)
- Called by: Routes

Data Flow:
Validated plant data received from route
        ↓
Business rules and ownership checks applied
        ↓
Plant model created, updated, or deleted
        ↓
Database transaction executed
        ↓
Result returned to route
"""


#app.services.plant_service.py


from sqlalchemy.orm import Session
from app.models.plant import Plant
from app.models.location import Location
from app.schemas.plant_schema import PlantCreate, PlantUpdate
from app.core.exceptions import NotFoundError, PermissionDeniedError

# ===============================
# CREATE PLANT
# ===============================
def create_plant(db: Session, plant: PlantCreate, user_id: int):

    # 🔒 Validate location ownership
    if plant.location_id is not None:
        location = db.query(Location).filter(
            Location.id == plant.location_id
        ).first()

        if not location:
            raise NotFoundError("Location not found")

        if location.user_id != user_id:
            raise PermissionDeniedError("Not allowed to use this location")

    new_plant = Plant(
        name=plant.name,
        species=plant.species,
        location_id=plant.location_id,
        group_id=plant.group_id,
        environment_type=plant.environment_type,
        planting_date=plant.planting_date,
        source=plant.source,
        user_id=user_id,
        use_sensor=plant.use_sensor
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return new_plant

# ===============================
# GET ALL PLANTS (USER-SCOPED)
# ===============================
def get_plants(db: Session, user_id: int):
    return db.query(Plant).filter(Plant.user_id == user_id).all()


# ===============================
# GET PLANT BY ID (USER-SCOPED)
# ===============================
def get_plant(db: Session, plant_id: int, user_id: int):
    return db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.user_id == user_id
    ).first()

# ===============================
# UPDATE PLANT (USER-SCOPED)
# ===============================
def update_plant(db: Session, plant_id: int, plant_update: PlantUpdate, user_id: int):

    plant = db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.user_id == user_id
    ).first()

    if not plant:
        return None

    # 🔒 Validate location if updating
    if plant_update.location_id is not None:
        location = db.query(Location).filter(
            Location.id == plant_update.location_id
        ).first()

        if not location:
            raise NotFoundError("Location not found")

        if location.user_id != user_id:
            raise PermissionDeniedError("Not allowed to use this location")

    for field, value in plant_update.dict(exclude_unset=True).items():
        setattr(plant, field, value)

    db.commit()
    db.refresh(plant)

    return plant

# ===============================
# DELETE PLANT (USER-SCOPED)
# ===============================
def delete_plant(db: Session, plant_id: int, user_id: int):
    plant = db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.user_id == user_id
    ).first()

    if not plant:
        return None

    db.delete(plant)
    db.commit()

    return plant
