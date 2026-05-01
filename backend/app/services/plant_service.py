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

def _detect_species(db: Session, plant_name: str, plant_type: str = None):
    # Pass plant_type to suggestions
    suggestions = suggest_species(db, plant_name, plant_type=plant_type)

    print(f"[DEBUG] Input: {plant_name} (Type: {plant_type})")

    # Pass plant_type to the ranker/matcher
    best_match = select_best_match(plant_name, suggestions, threshold=65, plant_type=plant_type)

    if not best_match:
        print("[AI] No confident match")
        return None

    try:
        species = get_or_create_species_cache(
            db,
            best_match["id"],
            fallback_name=best_match.get("scientific_name")
        )
        print(f"[AI] Linked '{plant_name}' → {species.scientific_name}")
        return species.id
    except Exception as e:
        print(f"[AI] Failed to fetch species: {e}")
        return None

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
    species_id = None
    species_record = None

    # 2. Get suggestions (Pass plant_type for more accurate results)
    suggestions = suggest_species(db, plant.name, plant_type=plant.plant_type)

    # 3. Use select_best_match (This uses your new fuzzy + constraint logic)
    best_match = select_best_match(
        plant.name,
        suggestions,
        threshold=65,
        plant_type=plant.plant_type
    )

    if best_match:
        try:
            # Fetch/Create the species record using the matched ID
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

    # 5. Determine Watering Interval
    user_interval = getattr(plant, "watering_interval_days", None)
    final_interval = (
        user_interval if user_interval else
        (species_record.watering_interval_days if species_record else 4)
    )

    # 6. Save to Database
    new_plant = Plant(
        name=plant.name,
        plant_type=plant.plant_type,
        species_id=species_id,
        location_id=plant.location_id,
        group_id=plant.group_id,
        planting_date=plant.planting_date,
        data_source="perenual" if species_id else "manual",
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days= final_interval
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
    plants = db.query(Plant).options(
        joinedload(Plant.species),
        joinedload(Plant.location)
    ).filter(
        Plant.user_id == user_id
    ).all()

    return [_attach_metadata(p) for p in plants]

# ===============================
# GET PLANT BY ID (USER-SCOPED)
# ===============================
def get_plant(db: Session, plant_id: int, user_id: int):
    plant = db.query(Plant).options(
        joinedload(Plant.species),
        joinedload(Plant.location)
    ).filter(
        Plant.id == plant_id,
        Plant.user_id == user_id
    ).first()

    return _attach_metadata(plant)

# ===============================
# UPDATE PLANT (USER-SCOPED)
# ===============================
def update_plant(db: Session, plant_id: int, plant_update: PlantUpdate, user_id: int):
    plant = db.query(Plant).options(
        joinedload(Plant.species),
        joinedload(Plant.location)
    ).filter(Plant.id == plant_id, Plant.user_id == user_id).first()

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

        new_id = _detect_species(db, search_name, plant_type=search_type)

        if new_id:
            plant.species_id = new_id
            plant.data_source = "perenual"
            # Optional: Sync watering interval if it was using defaults
            species_rec = db.query(PlantSpeciesCache).get(new_id)
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
    plant = db.query(Plant).filter(
        Plant.id == plant_id,
        Plant.user_id == user_id
    ).first()

    if not plant:
        return None

    db.delete(plant)
    db.commit()

    return {"message": "Successfully deleted plant"}

# ===============================
# CREATE PLANT WITH PERENUAL DATA
# ===============================
def create_plant_with_species(db: Session, plant: PlantCreate, user_id: int, species_id: int):
    # Validate location
    _validate_location(db, plant.location_id, user_id)

    # Use cache - passing the schema name as fallback just in case
    species = get_or_create_species_cache(db, species_id, fallback_name=plant.name)

    new_plant = Plant(
        name=plant.name,
        plant_type=plant.plant_type,
        species_id=species.id,
        location_id=plant.location_id,
        group_id=plant.group_id,
        planting_date=plant.planting_date,
        data_source="perenual",
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=species.watering_interval_days,
    )

    db.add(new_plant)
    db.commit()
    db.refresh(new_plant)

    return _attach_metadata(new_plant)

# ===============================
# CREATE SPECIES CACHE
# ===============================
def get_or_create_species_cache(db: Session, species_id: int, fallback_name: str = None) -> PlantSpeciesCache:
    # 1. Check cache
    cached = db.query(PlantSpeciesCache).filter_by(external_species_id=str(species_id)).first()

    # 2. Determine if we need to update (Sync Check)
    # We sync if the record is missing OR if key data is missing (NULL)
    needs_sync = (
            not cached or
            cached.scientific_name == "Unknown Species" or
            cached.is_fruit is None or  # Trigger sync if fruit/veg flags are missing
            cached.watering_interval_days is None
    )

    # If it exists and all key data is present, return it immediately
    if not needs_sync:
        return cached

    # 3. Fetch from API (only reached if needs_sync is True)
    api_data = get_species_details(species_id)

    # 4. Handle API Failure
    if not api_data:
        if cached: return cached  # Keep what we have if API fails

        final_name = fallback_name or "Unknown Species"
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

    # 5. Handle API Success
    print(f"[DEBUG] Syncing/Creating Species: {species_id}")
    enriched = normalize_species_data(api_data)

    # SAFE ASSIGNMENT
    final_scientific = (
            enriched.get("species")
            or (api_data.get("scientific_name")[0] if isinstance(api_data.get("scientific_name"),
                                                                 list) and api_data.get("scientific_name") else None)
            or api_data.get("common_name")
            or "Unknown Species"
    )

    common_name = api_data.get("common_name") or final_scientific

    if cached:
        # UPDATE existing record (Fill in the blanks)
        cached.scientific_name = final_scientific
        cached.common_name = common_name
        cached.is_fruit = enriched.get("is_fruit")  # Updated
        cached.is_veg = enriched.get("is_veg")  # Updated
        cached.is_edible = enriched.get("is_edible")  # Updated
        cached.growth_rate = enriched.get("growth_rate")
        cached.life_cycle = enriched.get("cycle")
        cached.sunlight_requirement = enriched.get("sunlight")
        cached.watering_interval_days = enriched.get("watering_interval_days", 7)
        cached.data = api_data
        new_species = cached
    else:
        # CREATE new record
        new_species = PlantSpeciesCache(
            external_species_id=str(species_id),
            scientific_name=final_scientific,
            common_name=common_name,
            is_fruit=enriched.get("is_fruit"),
            is_veg=enriched.get("is_veg"),
            is_edible=enriched.get("is_edible"),
            growth_rate=enriched.get("growth_rate"),
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

    # Ensure scientific_name is loaded for the return
    _ = new_species.scientific_name
    print(f"[DB] Synced and Verified species: {new_species.scientific_name}")

    return new_species

def cache_species_candidates(db: Session, candidates: list, limit: int = 2):
    """
    Background worker to pre-fill cache for top search results.
    """
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
            # Pass the name as fallback so the cache isn't empty if the details API fails
            get_or_create_species_cache(db, species_id, fallback_name=c.get("scientific_name"))
        except Exception as e:
            print(f"[CACHE] Failed to cache {species_id}: {e}")

# ===============================
# SPECIES SUGGESTION
# ===============================
def suggest_species(db: Session, query: str, plant_type: str = None):
    candidates = []

    # 1. Search Cache
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
                "is_edible": species.is_edible,
                "is_fruit": species.is_fruit,
                "is_veg": species.is_veg,
                "growth_rate": species.growth_rate
            }, "cache")
        )

    # 2. API Results
    api_results = search_species(query)

    for item in api_results:
        # Note: API results won't have 'edible' until we fetch details,
        # but the ranker handles missing keys gracefully.
        candidates.append(
            normalize_candidate({
                "id": item.get("id"),
                "common_name": item.get("common_name"),
                "scientific_name": item.get("scientific_name"),
            }, "api")
        )

    if not candidates:
        return []

    # 3. Rank them (Passing plant_type for the edibility boost)
    ranked = rank_species_matches(query, candidates, plant_type=plant_type)
    print(f"[DEBUG] Input: {query} (Type: {plant_type})")

    return ranked[:5]




