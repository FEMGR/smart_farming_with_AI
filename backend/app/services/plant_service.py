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
from app.services.perenual_service import search_plant_species, get_species_details, get_plant_scientific_name


# ===============================
# CREATE PLANT
# ===============================
def create_plant(db: Session, plant: PlantCreate, user_id: int):

    # Validate location ownership
    if plant.location_id is not None:
        location = db.query(Location).filter(
            Location.id == plant.location_id
        ).first()
        if not location:
            raise NotFoundError("Location not found")
        if location.user_id != user_id:
            raise PermissionDeniedError("Not allowed to use this location")

    # 2. API Integration
    species_name = "Unknown Species"
    watering_days = 30  # Default fallback
    search_results = search_plant_species(plant.name)
    if search_results:
        first_match = search_results[0]
        species_id = first_match.get('id')

        # Extract scientific name (it's usually a list in the search result too)
        sci_names = first_match.get("scientific_name", [])
        species_name = sci_names[0] if sci_names else species_name

        # Get details for watering info
        details = get_species_details(species_id)
        if details:
            watering_text = details.get("watering", "Average")
            # Simple conversion helper (Frequent=3, Average=7, Minimum=14)
            watering_days = convert_watering_to_days(watering_text)
            print(f"DEBUG: Plant Name: {plant.name}")
            print(f"DEBUG: Perenual Watering String: '{watering_text}'")
            print(f"DEBUG: Converted Days: {watering_days}")

    # 3. Create object (Now safe because variables are defined above)
    new_plant = Plant(
        name=plant.name,
        species=species_name,
        location_id=plant.location_id,
        group_id=plant.group_id,
        environment_type=plant.environment_type,
        planting_date=plant.planting_date,
        source=plant.source,
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=watering_days
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)
    return new_plant

def convert_watering_to_days(text: str) -> int:
    mapping = {
        "Frequent": 1,
        "Average": 3,
        "Minimum": 7,
        "None": 30
    }
    return mapping.get(text, 3)

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
