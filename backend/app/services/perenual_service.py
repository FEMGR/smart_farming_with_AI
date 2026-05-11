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
from app.core.constants import COOLDOWN_SECONDS, DEFAULT_TTL, MAX_CACHE_SIZE
from app.core.logger import setup_logger
from app.models.plant_species_cache import PlantSpeciesCache
from app.utils.species_matching import (
    select_best_match,
    rank_species_matches,
    normalize_candidate
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


# =========================================
# EXTERNAL API CALLS (Perenual)
# =========================================
def _make_api_call_with_cooldown(url: str, params: Dict, cache_key: str = None) -> Dict | List:
    """Handles API call with global cooldown and in-memory caching."""
    global _last_api_call_time
    now = time.time()

    if now - _last_api_call_time < COOLDOWN_SECONDS:
        logger.info(f"[PERENUAL API] Cooldown active, skipping API call for {url}")
        return {} if "details" in url else [] # Return appropriate empty type

    _last_api_call_time = now

    if cache_key:
        cached = _get_cache(cache_key)
        if cached is not None:
            return cached

    logger.info(f"[PERENUAL API] Querying external API: {url}")
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            logger.error(f"[PERENUAL API] Call failed with status={response.status_code} for {url}")
            return {} if "details" in url else []

        data = response.json()
        if cache_key:
            _set_cache(cache_key, data)
        return data

    except requests.exceptions.Timeout:
        logger.error(f"[PERENUAL API] Timeout during API call to {url}")
        return {} if "details" in url else []
    except requests.exceptions.RequestException as e:
        logger.error(f"[PERENUAL API] Request error during API call to {url}: {e}")
        return {} if "details" in url else []
    except Exception as e:
        logger.error(f"[PERENUAL API] Unexpected error during API call to {url}: {e}")
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
    url = f"{BASE_URL}/species/details/{species_id}"
    params = {"key": PERENUAL_API_KEY}
    cache_key = f"details:{species_id}"

    api_response = _make_api_call_with_cooldown(url, params, cache_key)
    logger.info(f"[PERENUAL API] Details for species_id={species_id}: {api_response.get('id')}")
    return api_response


# =========================================
# CONVERTING INCOMING SPECIES DATA
# =========================================
def normalize_species_data(api_data: dict) -> dict:
    """
    Convert Perenual API response into internal format.
    Ensures safe handling of missing or inconsistent fields.
    """
    is_fruit = api_data.get("edible_fruit", False)
    is_veg = api_data.get("edible_leaf", False)
    is_cuisine = api_data.get("cuisine", False)
    is_edible = is_fruit or is_veg or is_cuisine

    def safe_join(value):
        if isinstance(value, list):
            return ", ".join([str(v) for v in value if v])
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
        scientific = scientific[0] if scientific else None
    if not scientific:
        scientific = api_data.get("common_name")
    if not scientific:
        scientific = "Unknown Species"

    return {
        "species": scientific,
        "cycle": api_data.get("cycle"),
        "is_fruit": is_fruit,
        "is_veg": is_veg,
        "is_edible": is_edible,
        "type": api_data.get("type", "unknown"),
        "growth_rate": api_data.get("growth_rate"),
        "sunlight": safe_join(api_data.get("sunlight")),
        "soil": safe_join(api_data.get("soil")),
        "propagation": safe_join(api_data.get("propagation")),
        "pest_susceptibility": safe_join(api_data.get("pest_susceptibility")),
        "watering_interval_days": map_watering(api_data.get("watering", "Average")),
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
        cached.data = api_data
        db.commit()
        db.refresh(cached)
        return cached
    else:
        logger.info(f"[DB CACHE] Creating new DB cached species {external_species_id}.")
        new_species = PlantSpeciesCache(
            external_species_id=str(external_species_id),
            scientific_name=enriched.get("species"),
            common_name=api_data.get("common_name") or enriched.get("species"),
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
        logger.info(f"[DB CACHE] Created new species {external_species_id}. Internal ID: {new_species.id}")
        return new_species


# ===============================
# SPECIES SUGGESTION & RESOLUTION
# ===============================
def suggest_species(db: Session, query: str, plant_type: str = None, pre_cache_limit: int = 5):
    """
    Suggests species based on query, proactively caching details for top results.
    """
    candidates = []

    # 1. CACHE SEARCH (DB Cache)
    search_query_like = f"%{query}%"
    cached_matches = db.query(PlantSpeciesCache).filter(
        (PlantSpeciesCache.common_name.ilike(search_query_like)) |
        (PlantSpeciesCache.scientific_name.ilike(search_query_like))
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
                "growth_rate": species.growth_rate,
                "type": species.data.get("type") if species.data else None # Extract type from raw data
            }, "db_cache")
        )

    # 2. API SEARCH (Perenual API)
    api_results = search_plant_species_api(query)

    for item in api_results:
        candidates.append(
            normalize_candidate({
                "id": item.get("id"),
                "common_name": item.get("common_name"),
                "scientific_name": item.get("scientific_name"),
                "type": item.get("type"), # Pass type for matching
                "is_fruit": item.get("edible_fruit"),
                "is_veg": item.get("edible_leaf"),
            }, "api")
        )

    if not candidates:
        logger.info(f"[SPECIES SUGGEST] No candidates found for query='{query}'.")
        return []

    # 3. RANKING
    ranked = rank_species_matches(query, candidates, plant_type=plant_type)
    logger.info(f"[SPECIES SUGGEST] Ranked {len(ranked)} candidates for query='{query}'. Top 5: {ranked[:5]}")

    # 4. PROACTIVELY POPULATE IN-MEMORY CACHE FOR TOP SUGGESTIONS
    # This addresses the "temporary caching" request
    for i, suggestion in enumerate(ranked):
        if i >= pre_cache_limit:
            break
        species_id_to_cache = suggestion.get("id")
        if species_id_to_cache:
            logger.info(f"[SPECIES SUGGEST] Proactively fetching details for {species_id_to_cache} to warm in-memory cache.")
            get_species_details_api(species_id_to_cache) # This call will use/populate the in-memory cache

    return ranked[:5] # Return top 5 suggestions


def resolve_species(
    db: Session,
    plant_name: str,
    plant_type: str = None
) -> int | None:
    """
    Main entry used by plant_service to get an internal species_id.
    Returns internal species_id or None.
    """
    logger.info(f"[SPECIES RESOLVE] Attempting to resolve species for '{plant_name}' (type: {plant_type}).")

    suggestions = suggest_species(db, plant_name, plant_type, pre_cache_limit=1) # Only pre-cache the best match

    best_match = select_best_match(
        plant_name,
        suggestions,
        threshold=65,
        plant_type=plant_type
    )

    if not best_match:
        logger.info(f"[SPECIES RESOLVE] No confident best match found for '{plant_name}'.")
        return None

    logger.info(f"[SPECIES RESOLVE] Best match for '{plant_name}': {best_match['common_name']} (ID: {best_match['id']}, Score: {best_match['score']}).")

    try:
        # This will use the in-memory cache (if warmed by suggest_species)
        # and then the DB cache, fetching from API if necessary.
        species = get_or_create_species_cache(
            db,
            best_match["id"],
            fallback_name=best_match.get("scientific_name")
        )
        return species.id if species else None

    except Exception as e:
        logger.error(f"[SPECIES RESOLVE] Failed to get or create species cache for {best_match['id']}: {e}")
        return None
