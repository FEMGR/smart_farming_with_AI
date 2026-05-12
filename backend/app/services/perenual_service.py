"""
Service layer for external API integration (Perenual) and Species Management.

Key Point:
Consolidates all logic for interacting with the Perenual API, managing in-memory
and database caching of species data, and providing species resolution/suggestions.

Responsibilities:
- Manage API key and base URL
- Implement rate limiting/cooldown for API calls
- Provide in-memory caching for raw API responses
- Search for plant species by query
- Fetch detailed information for a specific species ID
- Normalize raw API data into a consistent internal format
- Manage persistent caching of species data in the database (PlantSpeciesCache)
- Provide species suggestion and resolution logic for other services

Architecture Role:
- Centralized species data provider and manager
- Shields other services from direct API interaction details and caching complexities

Layer Interaction:
- Communicates with: External Perenual API, Database (PlantSpeciesCache)
- Used by: Services (plant_service), Routes (species routes)

Data Flow:
User or system requests species data
        ↓
API request sent to Perenual
        ↓
Response received and parsed
        ↓
Data normalized and enriched (placeholders added)
        ↓
Returned to calling service or utility
"""

#app/services/perenual_service.py

import requests
import os
import time
from typing import List, Any, Dict, Tuple
from sqlalchemy.orm import Session

from app.core.config import PERENUAL_API_KEY
from app.core.constants import COOLDOWN_SECONDS, DEFAULT_TTL, MAX_CACHE_SIZE, API_REQUEST_TIMEOUT_SECONDS
from app.core.logger import setup_logger
from app.models.plant_species_cache import PlantSpeciesCache
from app.utils.species_matching import (
    select_best_match,
    rank_species_matches,
    normalize_candidate
)
from app.services.species_snapshot_service import (
    save_species_snapshot,
    load_species_snapshot
)
from app.services.species_suggestion_cache_service import (
    cache_species_suggestions,
    get_cached_species_suggestions
)

logger = setup_logger()
BASE_URL = "https://perenual.com/api/v2"


# ===============================
# SIMPLE IN-MEMORY CACHE (for raw API responses)
# ===============================

CACHE: Dict[str, Tuple[float, Any]] = {}


def _get_cache(key: str):
    """Retrieve cached value if not expired."""
    if key in CACHE:
        expiry, value = CACHE[key]

        if time.time() < expiry:
            logger.info(f"[IN-MEMORY CACHE HIT] {key}")
            return value

        # Expired → delete
        del CACHE[key]
        logger.info(f"[IN-MEMORY CACHE EXPIRED] {key}")

    return None

def _set_cache(key: str, value: Any, ttl: int = DEFAULT_TTL):
    if len(CACHE) > MAX_CACHE_SIZE:
        logger.warning(f"[IN-MEMORY CACHE] Max cache size ({MAX_CACHE_SIZE}) reached. Clearing cache.")
        CACHE.clear()  # simple reset strategy

    expiry = time.time() + ttl
    CACHE[key] = (expiry, value)
    logger.info(f"[IN-MEMORY CACHE SET] {key}")


# Using a simple global variable for last API call timestamp
_last_api_call_time = 0


# =====================================
# SAFE FLOAT PARSER
# =====================================

def safe_float(value):

    if value is None:
        return None

    try:
        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).strip()

        # Handle ranges like "12-24"
        if "-" in value:
            value = value.split("-")[0].strip()

        return float(value)

    except (ValueError, TypeError):
        return None

# =========================================
# EXTERNAL API CALLS (Perenual)
# =========================================
def _make_api_call_with_cooldown(
    url: str,
    params: Dict,
    cache_key: str = None
) -> Dict | List:
    """Handles API call with global cooldown and in-memory caching."""
    global _last_api_call_time

    # =====================================
    # CHECK CACHE FIRST
    # =====================================

    if cache_key:
        cached = _get_cache(cache_key)

        if cached is not None:
            return cached

    # =====================================
    # COOLDOWN - WAIT INSTEAD OF SKIP
    # =====================================

    now = time.time()
    time_since_last_call = now - _last_api_call_time

    if time_since_last_call < COOLDOWN_SECONDS:
        wait_time = COOLDOWN_SECONDS - time_since_last_call
        logger.info(
            f"[PERENUAL API] Cooldown active. Waiting {wait_time:.2f}s before calling {url}"
        )
        time.sleep(wait_time)
        now = time.time() # Update now after waiting

    _last_api_call_time = now

    # =====================================
    # REAL API CALL
    # =====================================

    logger.info(f"[PERENUAL API] Querying external API: {url}")

    try:
        response = requests.get(url, params=params, timeout=API_REQUEST_TIMEOUT_SECONDS)

        if response.status_code != 200:
            logger.error(
                f"[PERENUAL API] Call failed "
                f"with status={response.status_code} "
                f"for {url}"
            )

            return {} if "details" in url else []

        data = response.json()

        if cache_key:
            _set_cache(cache_key, data)

        return data

    except requests.exceptions.Timeout:

        logger.error(
            f"[PERENUAL API] Timeout during API call to {url}"
        )

        return {} if "details" in url else []

    except requests.exceptions.RequestException as e:

        logger.error(
            f"[PERENUAL API] Request error during API call "
            f"to {url}: {e}"
        )

        return {} if "details" in url else []

    except Exception as e:

        logger.error(
            f"[PERENUAL API] Unexpected error "
            f"during API call to {url}: {e}"
        )

        return {} if "details" in url else []


def search_plant_species_api(query: str, limit: int = 5) -> List[Dict]:
    """
    Search plant species by name from Perenual API.
    Returns a list of basic species dicts.
    """
    url = f"{BASE_URL}/species-list"
    params = {"key": PERENUAL_API_KEY, "q": query}
    cache_key = f"search:{query}:{limit}"

    api_response = _make_api_call_with_cooldown(url, params, cache_key)

    if not api_response:
        return []

    data = api_response.get("data", [])
    logger.info(f"[PERENUAL API] Search for '{query}' returned {len(data)} results.")

    results = []
    for plant in data[:limit]:
        scientific_names = plant.get("scientific_name", [])
        results.append({
            "id": plant.get("id"),
            "common_name": plant.get("common_name", "Unknown"),
            "scientific_name": scientific_names[0] if scientific_names else "Unknown",
            "type": plant.get("type"), # Include type for matching
            "is_fruit": plant.get("edible_fruit"),
            "is_veg": plant.get("edible_leaf"),
        })
    return results


def get_species_details_api(species_id: int) -> Dict:
    """Retrieve detailed plant data from Perenual API."""
    logger.debug(f"[PERENUAL API] Attempting to get details for species_id={species_id}")
    # =====================================
    # TRY SNAPSHOT FIRST
    # =====================================

    snapshot = load_species_snapshot(species_id)

    if snapshot:
        logger.info(
            f"[PERENUAL API] Using snapshot for species_id={species_id}"
        )
        logger.debug(f"[PERENUAL API] Snapshot data for {species_id}: {snapshot.get('id')}")
        return snapshot

    # =====================================
    # API CALL
    # =====================================

    url = f"{BASE_URL}/species/details/{species_id}"

    params = {
        "key": PERENUAL_API_KEY
    }

    cache_key = f"details:{species_id}"

    api_response = _make_api_call_with_cooldown(
        url,
        params,
        cache_key
    )
    logger.debug(f"[PERENUAL API] API response for {species_id}: {api_response.get('id') if api_response else 'None'}")

    if api_response and api_response.get("id"):
        save_species_snapshot(species_id, api_response)
        logger.info(f"[PERENUAL API] Saved new snapshot for species_id={species_id}")

    logger.info(
        f"[PERENUAL API] Details for species_id={species_id}: "
        f"{api_response.get('id')}"
    )

    return api_response


# =========================================
# CONVERTING INCOMING SPECIES DATA
# =========================================
def normalize_species_data(api_data: dict) -> dict:
    """
    Convert Perenual API response into internal format.
    Ensures safe handling of missing or inconsistent fields.
    """

    def safe_join(value):

        if isinstance(value, list):
            return ", ".join(
                [str(v) for v in value if v]
            )

        if isinstance(value, str):
            return value

        return None

    def map_watering(text: str) -> int:

        mapping = {
            "Frequent": 1,
            "Average": 3,
            "Minimum": 7,
            "None": 30
        }

        return mapping.get(text, 3)

    scientific = api_data.get("scientific_name")

    if isinstance(scientific, list):
        scientific = (
            scientific[0]
            if scientific
            else None
        )

    if not scientific:
        scientific = api_data.get("common_name")

    if not scientific:
        scientific = "Unknown Species"

    # =====================================
    # DIMENSIONS
    # =====================================

    dimension_data = (
        api_data.get("dimension")
        or api_data.get("dimensions")
        or {}
    )

    logger.info(dimension_data)

    height = None
    width = None

    # -------------------------------------
    # CASE 1 → DICT FORMAT
    # -------------------------------------

    if isinstance(dimension_data, dict):

        height = (
            dimension_data.get("height")
            or dimension_data.get("height_ft")
        )

        width = (
            dimension_data.get("width")
            or dimension_data.get("spread")
        )

    # -------------------------------------
    # CASE 2 → LIST FORMAT
    # -------------------------------------

    elif isinstance(dimension_data, list):

        for item in dimension_data:

            if not isinstance(item, dict):
                continue

            dimension_type = str(
                item.get("type", "")
            ).lower()

            max_value = (
                item.get("max_value")
                or item.get("max")
                or item.get("value")
            )

            if (
                "height" in dimension_type
                and height is None
            ):
                height = max_value

            if (
                "width" in dimension_type
                or "spread" in dimension_type
            ) and width is None:

                width = max_value

    # =====================================
    # MEDIA
    # =====================================

    image_data = api_data.get(
        "default_image",
        {}
    )

    # =====================================
    # RETURN NORMALIZED DATA
    # =====================================

    return {

        # =====================================
        # CORE
        # =====================================

        "species": scientific,
        "common_name": api_data.get("common_name"),
        "other_names": safe_join(
            api_data.get("other_name")
        ),

        "plant_type": api_data.get("type"),
        "description": api_data.get("description"),

        # =====================================
        # EDIBILITY
        # =====================================

        "is_fruit": api_data.get(
            "edible_fruit",
            False
        ),

        "is_veg": api_data.get(
            "edible_leaf",
            False
        ),

        "cuisine": api_data.get(
            "cuisine",
            False
        ),

        "medicinal": api_data.get(
            "medicinal",
            False
        ),

        "poisonous_to_humans": api_data.get(
            "poisonous_to_humans"
        ),

        "poisonous_to_pets": api_data.get(
            "poisonous_to_pets"
        ),

        "is_edible": (
            api_data.get(
                "edible_fruit",
                False
            )
            or api_data.get(
                "edible_leaf",
                False
            )
            or api_data.get(
                "cuisine",
                False
            )
        ),

        # =====================================
        # GROWTH
        # =====================================

        "cycle": api_data.get("cycle"),

        "growth_rate": api_data.get(
            "growth_rate"
        ),

        "care_level": api_data.get(
            "care_level"
        ),

        "watering": api_data.get(
            "watering"
        ),

        "watering_interval_days": map_watering(
            api_data.get(
                "watering",
                "Average"
            )
        )
        ,

        "drought_tolerant": api_data.get(
            "drought_tolerant"
        ),

        "salt_tolerant": api_data.get(
            "salt_tolerant"
        ),

        "thorny": api_data.get(
            "thorny"
        ),

        "invasive": api_data.get(
            "invasive"
        ),

        "tropical": api_data.get(
            "tropical"
        ),

        "indoor": api_data.get(
            "indoor"
        ),

        # =====================================
        # ENVIRONMENT
        # =====================================

        "sunlight": safe_join(
            api_data.get("sunlight")
        ),

        "soil": safe_join(
            api_data.get("soil")
        ),

        "propagation": safe_join(
            api_data.get("propagation")
        ),

        "pest_susceptibility": safe_join(
            api_data.get(
                "pest_susceptibility"
            )
        ),

        "hardiness": (
            f"{api_data.get('hardiness', {}).get('min')} "
            f"to "
            f"{api_data.get('hardiness', {}).get('max')}"
            if api_data.get("hardiness")
            else None
        ),

        "hardiness_location": (
            api_data.get(
                "hardiness_location",
                {}
            ).get("full_url")
            if api_data.get(
                "hardiness_location"
            )
            else None
        ),

        # =====================================
        # DIMENSIONS
        # =====================================

        "max_height_ft": safe_float(
            height
        ),

        "max_width_ft": safe_float(
            width
        ),

        # =====================================
        # MEDIA
        # =====================================

        "default_image_url": image_data.get(
            "regular_url"
        ),

        "thumbnail_url": image_data.get(
            "thumbnail"
        )
    }

# ===============================
# DATABASE CACHE LAYER (PlantSpeciesCache)
# ===============================
def get_or_create_species_cache(
    db: Session,
    external_species_id: int,
    fallback_name: str = None
) -> PlantSpeciesCache:
    """
    Retrieves species from DB cache or fetches from API and caches it.
    """
    logger.info(f"[DB CACHE] Attempting to get or create species with external_species_id={external_species_id}")

    cached = db.query(PlantSpeciesCache).filter(
        PlantSpeciesCache.external_species_id == str(external_species_id)
    ).first()

    needs_sync = (
        not cached or
        cached.scientific_name == "Unknown Species" or # Placeholder
        cached.is_fruit is None or
        cached.watering_interval_days is None
    )

    if cached and not needs_sync:
        logger.info(f"[DB CACHE] Found species {external_species_id} in DB cache. Internal ID: {cached.id}")
        return cached
    elif cached and needs_sync:
        logger.info(f"[DB CACHE] Species {external_species_id} found but needs sync.")
    else:
        logger.info(f"[DB CACHE] Species {external_species_id} not found in DB cache. Fetching from API.")

    api_data = get_species_details_api(external_species_id)

    # -------------------------------
    # API FAILURE (or no valid data)
    # -------------------------------
    if not api_data or not api_data.get("id"):
        logger.warning(f"[DB CACHE] API call for species {external_species_id} failed or returned no valid data. Creating/updating placeholder.")
        if cached: # Update existing placeholder
            cached.scientific_name = fallback_name or "Unknown Species"
            cached.common_name = fallback_name or "Unknown Species"
            cached.watering_interval_days = 7 # Default
            db.commit()
            db.refresh(cached)
            logger.info(f"[DB CACHE] Updated placeholder species {external_species_id}. Internal ID: {cached.id}")
            return cached
        else: # Create new placeholder
            new_species = PlantSpeciesCache(
                external_species_id=str(external_species_id),
                scientific_name=fallback_name or "Unknown Species",
                common_name=fallback_name or "Unknown Species",
                watering_interval_days=7
            )
            db.add(new_species)
            db.commit()
            db.refresh(new_species)
            logger.info(f"[DB CACHE] Created placeholder species {external_species_id}. Internal ID: {new_species.id}")
            return new_species

    # -------------------------------
    # API SUCCESS
    # -------------------------------
    logger.info(f"[DB CACHE] API call for species {external_species_id} successful. Processing data.")
    enriched = normalize_species_data(api_data)

    if cached:
        logger.info(f"[DB CACHE] Updating existing DB cached species {external_species_id}. Internal ID: {cached.id}")
        cached.scientific_name = enriched.get("species")
        cached.common_name = api_data.get("common_name") or enriched.get("species")
        cached.other_names = enriched.get("other_names")
        cached.is_fruit = enriched.get("is_fruit")
        cached.is_veg = enriched.get("is_veg")
        cached.is_edible = enriched.get("is_edible")
        cached.growth_rate = enriched.get("growth_rate")
        cached.life_cycle = enriched.get("cycle")
        cached.sunlight_requirement = enriched.get("sunlight")
        cached.watering_interval_days = enriched.get("watering_interval_days", 7)
        cached.recommended_soil = enriched.get("soil")
        cached.propagation_method = enriched.get("propagation")
        cached.pest_susceptibility = enriched.get("pest_susceptibility")
        cached.plant_type = enriched.get("plant_type")
        cached.description = enriched.get("description")
        cached.cuisine = enriched.get("cuisine")
        cached.medicinal = enriched.get("medicinal")
        cached.poisonous_to_humans = enriched.get("poisonous_to_humans")
        cached.poisonous_to_pets = enriched.get("poisonous_to_pets")
        cached.care_level = enriched.get("care_level")
        cached.watering = enriched.get("watering")
        cached.drought_tolerant = enriched.get("drought_tolerant")
        cached.salt_tolerant = enriched.get("salt_tolerant")
        cached.thorny = enriched.get("thorny")
        cached.invasive = enriched.get("invasive")
        cached.tropical = enriched.get("tropical")
        cached.indoor = enriched.get("indoor")
        cached.hardiness = enriched.get("hardiness")
        cached.hardiness_location = enriched.get("hardiness_location")
        cached.max_height_ft = enriched.get("max_height_ft")
        cached.max_width_ft = enriched.get("max_width_ft")
        cached.default_image_url = enriched.get("default_image_url")
        cached.thumbnail_url = enriched.get("thumbnail_url")
        cached.data = api_data
        db.commit()
        db.refresh(cached)
        return cached
    else:
        logger.info(
            f"[DB CACHE] Creating new DB cached species "
            f"{external_species_id}."
        )

        new_species = PlantSpeciesCache(
            external_species_id=str(external_species_id),

            # =====================================
            # CORE IDENTITY
            # =====================================

            scientific_name=enriched.get("species"),
            common_name=api_data.get("common_name")
                        or enriched.get("species"),

            other_names=enriched.get("other_names"),
            plant_type=enriched.get("plant_type"),
            description=enriched.get("description"),

            # =====================================
            # EDIBILITY
            # =====================================

            is_edible=enriched.get("is_edible"),
            is_fruit=enriched.get("is_fruit"),
            is_veg=enriched.get("is_veg"),
            cuisine=enriched.get("cuisine"),
            medicinal=enriched.get("medicinal"),

            poisonous_to_humans=enriched.get(
                "poisonous_to_humans"
            ),

            poisonous_to_pets=enriched.get(
                "poisonous_to_pets"
            ),

            # =====================================
            # GROWTH & CARE
            # =====================================

            growth_rate=enriched.get("growth_rate"),
            life_cycle=enriched.get("cycle"),
            care_level=enriched.get("care_level"),

            watering=enriched.get("watering"),

            watering_interval_days=enriched.get(
                "watering_interval_days",
                4
            ),

            drought_tolerant=enriched.get(
                "drought_tolerant"
            ),

            salt_tolerant=enriched.get(
                "salt_tolerant"
            ),

            thorny=enriched.get("thorny"),
            invasive=enriched.get("invasive"),
            tropical=enriched.get("tropical"),
            indoor=enriched.get("indoor"),

            # =====================================
            # ENVIRONMENT
            # =====================================

            sunlight_requirement=enriched.get("sunlight"),

            recommended_soil=enriched.get("soil"),

            propagation_method=enriched.get(
                "propagation"
            ),

            pest_susceptibility=enriched.get(
                "pest_susceptibility"
            ),

            hardiness=enriched.get("hardiness"),

            hardiness_location=enriched.get(
                "hardiness_location"
            ),

            # =====================================
            # DIMENSIONS
            # =====================================

            max_height_ft=enriched.get("max_height_ft"),
            max_width_ft=enriched.get("max_width_ft"),

            # =====================================
            # MEDIA
            # =====================================

            default_image_url=enriched.get(
                "default_image_url"
            ),

            thumbnail_url=enriched.get(
                "thumbnail_url"
            ),

            # =====================================
            # RAW API PAYLOAD
            # =====================================

            data=api_data
        )

        db.add(new_species)
        db.commit()
        db.refresh(new_species)

        logger.info(
            f"[DB CACHE] Created new species "
            f"{external_species_id}. "
            f"Internal ID: {new_species.id}"
        )

        return new_species


# ===============================
# SPECIES SUGGESTION & RESOLUTION
# ===============================

def suggest_species(
    db: Session,
    query: str,
    plant_type: str = None,
    pre_cache_limit: int = 5
):
    """
    Suggests species based on query.
    """

    candidates = []

    # =====================================
    # 1. SEARCH DB CACHE
    # =====================================

    search_query_like = f"%{query}%"

    cached_matches = db.query(
        PlantSpeciesCache
    ).filter(
        (
            PlantSpeciesCache.common_name.ilike(
                search_query_like
            )
        )
        |
        (
            PlantSpeciesCache.scientific_name.ilike(
                search_query_like
            )
        )
    ).all()

    for species in cached_matches:

        candidates.append(
            normalize_candidate(
                {
                    "id": int(
                        species.external_species_id
                    ),

                    "common_name": species.common_name,

                    "scientific_name": (
                        species.scientific_name
                    ),

                    "is_edible": species.is_edible,

                    "is_fruit": species.is_fruit,

                    "is_veg": species.is_veg,

                    "growth_rate": (
                        species.growth_rate
                    ),

                    "type": (
                        species.data.get("type")
                        if species.data
                        else None
                    )
                },
                "db_cache"
            )
        )

    # =====================================
    # 2. SEARCH API
    # =====================================

    cached_suggestions = get_cached_species_suggestions(query)

    if cached_suggestions:

        logger.info(
            f"[SPECIES SUGGEST] Using cached suggestions "
            f"for '{query}'"
        )

        api_results = cached_suggestions

    else:

        api_results = search_plant_species_api(query)

        if api_results:
            cache_species_suggestions(
                query,
                api_results
            )
    for item in api_results:

        candidates.append(
            normalize_candidate(
                {
                    "id": item.get("id"),

                    "common_name": item.get(
                        "common_name"
                    ),

                    "scientific_name": item.get(
                        "scientific_name"
                    ),

                    "type": item.get("type"),

                    "is_fruit": item.get(
                        "edible_fruit"
                    ),

                    "is_veg": item.get(
                        "edible_leaf"
                    ),
                },
                "api"
            )
        )
    # 3. RANKING
    ranked = rank_species_matches(
        query,
        candidates,
        plant_type=plant_type
    )

    logger.info(
        f"[SPECIES SUGGEST] Ranked {len(ranked)} "
        f"candidates for query='{query}'. "
        f"Top 5: {ranked[:5]}"
    )

    # =====================================
    # SAVE TOP SUGGESTIONS TO JSON
    # =====================================
    saved_count = 0
    for i, suggestion in enumerate(ranked):
        if saved_count >= pre_cache_limit:
            logger.debug(f"[SUGGESTION CACHE] Reached pre_cache_limit ({pre_cache_limit}). Stopping further snapshot saves.")
            break

        species_id = suggestion.get("id")
        score = suggestion.get("score")

        logger.debug(f"[SUGGESTION CACHE] Processing suggestion {i+1}: ID={species_id}, Score={score}")

        # Only save if species_id is valid and score is > 50 or == 100
        if species_id and (score >= 50 ):
            logger.debug(f"[SUGGESTION CACHE] Score {score} meets criteria for species ID {species_id}. Attempting to get details.")
            details = get_species_details_api(species_id)

            if details and details.get("id"):
                save_species_snapshot(
                    species_id,
                    details
                )
                saved_count += 1
                logger.debug(f"[SUGGESTION CACHE] Successfully saved snapshot for species ID {species_id}.")
            else:
                logger.warning(f"[SUGGESTION CACHE] Failed to get valid details for species ID {species_id}. Snapshot not saved.")
        else:
            logger.debug(f"[SUGGESTION CACHE] Species ID {species_id} or score {score} does not meet criteria. Snapshot not saved.")


    logger.info(
        f"[SUGGESTION CACHE] Saved {saved_count} "
        f"species snapshots for '{query}' based on score criteria."
    )

    return ranked[:5]


def resolve_species(
    db: Session,
    plant_name: str,
    plant_type: str = None
) -> int | None:
    """
    Main entry used by plant_service
    to get an internal species_id.
    """

    logger.info(
        f"[SPECIES RESOLVE] "
        f"Attempting to resolve species "
        f"for '{plant_name}' "
        f"(type: {plant_type})."
    )

    suggestions = suggest_species(
        db,
        plant_name,
        plant_type
    )

    best_match = select_best_match(
        plant_name,
        suggestions,
        threshold=65,
        plant_type=plant_type
    )

    # =====================================
    # NO GOOD MATCH
    # =====================================

    if not best_match:

        logger.info(
            f"[SPECIES RESOLVE] "
            f"No confident best match found "
            f"for '{plant_name}'."
        )

        return None

    logger.info(
        f"[SPECIES RESOLVE] "
        f"Best match for '{plant_name}': "
        f"{best_match['common_name']} "
        f"(ID: {best_match['id']}, "
        f"Score: {best_match['score']})."
    )

    # =====================================
    # CREATE / LOAD CACHE
    # =====================================

    try:

        species = get_or_create_species_cache(
            db,
            best_match["id"],
            fallback_name=best_match.get(
                "scientific_name"
            )
        )

        return species.id if species else None

    except Exception as e:

        logger.error(
            f"[SPECIES RESOLVE] "
            f"Failed to get or create "
            f"species cache for "
            f"{best_match['id']}: {e}"
        )

        return None
