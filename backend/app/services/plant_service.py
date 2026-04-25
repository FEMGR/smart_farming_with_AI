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


from sqlalchemy.orm import Session,joinedload
from app.models.plant import Plant
from app.models.location import Location
from app.schemas.plant_schema import PlantCreate, PlantUpdate
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.plant_species_cache import PlantSpeciesCache
from app.integrations.perenual_api import get_species_details, normalize_species_data, search_species
from app.utils.species_matching import select_best_match, rank_species_matches, normalize_candidate



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

def _detect_species(db: Session, plant_name: str):
    suggestions = suggest_species(db, plant_name)

    print(f"[DEBUG] Input: {plant_name}")
    print(f"[DEBUG] Suggestions: {suggestions[:3]}")

    best_match = select_best_match(plant_name, suggestions, threshold=65)

    if not best_match:
        print("[AI] No confident match")
        return None

    try:
        species = get_or_create_species_cache(db, best_match["id"])
        print(f"[AI] Linked '{plant_name}' → {species.scientific_name} (score={best_match['score']})")
        return species.id
    except Exception as e:
        print(f"[AI] Failed to fetch species: {e}")
        return None

def _attach_metadata(plant: Plant):
    """Helper to fill species_name from the linked species object."""
    if plant and plant.species:
        plant.species_name = plant.species.scientific_name
    else:
        plant.species_name = "Unknown"
    return plant

# ===============================
# CREATE PLANT
# ===============================
def create_plant(db: Session, plant: PlantCreate, user_id: int):
    _validate_location(db, plant.location_id, user_id)

    # 1. Initialize variables
    species_id = None
    species_record = None  # <--- Crucial fix: initialize this!

    # 2. Get suggestions
    suggestions = suggest_species(db, plant.name)
    best_match = suggestions[0] if suggestions else None

    # 3. Process the best match
    if best_match and best_match.get("score", 0) >= 65:
        try:
            species_record = get_or_create_species_cache(
                db,
                best_match["id"],
                fallback_name=best_match.get("scientific_name")
            )
            if species_record:
                db.refresh(species_record)
                species_id = species_record.id
                print(f"[AI] Linked '{plant.name}' → {species_record.scientific_name} (DB ID: {species_record.id})")
        except Exception as e:
            print(f"[AI] Failed to fetch species: {e}")

    # 4. Fallback: If AI failed, try your local detector
    if not species_id:
        species_id = _detect_species(db, plant.name)

    # 5. Create plant
    # LOGIC: Use user input if they provided a specific value,
    # otherwise use the AI/Cache value, otherwise default to 7.
    user_interval = getattr(plant, "watering_interval_days", None)

    final_interval = (
        user_interval if user_interval else
        (species_record.watering_interval_days if species_record else 4)
    )

    new_plant = Plant(
        name=plant.name,
        species_id=species_id,
        location_id=plant.location_id,
        group_id=plant.group_id,
        environment_type=plant.environment_type,
        planting_date=plant.planting_date,
        data_source="perenual" if species_id else "manual",
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=final_interval
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return _attach_metadata(new_plant)

# ===============================
# GET ALL PLANTS (USER-SCOPED)
# ===============================
def get_plants(db: Session, user_id: int):
    plants = db.query(Plant).options(
        joinedload(Plant.species)
    ).filter(
        Plant.user_id == user_id
    ).all()

    for plant in plants:
        plant.species_name = (
            plant.species.scientific_name
            if plant.species else None
        )

    return plants

# ===============================
# GET PLANT BY ID (USER-SCOPED)
# ===============================
def get_plant(db: Session, plant_id: int, user_id: int):
    plant = db.query(Plant).options(
        joinedload(Plant.species)
    ).filter(
        Plant.id == plant_id,
        Plant.user_id == user_id
    ).first()

    if plant:
        plant.species_name = (
            plant.species.scientific_name
            if plant.species else None
        )

    return plant

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

    # Validate location if updating
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

# ===============================
# CREATE PLANT WITH PERENUAL DATA
# ===============================
def create_plant_with_species(db: Session, plant: PlantCreate, user_id: int, species_id: int):
    """
    Create plant using species cache (avoids duplicate API calls).
    """
    # Validate location
    if plant.location_id is not None:
        location = db.query(Location).filter(
            Location.id == plant.location_id
        ).first()
        if not location:
            raise NotFoundError("Location not found")
        if location.user_id != user_id:
            raise PermissionDeniedError("Not allowed to use this location")

    # use cache when available
    species = get_or_create_species_cache(db, species_id)

    # Create new plant
    new_plant = Plant(
        name=plant.name,
        # LINK instead of duplicate
        species_id=species.id,
        location_id=plant.location_id,
        group_id=plant.group_id,
        environment_type=plant.environment_type,
        planting_date=plant.planting_date,
        data_source="perenual",
        user_id=user_id,
        use_sensor=plant.use_sensor,
        # fallback (temporary)
        watering_interval_days=species.watering_interval_days,
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return new_plant

# ===============================
# CREATE SPECIES CACHE
# ===============================
# 1. Added 'fallback_name=None' to the function signature below:
def get_or_create_species_cache(db: Session, species_id: int, fallback_name: str = None) -> PlantSpeciesCache:
    # 1. Check cache
    cached = db.query(PlantSpeciesCache).filter(
        PlantSpeciesCache.external_species_id == str(species_id)
    ).first()

    # If found and it has a real name, return it
    if cached and cached.scientific_name and cached.scientific_name != "Unknown Species":
        return cached

    # 2. Fetch from API
    api_data = get_species_details(species_id)
    print(f"API_data: {api_data}")
    # 3. Handle API Failure (Use the fallback name provided)
    if not api_data:
        print(f"[WARN] No API data for species_id={species_id}. Using fallback: {fallback_name}")

        final_name = fallback_name or "Unknown Species"

        # If a "broken" record already exists in DB, update it instead of creating a new one
        if cached:
            cached.scientific_name = final_name
            cached.common_name = final_name
            db.commit()
            db.refresh(cached)
            return cached

        # Otherwise, create a new record
        new_species = PlantSpeciesCache(
            external_species_id=str(species_id),
            scientific_name=final_name,
            common_name=final_name,
            watering_interval_days=7
        )
        db.add(new_species)
        db.commit()
        db.refresh(new_species)
        return new_species

    # 4. Handle API Success (Normal logic)
    print("[DEBUG] RAW API DATA:", api_data)
    enriched = normalize_species_data(api_data)

    # SAFE ASSIGNMENT
    final_scientific = (
            enriched.get("species")
            or (api_data.get("scientific_name")[0]
                if isinstance(api_data.get("scientific_name"),list)
                   and api_data.get("scientific_name") else None)
            or api_data.get("common_name")
            or "Unknown Species"
    )
    common_name = (
            api_data.get("common_name")
            or enriched.get("species")
            or final_scientific
    )

    if cached:
        # Update existing broken record
        cached.scientific_name = final_scientific
        cached.common_name = api_data.get("common_name") or final_scientific
        cached.life_cycle = enriched.get("cycle")
        cached.sunlight_requirement = enriched.get("sunlight")
        cached.watering_interval_days = enriched.get("watering_interval_days", 7)
        cached.data = api_data
        new_species = cached
    else:
        # Create new record
        new_species = PlantSpeciesCache(
            external_species_id=str(species_id),

            scientific_name=final_scientific,
            common_name=common_name,

            life_cycle=enriched.get("cycle"),
            sunlight_requirement=enriched.get("sunlight"),
            watering_interval_days=enriched.get("watering_interval_days", 4),
            recommended_soil=enriched.get("soil"),
            propagation_method=enriched.get("propagation"),
            pest_susceptibility=enriched.get("pest_susceptibility"),
            data=api_data
        )
        db.add(new_species)

    db.commit()
    db.refresh(new_species)

    # Touch attribute to ensure it's loaded
    _ = new_species.scientific_name
    print(f"[DB] Saved and Verified species: {new_species.scientific_name}")

    return new_species


# ===============================
# SPECIES SUGGESTION
# ===============================
def suggest_species(db: Session, query: str):
    candidates = []

    # 1. ONLY fetch from cache if the name matches the query (Don't use .all()!)
    # This prevents 'Cucumber' from being a candidate for 'Nasturtium'
    search_query = f"%{query}%"
    cached_matches = db.query(PlantSpeciesCache).filter(
        (PlantSpeciesCache.common_name.ilike(search_query)) |
        (PlantSpeciesCache.scientific_name.ilike(search_query))
    ).all()

    for species in cached_matches:
        candidates.append(
            normalize_candidate({
                "id": int(species.external_species_id),
                "common_name": species.common_name,
                "scientific_name": species.scientific_name,
            }, "cache")
        )

    # 2. API Results (These are usually the most accurate for new plants)
    api_results = search_species(query)

    for item in api_results:
        candidates.append(
            normalize_candidate({
                "id": item.get("id"),
                "common_name": item.get("common_name"),
                "scientific_name": item.get("scientific_name"),
            }, "api")
        )

    if not candidates:
        return []

    # 3. Rank them
    ranked = rank_species_matches(query, candidates)

    # 4. CRITICAL: If an API result has a much higher score than a cache result,
    # make sure it stays at the top.
    return ranked[:5]


def cache_species_candidates(db: Session, candidates: list, limit: int = 2):
    for c in candidates[:limit]:
        species_id = c.get("id")
        if not species_id:
            continue

        exists = db.query(PlantSpeciesCache).filter(
            PlantSpeciesCache.external_species_id == str(species_id)
        ).first()

        if exists:
            continue

        try:
            print(f"[CACHE] Saving species_id={species_id}")
            get_or_create_species_cache(db, species_id)
        except Exception as e:
            print(f"[CACHE] Failed to cache {species_id}: {e}")

