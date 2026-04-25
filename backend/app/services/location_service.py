"""
Service layer for FastAPI (Locations).

Key Point:
Handles business logic for managing plant locations.

Responsibilities:
- Create and manage locations
- Associate plants with locations
- Apply location-based rules

Architecture Role:
- Core logic layer for location management
- Maintains relationship between plants and environments

Layer Interaction:
- Communicates with: Models (location, plant), Database
- Called by: Routes

Data Flow:
Validated location data received from route
        ↓
Business rules applied
        ↓
Location model created or updated
        ↓
Database transaction executed
        ↓
Result returned to route
"""

#app.services.location_service.py


from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.location import Location
from app.models.plant import Plant
from app.schemas.location_schema import LocationCreate, LocationUpdate


# ===============================
# CREATE
# ===============================
def create_location(db: Session, location: LocationCreate, user_id: int):
    new_location = Location(
        name=location.name,
        description=location.description,
        environment_type=location.environment_type,
        user_id=user_id
    )

    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location


# ===============================
# GET ALL
# ===============================
def get_locations(db: Session, user_id: int):
    return db.query(Location).filter(Location.user_id == user_id).all()


# ===============================
# GET ONE
# ===============================
def get_location(db: Session, location_id: int, user_id: int):
    return db.query(Location).filter(
        Location.id == location_id,
        Location.user_id == user_id
    ).first()


# ===============================
# UPDATE
# ===============================
def update_location(db: Session, location_id: int, location_update: LocationUpdate, user_id: int):
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.user_id == user_id
    ).first()

    if not location:
        return None

    for field, value in location_update.dict(exclude_unset=True).items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)

    return location


# ===============================
# DELETE
# ===============================
def delete_location(db: Session, location_id: int, user_id: int):
    location = db.query(Location).filter(
        Location.id == location_id,
        Location.user_id == user_id
    ).first()

    if not location:
        return False

    # Prevent deletion if plants exist
    plant_exists = db.query(Plant).filter(
        Plant.location_id == location_id
    ).first()

    if plant_exists:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete location with existing plants"
        )

    db.delete(location)
    db.commit()

    return True
