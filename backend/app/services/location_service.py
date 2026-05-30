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

# app.services.location_service.py


from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.location import Location
from app.models.plant import Plant
from app.models.production.farm_section import FarmSection
from app.schemas.location_schema import LocationCreate, LocationUpdate


# ===============================
# CREATE
# ===============================
def create_location(db: Session, location: LocationCreate, user_id: int):
    new_location = Location(
        name=location.name,
        description=location.description,
        environment_type=location.environment_type,
        width_m=location.width_m,
        length_m=location.length_m,
        user_id=user_id,
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
    return db.query(Location).filter(Location.id == location_id, Location.user_id == user_id).first()


def _to_float(value):
    if value is None:
        return None

    return float(value)


def _validate_location_dimensions_for_sections(db: Session, location: Location, width_m, length_m):
    width = _to_float(width_m)
    length = _to_float(length_m)

    if width is None or length is None:
        return

    sections = (
        db.query(FarmSection)
        .filter(
            FarmSection.location_id == location.id,
            FarmSection.user_id == location.user_id,
            FarmSection.is_active.is_(True),
        )
        .all()
    )

    section_area = 0

    for section in sections:
        section_width = _to_float(section.width_m) or 0
        section_length = _to_float(section.length_m) or 0
        section_area += _to_float(section.area_m2) or 0

        if section_width > width or section_length > length:
            raise HTTPException(
                status_code=400,
                detail="Location dimensions cannot be smaller than an existing active section",
            )

    if section_area > width * length:
        raise HTTPException(
            status_code=400,
            detail="Location area cannot be smaller than the total active section area",
        )


# ===============================
# UPDATE
# ===============================
def update_location(db: Session, location_id: int, location_update: LocationUpdate, user_id: int):
    location = db.query(Location).filter(Location.id == location_id, Location.user_id == user_id).first()

    if not location:
        return None

    updates = location_update.model_dump(exclude_unset=True)
    target_width = updates.get("width_m", location.width_m)
    target_length = updates.get("length_m", location.length_m)

    _validate_location_dimensions_for_sections(db, location, target_width, target_length)

    for field, value in updates.items():
        setattr(location, field, value)

    db.commit()
    db.refresh(location)

    return location


# ===============================
# DELETE
# ===============================
def delete_location(db: Session, location_id: int, user_id: int):
    location = db.query(Location).filter(Location.id == location_id, Location.user_id == user_id).first()

    if not location:
        return False

    # Prevent deletion if plants exist
    plant_exists = db.query(Plant).filter(Plant.location_id == location_id).first()

    if plant_exists:
        raise HTTPException(status_code=400, detail="Cannot delete location with existing plants")

    section_exists = (
        db.query(FarmSection)
        .filter(
            FarmSection.location_id == location_id,
            FarmSection.user_id == user_id,
            FarmSection.is_active.is_(True),
        )
        .first()
    )

    if section_exists:
        raise HTTPException(status_code=400, detail="Cannot delete location with existing farm sections")

    db.delete(location)
    db.commit()

    return True
