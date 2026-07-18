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

from app.core.constants import (
    DATA_SOURCE_KNOWLEDGE_BASE,
    DATA_SOURCE_MANUAL,
    DATA_SOURCE_PERENUAL,
)
from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.logger import setup_logger
from app.database.db import sync_postgres_sequence
from app.models.location import Location
from app.models.plant import Plant
from app.models.plant_group import PlantGroup
from app.models.plant_species_cache import PlantSpeciesCache
from app.schemas.plant_schema import PlantCreate, PlantUpdate
from app.services.grouping_service import (
    generate_groups_internal,
    generate_groups_display,
)
from app.services.positioning_service import generate_layout

# Import species-related services from perenual_service
from app.services.perenual_service import (
    correct_species_query,
    get_or_create_species_cache,
    resolve_species,
)
from app.services.lifecycle.plant_timeline_service import save_plant_timeline_snapshot
from app.services.plant_taxonomy_service import PlantIdentity, normalize_plant_input
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


def _ensure_user_group(db: Session, group_id: int | None, user_id: int):
    if group_id is None:
        return None

    group = db.query(PlantGroup).filter(PlantGroup.id == group_id).first()

    if group:
        if group.user_id != user_id:
            raise PermissionDeniedError("Not allowed to use this plant group")
        return group

    group = PlantGroup(id=group_id, user_id=user_id, name=f"Companion Group {group_id}")
    db.add(group)
    db.flush()
    return group


def _sync_plant_id_sequence(db: Session):
    sync_postgres_sequence(db, Plant.__tablename__)


def _attach_metadata(plant: Plant):
    if plant:
        # Relationship name should be 'species'
        # Column name should be 'scientific_name'
        plant.species_name = plant.species.scientific_name if plant.species else "Unknown"

        # Ensure plant_type is never None for the frontend
        if not plant.plant_type:
            plant.plant_type = "vegetable"
    return plant


def _identity_from_plant(plant: Plant) -> PlantIdentity:
    return PlantIdentity(
        plant_atom=plant.plant_atom or to_prolog_atom({"name": plant.name}),
        scientific_name=plant.scientific_name,
        genus=plant.genus,
        family=plant.family,
        taxonomy_confidence=plant.taxonomy_confidence,
    )


def _apply_identity(plant: Plant, identity: PlantIdentity) -> None:
    plant.plant_atom = identity.plant_atom
    plant.scientific_name = identity.scientific_name
    plant.genus = identity.genus
    plant.family = identity.family
    plant.taxonomy_confidence = identity.taxonomy_confidence


def _has_knowledge_base_identity(identity: PlantIdentity) -> bool:
    return bool(identity.scientific_name and identity.taxonomy_confidence and identity.taxonomy_confidence != "user_override")


def _data_source_for_identity(species_internal_id: int | None, identity: PlantIdentity) -> str:
    if species_internal_id:
        return DATA_SOURCE_PERENUAL
    if _has_knowledge_base_identity(identity):
        return DATA_SOURCE_KNOWLEDGE_BASE
    return DATA_SOURCE_MANUAL


def _canonical_scientific_override(value: str | None) -> str | None:
    value = str(value or "").strip()
    if not value:
        return None

    parts = value.split()
    if len(parts) < 2:
        return None

    genus = parts[0].capitalize()
    rest = " ".join(part.lower() if part != "x" else "x" for part in parts[1:])
    return f"{genus} {rest}"


def _identity_for_plant_input(plant_name: str, species_name: str | None = None) -> PlantIdentity:
    base_identity = normalize_plant_input(plant_name)
    scientific_override = _canonical_scientific_override(species_name)

    if not scientific_override:
        return base_identity

    override_identity = normalize_plant_input(scientific_override)
    genus = override_identity.genus or scientific_override.split()[0].lower()

    return PlantIdentity(
        plant_atom=base_identity.plant_atom,
        scientific_name=scientific_override,
        alternate_scientific_names=override_identity.alternate_scientific_names or base_identity.alternate_scientific_names,
        genus=genus,
        family=override_identity.family or base_identity.family,
        taxonomy_confidence="user_override",
        taxonomy_source=override_identity.taxonomy_source or base_identity.taxonomy_source,
        taxonomy_note=override_identity.taxonomy_note or base_identity.taxonomy_note,
    )


def _preferred_scientific_names(identity: PlantIdentity) -> list[str]:
    names = [identity.scientific_name, *(identity.alternate_scientific_names or [])]
    result: list[str] = []
    seen: set[str] = set()
    for name in names:
        name = str(name or "").strip()
        key = name.lower()
        if name and key not in seen:
            result.append(name)
            seen.add(key)
    return result


def _preferred_common_names(*names: str | None) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for name in names:
        name = str(name or "").strip()
        key = name.lower()
        if name and key not in seen:
            result.append(name)
            seen.add(key)
    return result


def _identity_from_species_record(species_record: PlantSpeciesCache, fallback_name: str) -> PlantIdentity:
    data = species_record.data or {}
    common_name = species_record.common_name or fallback_name
    scientific_name = species_record.scientific_name
    genus = data.get("genus")
    family = data.get("family")

    if not genus and scientific_name:
        genus = scientific_name.split()[0]

    base_identity = normalize_plant_input(common_name)
    return PlantIdentity(
        plant_atom=base_identity.plant_atom,
        scientific_name=scientific_name or base_identity.scientific_name,
        alternate_scientific_names=base_identity.alternate_scientific_names,
        genus=genus or base_identity.genus,
        family=family,
        taxonomy_confidence="perenual_selected",
        taxonomy_source=base_identity.taxonomy_source,
        taxonomy_note=base_identity.taxonomy_note,
    )


# ===============================
# CREATE PLANT
# ===============================
def create_plant(db: Session, plant: PlantCreate, user_id: int):
    _validate_location(db, plant.location_id, user_id)
    _ensure_user_group(db, plant.group_id, user_id)

    stored_name = correct_species_query(plant.name) or plant.name
    if stored_name != plant.name:
        logger.info("[PLANT SERVICE] Corrected plant name '%s' -> '%s' before storing.", plant.name, stored_name)

    identity = _identity_for_plant_input(stored_name, plant.species_name)

    # 1. Initialize variables
    species_record = None

    # 2. Resolve species from the user-entered name.
    species_internal_id = resolve_species(
        db,
        stored_name,
        plant_type=plant.plant_type,
        preferred_scientific_names=_preferred_scientific_names(identity),
        preferred_common_names=_preferred_common_names(stored_name, plant.name),
        preferred_genus=identity.genus,
        preferred_family=identity.family,
    )

    if species_internal_id:
        species_record = db.query(PlantSpeciesCache).get(species_internal_id)
        identity = _identity_from_species_record(species_record, stored_name)
        logger.info(f"[PLANT SERVICE] Linked '{stored_name}' → {species_record.scientific_name} (DB ID: {species_record.id})")
    elif identity.scientific_name:
        logger.info(
            "[PLANT SERVICE] No Perenual detail cache linked for '%s'; using normalized taxonomy identity %s.",
            stored_name,
            identity.scientific_name,
        )
    else:
        logger.info(f"[PLANT SERVICE] No confident species match found for '{stored_name}'.")

    # 3. Determine Watering Interval
    user_interval = getattr(plant, "watering_interval_days", None)
    final_interval = user_interval if user_interval else (species_record.watering_interval_days if species_record else 4)

    # 4. Save to Database
    new_plant = Plant(
        name=stored_name,
        plant_type=plant.plant_type,
        species_id=species_internal_id,
        location_id=plant.location_id,
        group_id=plant.group_id,
        bed_x=plant.bed_x,
        bed_y=plant.bed_y,
        planting_date=plant.planting_date,
        data_source=_data_source_for_identity(species_internal_id, identity),
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=final_interval,
    )
    _apply_identity(new_plant, identity)

    _sync_plant_id_sequence(db)
    db.add(new_plant)
    db.flush()
    save_plant_timeline_snapshot(db, new_plant, identity)
    db.commit()
    db.refresh(new_plant)

    return _attach_metadata(new_plant)


# ===============================
# GET ALL PLANTS (USER-SCOPED)
# ===============================
def get_plants(db: Session, user_id: int):
    # We use joinedload to get species and location in one query
    plants = (
        db.query(Plant)
        .options(joinedload(Plant.species), joinedload(Plant.location), joinedload(Plant.timeline_snapshots))
        .filter(Plant.user_id == user_id)
        .all()
    )

    return [_attach_metadata(p) for p in plants]


# ===============================
# GET PLANT BY ID (USER-SCOPED)
# ===============================
def get_plant(db: Session, plant_id: int, user_id: int):
    plant = (
        db.query(Plant)
        .options(joinedload(Plant.species), joinedload(Plant.location), joinedload(Plant.timeline_snapshots))
        .filter(Plant.id == plant_id, Plant.user_id == user_id)
        .first()
    )

    return _attach_metadata(plant)


# ===============================
# DUPLICATE PLANT (USER-SCOPED)
# ===============================
def duplicate_plant(db: Session, plant_id: int, user_id: int, group_id: int | None = None):
    plant = db.query(Plant).filter(Plant.id == plant_id, Plant.user_id == user_id).first()

    if not plant:
        return None

    target_group_id = plant.group_id if group_id is None else group_id
    _ensure_user_group(db, target_group_id, user_id)

    duplicate = Plant(
        name=plant.name,
        plant_type=plant.plant_type,
        species_id=plant.species_id,
        location_id=plant.location_id,
        group_id=target_group_id,
        bed_x=None,
        bed_y=None,
        planting_date=plant.planting_date,
        data_source=plant.data_source,
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=plant.watering_interval_days,
    )
    _apply_identity(duplicate, _identity_from_plant(plant))

    _sync_plant_id_sequence(db)
    db.add(duplicate)
    db.flush()
    save_plant_timeline_snapshot(db, duplicate, _identity_from_plant(duplicate))
    db.commit()
    db.refresh(duplicate)

    return _attach_metadata(duplicate)


# ===============================
# UPDATE PLANT (USER-SCOPED)
# ===============================
def update_plant(db: Session, plant_id: int, plant_update: PlantUpdate, user_id: int):
    plant = (
        db.query(Plant)
        .options(joinedload(Plant.species), joinedload(Plant.location), joinedload(Plant.timeline_snapshots))
        .filter(Plant.id == plant_id, Plant.user_id == user_id)
        .first()
    )

    if not plant:
        return None

    if plant_update.location_id is not None:
        _validate_location(db, plant_update.location_id, user_id)

    update_data = plant_update.dict(exclude_unset=True)
    species_name_supplied = "species_name" in update_data or "scientific_name" in update_data
    species_name_override = update_data.pop("species_name", None)
    scientific_name_override = update_data.pop("scientific_name", None)
    species_name_override = species_name_override if species_name_override is not None else scientific_name_override
    canonical_species_override = _canonical_scientific_override(species_name_override)
    current_scientific_name = _canonical_scientific_override(plant.scientific_name) or plant.scientific_name
    species_name_changed = species_name_supplied and (canonical_species_override or "") != (current_scientific_name or "")
    layout_fields = {"group_id", "bed_x", "bed_y"}
    logs_layout_update = bool(layout_fields.intersection(update_data))

    if logs_layout_update:
        logger.info(
            "plant_service.update_plant.layout_request plant_id=%s user_id=%s " "payload=%s before=%s",
            plant_id,
            user_id,
            {field: update_data.get(field) for field in sorted(layout_fields) if field in update_data},
            {
                "group_id": plant.group_id,
                "bed_x": plant.bed_x,
                "bed_y": plant.bed_y,
            },
        )

    if "group_id" in update_data:
        _ensure_user_group(db, update_data["group_id"], user_id)

    # --- RE-DETECTION LOGIC ---
    # Trigger if name changes OR if type changes on a manual plant
    name_changed = "name" in update_data and update_data["name"] != plant.name
    type_changed = "plant_type" in update_data and update_data["plant_type"] != plant.plant_type

    if name_changed or species_name_changed or (type_changed and plant.data_source == "manual"):
        # Use the NEW name if provided, otherwise the existing name
        raw_search_name = update_data.get("name", plant.name)
        search_name = correct_species_query(raw_search_name) or raw_search_name
        if search_name != raw_search_name:
            logger.info("[PLANT SERVICE] Corrected plant name '%s' -> '%s' before storing.", raw_search_name, search_name)
            update_data["name"] = search_name
        # Use the NEW type if provided, otherwise the existing type
        search_type = update_data.get("plant_type", plant.plant_type)
        identity = _identity_for_plant_input(search_name, species_name_override)
        logger.info(
            "plant_service.update_plant.identity_request plant_id=%s "
            "species_name_supplied=%s species_name_override=%s current_scientific=%s "
            "identity=%s perenual_query=%s",
            plant_id,
            species_name_supplied,
            species_name_override,
            plant.scientific_name,
            identity.as_dict(),
            search_name,
        )

        new_species_internal_id = resolve_species(
            db,
            search_name,
            plant_type=search_type,
            force_refresh=True,
            preferred_scientific_names=_preferred_scientific_names(identity),
            preferred_common_names=_preferred_common_names(search_name, raw_search_name),
            preferred_genus=identity.genus,
            preferred_family=identity.family,
        )
        _apply_identity(plant, identity)

        if new_species_internal_id:
            plant.species_id = new_species_internal_id
            plant.data_source = DATA_SOURCE_PERENUAL
            # Optional: Sync watering interval if it was using defaults
            species_rec = db.query(PlantSpeciesCache).get(new_species_internal_id)
            if species_rec:
                plant.watering_interval_days = species_rec.watering_interval_days
        else:
            if identity.scientific_name:
                logger.info(
                    "[PLANT SERVICE] No Perenual detail cache linked for updated plant '%s'; keeping normalized taxonomy identity %s.",
                    search_name,
                    identity.scientific_name,
                )
            plant.species_id = None
            plant.data_source = _data_source_for_identity(None, identity)

    # Apply other fields
    for field, value in update_data.items():
        setattr(plant, field, value)

    if name_changed or species_name_changed or "planting_date" in update_data:
        save_plant_timeline_snapshot(db, plant, _identity_from_plant(plant))

    db.commit()
    db.refresh(plant)

    if logs_layout_update:
        logger.info(
            "plant_service.update_plant.layout_response plant_id=%s user_id=%s after=%s",
            plant_id,
            user_id,
            {
                "group_id": plant.group_id,
                "bed_x": plant.bed_x,
                "bed_y": plant.bed_y,
            },
        )

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
    _ensure_user_group(db, plant.group_id, user_id)

    # Use get_or_create_species_cache from perenual_service
    species_record = get_or_create_species_cache(db, external_species_id, fallback_name=plant.name)

    if not species_record:
        raise NotFoundError("Species not found")

    stored_name = species_record.common_name or plant.name
    identity = _identity_from_species_record(species_record, stored_name)
    logger.info(
        "[PLANT SERVICE] Using selected species for plant name/identity: input_name=%s stored_name=%s scientific=%s genus=%s family=%s.",
        plant.name,
        stored_name,
        identity.scientific_name,
        identity.genus,
        identity.family,
    )

    new_plant = Plant(
        name=stored_name,
        plant_type=plant.plant_type,
        species_id=species_record.id,  # Use the internal ID of the cached species
        location_id=plant.location_id,
        group_id=plant.group_id,
        bed_x=plant.bed_x,
        bed_y=plant.bed_y,
        planting_date=plant.planting_date,
        data_source=DATA_SOURCE_PERENUAL,
        user_id=user_id,
        use_sensor=plant.use_sensor,
        watering_interval_days=species_record.watering_interval_days,
    )
    _apply_identity(new_plant, identity)

    _sync_plant_id_sequence(db)
    db.add(new_plant)
    db.flush()
    save_plant_timeline_snapshot(db, new_plant, identity)
    db.commit()
    db.refresh(new_plant)

    return _attach_metadata(new_plant)


# ===============================
# Companion Planting Reccomendation
# ===============================
def get_companion_recommendations(db: Session, user_id: int):

    plants = db.query(Plant).options(joinedload(Plant.species), joinedload(Plant.location)).filter(Plant.user_id == user_id).all()

    # Normalize and deduplicate plant names for Prolog
    atoms = get_unique_prolog_atoms(plants)

    logger.info(f"[PROLOG INPUT] {atoms}")

    # Get interactions among existing plants
    existing_interactions = get_recommendations(atoms)

    recommended_items = existing_interactions.get("recommended", [])
    avoid_items = existing_interactions.get("avoid", [])

    recommended_pairs = [item["pair"] for item in recommended_items]
    avoid_pairs = [item["pair"] for item in avoid_items]

    filtered_pairs = [pair for pair in recommended_pairs if pair not in avoid_pairs and "-".join(pair.split("-")[::-1]) not in avoid_pairs]

    filtered_recommended_items = [item for item in recommended_items if item["pair"] in filtered_pairs]

    pair_reasons = {item["pair"]: item for item in filtered_recommended_items}

    groups_internal = generate_groups_internal(
        plants=plants,
        valid_pairs=filtered_pairs,
        avoid_pairs=avoid_pairs,
    )

    groups_display = generate_groups_display(
        plants=plants,
        valid_pairs=filtered_pairs,
        avoid_pairs=avoid_pairs,
        pair_reasons=pair_reasons,
    )

    layout = generate_layout(
        groups=groups_internal,
        recommended_pairs=filtered_pairs,
        avoid_pairs=avoid_pairs,
        grid_width=10,
        grid_height=10,
    )

    existing_interactions["recommended"] = filtered_recommended_items
    existing_interactions["avoid"] = avoid_items

    new_suggestions = get_companion_suggestions(atoms)

    return {
        "existing_plant_interactions": existing_interactions,
        "groups": groups_display,
        "layout": layout,
        "new_companion_suggestions": new_suggestions,
    }


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
