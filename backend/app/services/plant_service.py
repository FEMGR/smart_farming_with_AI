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

# app/services/plant_service.py


from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.logger import setup_logger
from app.models.location import Location
from app.models.plant import Plant
from app.models.plant_species_cache import PlantSpeciesCache
from app.schemas.plant_schema import PlantCreate, PlantUpdate

# Import species-related services from perenual_service
from app.services.perenual_service import (
    get_or_create_species_cache,
    resolve_species,  # This is the main entry for species resolution
)
from app.services.prolog.prolog_service import (
    get_recommendations,
    get_companion_suggestions,
)  # Import get_companion_suggestions
from app.utils.prolog_normalizer import to_prolog_atom

logger = setup_logger()


# ===============================
# HELPERS
# ===============================


def _validate_location(db: Session, location_id: int, user_id: int):
    """Reusable location ownership check."""
    if location_id is None:
        return
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise NotFoundError("Location not found")
    if location.user_id != user_id:
        raise PermissionDeniedError("Not allowed to use this location")


def _attach_metadata(plant: Plant):
    if plant:
        # Relationship name should be 'species'
        # Column name should be 'scientific_name'
        plant.species_name = plant.species.scientific_name if plant.species else "Unknown"

        # Ensure plant_type is never None for the frontend
        if not plant.plant_type:
            plant.plant_type = "vegetable"
    return plant


# ===============================
# CREATE PLANT
# ===============================
def create_plant(db: Session, plant: PlantCreate, user_id: int):
    _validate_location(db, plant.location_id, user_id)

    # 1. Initialize variables
    species_record = None

    # 2. Resolve species using the centralized service
    species_internal_id = resolve_species(db, plant.name, plant_type=plant.plant_type)

    if species_internal_id:
        species_record = db.query(PlantSpeciesCache).get(species_internal_id)
        logger.info(f"[PLANT SERVICE] Linked '{plant.name}' → {species_record.scientific_name} (DB ID: {species_record.id})")
    else:
        logger.info(f"[PLANT SERVICE] No confident species match found for '{plant.name}'.")

    # 3. Determine Watering Interval
    user_interval = getattr(plant, "watering_interval_days", None)
    final_interval = user_interval if user_interval else (species_record.watering_interval_days if species_record else 4)

    # 4. Save to Database
    new_plant = Plant(
        name=plant.name,
        plant_type=plant.plant_type,
        species_id=species_internal_id,
        location_id=plant.location_id,
        group_id=plant.group_id,
        planting_date=plant.planting_date,
        data_source="perenual" if species_internal_id else "manual",
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=final_interval,
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return _attach_metadata(new_plant)


# ===============================
# GET ALL PLANTS (USER-SCOPED)
# ===============================
def get_plants(db: Session, user_id: int):
    # We use joinedload to get species and location in one query
    plants = db.query(Plant).options(joinedload(Plant.species), joinedload(Plant.location)).filter(Plant.user_id == user_id).all()

    return [_attach_metadata(p) for p in plants]


# ===============================
# GET PLANT BY ID (USER-SCOPED)
# ===============================
def get_plant(db: Session, plant_id: int, user_id: int):
    plant = db.query(Plant).options(joinedload(Plant.species), joinedload(Plant.location)).filter(Plant.id == plant_id, Plant.user_id == user_id).first()

    return _attach_metadata(plant)


# ===============================
# UPDATE PLANT (USER-SCOPED)
# ===============================
def update_plant(db: Session, plant_id: int, plant_update: PlantUpdate, user_id: int):
    plant = db.query(Plant).options(joinedload(Plant.species), joinedload(Plant.location)).filter(Plant.id == plant_id, Plant.user_id == user_id).first()

    if not plant:
        return None

    if plant_update.location_id is not None:
        _validate_location(db, plant_update.location_id, user_id)

    update_data = plant_update.dict(exclude_unset=True)

    # --- RE-DETECTION LOGIC ---
    # Trigger if name changes OR if type changes on a manual plant
    name_changed = "name" in update_data and update_data["name"] != plant.name
    type_changed = "plant_type" in update_data and update_data["plant_type"] != plant.plant_type

    if name_changed or (type_changed and plant.data_source == "manual"):
        # Use the NEW name if provided, otherwise the existing name
        search_name = update_data.get("name", plant.name)
        # Use the NEW type if provided, otherwise the existing type
        search_type = update_data.get("plant_type", plant.plant_type)

        new_species_internal_id = resolve_species(db, search_name, plant_type=search_type)

        if new_species_internal_id:
            plant.species_id = new_species_internal_id
            plant.data_source = "perenual"
            # Optional: Sync watering interval if it was using defaults
            species_rec = db.query(PlantSpeciesCache).get(new_species_internal_id)
            if species_rec:
                plant.watering_interval_days = species_rec.watering_interval_days
        else:
            # If name changed to something unmatchable, reset to manual
            plant.species_id = None
            plant.data_source = "manual"

    # Apply other fields
    for field, value in update_data.items():
        setattr(plant, field, value)

    db.commit()
    db.refresh(plant)
    return _attach_metadata(plant)


# ===============================
# DELETE PLANT (USER-SCOPED)
# ===============================
def delete_plant(db: Session, plant_id: int, user_id: int):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == user_id).first()

    if not plant:
        return None

    db.delete(plant)
    db.commit()

    return {"message": "Successfully deleted plant"}


# ===============================
# CREATE PLANT WITH PERENUAL DATA
# ===============================
def create_plant_with_species(db: Session, plant: PlantCreate, user_id: int, external_species_id: int):
    # Validate location
    _validate_location(db, plant.location_id, user_id)

    # Use get_or_create_species_cache from perenual_service
    species_record = get_or_create_species_cache(db, external_species_id, fallback_name=plant.name)

    if not species_record:
        raise NotFoundError("Species not found")

    new_plant = Plant(
        name=plant.name,
        plant_type=plant.plant_type,
        species_id=species_record.id,  # Use the internal ID of the cached species
        location_id=plant.location_id,
        group_id=plant.group_id,
        planting_date=plant.planting_date,
        data_source="perenual",
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=species_record.watering_interval_days,
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return _attach_metadata(new_plant)


# ===============================
# Companion Planting Reccomendation
# ===============================
def get_companion_recommendations(db: Session, user_id: int):

    plants = db.query(Plant).options(joinedload(Plant.species)).filter(Plant.user_id == user_id).all()

    # Normalize and deduplicate plant names for Prolog
    atoms = get_unique_prolog_atoms(plants)

    logger.info(f"[PROLOG INPUT] {atoms}")

    # Get interactions among existing plants
    existing_interactions = get_recommendations(atoms)

    # Get suggestions for new companion plants
    new_suggestions = get_companion_suggestions(atoms)

    # Combine results
    return {"existing_plant_interactions": existing_interactions, "new_companion_suggestions": new_suggestions}


def get_unique_prolog_atoms(plants):
    atoms = set()

    for plant in plants:
        plant_data = {
            "name": plant.name,
            "species": (
                {
                    "common_name": plant.species.common_name if plant.species else None,
                    "scientific_name": plant.species.scientific_name if plant.species else None,
                }
                if plant.species
                else None
            ),
        }

        atom = to_prolog_atom(plant_data)

        if atom:
            atoms.add(atom)

    return list(atoms)
