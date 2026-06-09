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

# app/services/perenual_service.py

import json
import os
import re
import tempfile
import time
from email.utils import parsedate_to_datetime
from typing import List, Any, Dict, Tuple, Optional

import requests
from rapidfuzz import fuzz
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import PERENUAL_API_KEY
from app.core.constants import (
    COOLDOWN_SECONDS,
    DEFAULT_TTL,
    MAX_CACHE_SIZE,
    API_REQUEST_TIMEOUT_SECONDS,
    PERENUAL_429_DEFAULT_BACKOFF_SECONDS,
    PERENUAL_429_MAX_BACKOFF_SECONDS,
    PERENUAL_BASE_URL,
    PERENUAL_DAILY_REQUEST_LIMIT,
    PERENUAL_DAILY_SOFT_LIMIT,
    PERENUAL_RATE_LIMIT_STATE_FILE,
    PERENUAL_SPECIES_DETAILS_MAX_ID,
)
from app.core.logger import setup_logger
from app.models.plant_species_cache import PlantSpeciesCache
from app.services.species_snapshot_service import (
    save_species_snapshot,
    load_species_snapshot,
)
from app.services.species_suggestion_cache_service import (
    cache_species_suggestions,
    get_cached_species_suggestions,
    load_suggestion_cache,
    remove_cached_species_suggestion,
)
from app.services.plant_taxonomy_service import get_taxonomy_by_atom
from app.utils.species_matching import (
    rank_species_matches,
    normalize_candidate,
    compute_match_score,
)

logger = setup_logger()


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
_details_backoff_until = 0.0
_search_backoff_until = 0.0
_perenual_429_failures = 0


def _today_key() -> str:
    return time.strftime("%Y-%m-%d", time.localtime())


def _load_rate_limit_state() -> dict:
    if not PERENUAL_RATE_LIMIT_STATE_FILE.exists():
        return {"date": _today_key(), "request_count": 0, "search_backoff_until": 0, "details_backoff_until": 0}

    try:
        with open(PERENUAL_RATE_LIMIT_STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("[PERENUAL API] Could not load rate-limit state; resetting. Error: %s", exc)
        return {"date": _today_key(), "request_count": 0, "search_backoff_until": 0, "details_backoff_until": 0}

    if state.get("date") != _today_key():
        return {"date": _today_key(), "request_count": 0, "search_backoff_until": 0, "details_backoff_until": 0}

    return state


def _save_rate_limit_state(state: dict) -> None:
    PERENUAL_RATE_LIMIT_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=PERENUAL_RATE_LIMIT_STATE_FILE.parent, delete=False) as f:
            json.dump(state, f, indent=2)
            temp_path = f.name
        os.replace(temp_path, PERENUAL_RATE_LIMIT_STATE_FILE)
    except OSError as exc:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        logger.warning("[PERENUAL API] Could not persist rate-limit state: %s", exc)


def _daily_request_count() -> int:
    return int(_load_rate_limit_state().get("request_count") or 0)


def _record_perenual_request() -> None:
    state = _load_rate_limit_state()
    state["request_count"] = int(state.get("request_count") or 0) + 1
    _save_rate_limit_state(state)


def _parse_retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None

    try:
        return max(float(value), 0.0)
    except ValueError:
        pass

    try:
        retry_at = parsedate_to_datetime(value)
        return max(retry_at.timestamp() - time.time(), 0.0)
    except (TypeError, ValueError, AttributeError):
        return None


def _is_details_url(url: str) -> bool:
    return "/species/details/" in url


def _species_details_plan_block_reason(species_id: int) -> str | None:
    if PERENUAL_SPECIES_DETAILS_MAX_ID <= 0:
        return None

    try:
        numeric_species_id = int(species_id)
    except (TypeError, ValueError):
        return None

    if numeric_species_id > PERENUAL_SPECIES_DETAILS_MAX_ID:
        return f"species_id={numeric_species_id} is outside configured Perenual species details access " f"range 1-{PERENUAL_SPECIES_DETAILS_MAX_ID}"

    return None


def _endpoint_backoff_remaining(url: str) -> float:
    state = _load_rate_limit_state()
    if _is_details_url(url):
        persisted_backoff_until = float(state.get("details_backoff_until") or 0)
        in_memory_backoff_until = _details_backoff_until
    else:
        persisted_backoff_until = float(state.get("search_backoff_until") or 0)
        in_memory_backoff_until = _search_backoff_until

    return max(max(in_memory_backoff_until, persisted_backoff_until) - time.time(), 0.0)


def _perenual_request_block_reason(url: str, *, ignore_endpoint_backoff: bool = False) -> str | None:
    remaining = 0.0 if ignore_endpoint_backoff else _endpoint_backoff_remaining(url)
    if remaining > 0:
        endpoint = "details" if _is_details_url(url) else "species-list"
        return f"{endpoint} 429 backoff active for {remaining:.0f} more seconds"

    request_count = _daily_request_count()
    if request_count >= PERENUAL_DAILY_SOFT_LIMIT:
        return f"local daily soft limit reached ({request_count}/{PERENUAL_DAILY_REQUEST_LIMIT} requests)"

    return None


def _can_make_perenual_request(url: str, *, ignore_endpoint_backoff: bool = False) -> bool:
    block_reason = _perenual_request_block_reason(url, ignore_endpoint_backoff=ignore_endpoint_backoff)
    if block_reason:
        logger.warning("[PERENUAL API] %s. Skipping %s.", block_reason, url)
        return False

    return True


def _record_perenual_response(url: str, response: requests.Response) -> None:
    global _details_backoff_until, _search_backoff_until, _perenual_429_failures

    if response.status_code != 429:
        _perenual_429_failures = 0
        return

    if "upgrade plan" in (response.text or "").lower():
        logger.warning(
            "[PERENUAL API] Received plan-gated 429 for %s. Not applying endpoint backoff.",
            url,
        )
        return

    _perenual_429_failures += 1
    retry_after = _parse_retry_after_seconds(response.headers.get("Retry-After"))
    if retry_after is None:
        retry_after = min(
            PERENUAL_429_DEFAULT_BACKOFF_SECONDS * (2 ** min(_perenual_429_failures - 1, 5)),
            PERENUAL_429_MAX_BACKOFF_SECONDS,
        )
    else:
        retry_after = min(max(retry_after, COOLDOWN_SECONDS), PERENUAL_429_MAX_BACKOFF_SECONDS)

    backoff_until = time.time() + retry_after
    state = _load_rate_limit_state()
    if _is_details_url(url):
        _details_backoff_until = max(_details_backoff_until, backoff_until)
        state["details_backoff_until"] = max(float(state.get("details_backoff_until") or 0), backoff_until)
    else:
        _search_backoff_until = max(_search_backoff_until, backoff_until)
        state["search_backoff_until"] = max(float(state.get("search_backoff_until") or 0), backoff_until)
    state["last_429_at"] = time.time()
    _save_rate_limit_state(state)

    logger.warning(
        "[PERENUAL API] Received 429 for %s. Backing off this endpoint for %.0f seconds.",
        url,
        retry_after,
    )


def _wait_for_api_cooldown(url: str) -> None:
    global _last_api_call_time

    now = time.time()
    time_since_last_call = now - _last_api_call_time

    if time_since_last_call < COOLDOWN_SECONDS:
        wait_time = COOLDOWN_SECONDS - time_since_last_call
        logger.info(f"[PERENUAL API] Cooldown active. Waiting {wait_time:.2f}s before calling {url}")
        time.sleep(wait_time)
        now = time.time()

    _last_api_call_time = now


def _is_search_result_only_payload(data: dict | None) -> bool:
    return bool(data and (data.get("snapshot_quality") == "search_result_only" or data.get("details_status") == "unavailable"))


def _candidate_search_terms_from_taxonomy() -> set[str]:
    terms: set[str] = set()
    for atom, data in get_taxonomy_by_atom().items():
        if atom:
            terms.add(atom.replace("_", " "))
        for field in ("scientific_name", "genus"):
            value = data.get(field)
            if value:
                terms.add(str(value))
        for value in data.get("alternate_scientific_names") or []:
            if value:
                terms.add(str(value))
    return terms


def _candidate_search_terms_from_suggestion_cache() -> set[str]:
    terms: set[str] = set()
    for query, item in load_suggestion_cache().items():
        if query:
            terms.add(str(query))
        for suggestion in item.get("suggestions") or []:
            for field in ("common_name", "scientific_name", "genus"):
                value = suggestion.get(field)
                if value:
                    terms.add(str(value))
    return terms


def _correct_species_query(query: str, min_score: int = 84) -> tuple[str | None, int]:
    """Return a local spelling correction candidate for missed Perenual searches."""
    normalized_query = _normalized_name(query)
    if len(normalized_query) < 5:
        return None, 0

    terms = _candidate_search_terms_from_taxonomy() | _candidate_search_terms_from_suggestion_cache()
    normalized_terms = {_normalized_name(term) for term in terms if term}
    if normalized_query in normalized_terms:
        return None, 0

    candidates = []
    for term in terms:
        term = str(term or "").strip()
        normalized_term = _normalized_name(term)
        if not normalized_term or normalized_term == normalized_query:
            continue
        score = int(fuzz.WRatio(normalized_query, normalized_term))
        if score >= min_score:
            candidates.append((score, len(normalized_term.split()), len(normalized_term), term))

    if not candidates:
        return None, 0

    candidates.sort(key=lambda item: (item[0], -item[1], -item[2]), reverse=True)
    score, _, _, corrected = candidates[0]
    logger.info("[SPECIES SUGGEST] Corrected query '%s' -> '%s' (score=%s).", query, corrected, score)
    return corrected, score


def correct_species_query(query: str, min_score: int = 84) -> str | None:
    """Return the corrected plant/species search name when confidence is high enough."""
    corrected, _ = _correct_species_query(query, min_score=min_score)
    return corrected


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
def _make_api_call_with_cooldown(url: str, params: Dict, cache_key: str = None) -> Dict | List:
    """Handles API call with global cooldown and in-memory caching."""
    # =====================================
    # CHECK CACHE FIRST
    # =====================================

    if cache_key:
        cached = _get_cache(cache_key)

        if cached is not None:
            return cached

    if not _can_make_perenual_request(url):
        return {} if "details" in url else []

    # =====================================
    # COOLDOWN - WAIT INSTEAD OF SKIP
    # =====================================

    _wait_for_api_cooldown(url)

    # =====================================
    # REAL API CALL
    # =====================================

    logger.info(f"[PERENUAL API] Querying external API: {url}")

    try:
        _record_perenual_request()
        response = requests.get(url, params=params, timeout=API_REQUEST_TIMEOUT_SECONDS)
        _record_perenual_response(url, response)

        if response.status_code != 200:
            logger.error(f"[PERENUAL API] Call failed " f"with status={response.status_code} " f"for {url}")

            return {} if "details" in url else []

        data = response.json()

        if cache_key:
            _set_cache(cache_key, data)

        return data

    except requests.exceptions.Timeout:

        logger.error(f"[PERENUAL API] Timeout during API call to {url}")

        return {} if "details" in url else []

    except requests.exceptions.RequestException as e:

        logger.error(f"[PERENUAL API] Request error during API call " f"to {url}: {e}")

        return {} if "details" in url else []

    except Exception as e:

        logger.error(f"[PERENUAL API] Unexpected error " f"during API call to {url}: {e}")

        return {} if "details" in url else []


def _make_details_api_call_with_retry(
    species_id: int,
    max_retries: int = 1,
    *,
    ignore_backoff: bool = False,
) -> Optional[Dict]:
    """Fetch details for the selected species; a 429 starts endpoint backoff."""
    url = f"{PERENUAL_BASE_URL}/species/details/{species_id}"
    params = {"key": PERENUAL_API_KEY}
    cache_key = f"details:{species_id}"

    plan_block_reason = _species_details_plan_block_reason(species_id)
    if plan_block_reason:
        logger.warning("[PERENUAL API] Skipping details fetch: %s.", plan_block_reason)
        return None

    cached = _get_cache(cache_key)
    if cached is not None:
        return cached

    total_attempts = max(1, int(max_retries or 1))

    for attempt in range(total_attempts):
        if not _can_make_perenual_request(url, ignore_endpoint_backoff=ignore_backoff):
            return None

        _wait_for_api_cooldown(url)
        logger.info(
            "[PERENUAL API] Querying external API: %s (details request for species_id=%s attempt=%s/%s)",
            url,
            species_id,
            attempt + 1,
            total_attempts,
        )

        try:
            _record_perenual_request()
            response = requests.get(url, params=params, timeout=API_REQUEST_TIMEOUT_SECONDS)
            _record_perenual_response(url, response)
        except requests.exceptions.Timeout:
            logger.error(f"[PERENUAL API] Timeout during API call to {url}")
            return None
        except requests.exceptions.RequestException as exc:
            logger.error(f"[PERENUAL API] Request error during API call to {url}: {exc}")
            return None

        if response.status_code == 200:
            data = response.json()
            _set_cache(cache_key, data)
            return data

        logger.error(f"[PERENUAL API] Call failed with status={response.status_code} for {url}")
        if response.status_code == 429:
            return None
        return None

    return None


def search_plant_species_api(query: str, limit: int = 5) -> List[Dict]:
    """
    Search plant species by name from Perenual API.
    Returns a list of basic species dicts.
    """
    url = f"{PERENUAL_BASE_URL}/species-list"
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
        results.append(
            {
                "id": plant.get("id"),
                "common_name": plant.get("common_name", "Unknown"),
                "scientific_name": (scientific_names[0] if scientific_names else "Unknown"),
                "type": plant.get("type"),  # Include type for matching
                "is_fruit": plant.get("edible_fruit"),
                "is_veg": plant.get("edible_leaf"),
                "genus": plant.get("genus"),
                "family": plant.get("family"),
            }
        )
    return results


def _get_species_details_from_source(
    species_id: int,
    *,
    ignore_backoff: bool = False,
    max_retries: int = 1,
    force_api: bool = False,
) -> Optional[Dict]:
    """
    Helper to retrieve species details, checking snapshot first, then API.
    Handles saving snapshot if API is called.
    """
    logger.debug(f"[PERENUAL API] Attempting to get details for species_id={species_id} from source.")

    # 1. Try Snapshot
    snapshot = None if force_api else load_species_snapshot(species_id)
    if snapshot:
        if snapshot.get("snapshot_quality") != "search_result_only":
            logger.info(f"[PERENUAL API] Using snapshot for species_id={species_id}")
            return snapshot
        logger.info(
            "[PERENUAL API] Snapshot for species_id=%s is search-result-only; attempting details refresh.",
            species_id,
        )

    plan_block_reason = _species_details_plan_block_reason(species_id)
    if plan_block_reason:
        logger.warning("[PERENUAL API] Skipping details fetch: %s.", plan_block_reason)
        return None

    details_url = f"{PERENUAL_BASE_URL}/species/details/{species_id}"
    remaining = 0.0 if ignore_backoff else _endpoint_backoff_remaining(details_url)
    if remaining > 0:
        logger.warning(
            "[PERENUAL API] Details endpoint is in 429 backoff for %.0f more seconds. Skipping species_id=%s.",
            remaining,
            species_id,
        )
        return None

    # 2. Fallback to API
    api_response = _make_details_api_call_with_retry(species_id, max_retries=max_retries, ignore_backoff=ignore_backoff)

    if api_response and api_response.get("id"):
        save_species_snapshot(species_id, api_response)
        logger.info(f"[PERENUAL API] Saved new snapshot for species_id={species_id}")
        return api_response
    else:
        logger.warning(f"[PERENUAL API] Failed to get valid details for species ID {species_id} from API.")
        return None


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
            return ", ".join([str(v).strip() for v in value if v])
        if isinstance(value, str):
            return value.strip()
        return None

    def map_watering(text: str) -> int:
        mapping = {"frequent": 1, "average": 3, "minimum": 7, "none": 30}
        if not text:
            return 3
        return mapping.get(text.lower(), 3)

    # ===============================
    # SCIENTIFIC NAME
    # ===============================
    scientific = api_data.get("scientific_name")

    if isinstance(scientific, list):
        scientific = scientific[0] if scientific else None

    if not scientific:
        scientific = api_data.get("common_name") or "Unknown Species"

    genus = api_data.get("genus")
    if not genus and scientific:
        genus = str(scientific).split()[0].lower()

    # ===============================
    # DIMENSIONS
    # ===============================
    dimension_data = api_data.get("dimension") or api_data.get("dimensions") or {}

    height = None
    width = None

    if isinstance(dimension_data, dict):
        height = dimension_data.get("height") or dimension_data.get("height_ft")
        width = dimension_data.get("width") or dimension_data.get("spread")

    elif isinstance(dimension_data, list):
        for item in dimension_data:
            if not isinstance(item, dict):
                continue

            dtype = str(item.get("type", "")).lower()
            value = item.get("max_value") or item.get("value")

            if "height" in dtype and height is None:
                height = value
            if ("width" in dtype or "spread" in dtype) and width is None:
                width = value

    # ===============================
    # NORMALIZED FIELDS (CRITICAL)
    # ===============================
    raw_watering = api_data.get("watering") or "Average"
    raw_sunlight = safe_join(api_data.get("sunlight")) or "Full Sun"
    raw_soil = safe_join(api_data.get("soil")) or "Well-drained"

    # ===============================
    # MEDIA
    # ===============================
    image_data = api_data.get("default_image") or {}

    # ===============================
    # RETURN STRUCTURE
    # ===============================
    return {
        # CORE
        "species": scientific,
        "common_name": api_data.get("common_name") or scientific,
        "other_names": safe_join(api_data.get("other_name")),
        "genus": genus,
        "family": api_data.get("family"),
        "plant_type": api_data.get("type") or "",
        # EDIBILITY
        "is_fruit": api_data.get("edible_fruit", False),
        "is_veg": api_data.get("edible_leaf", False),
        "cuisine": api_data.get("cuisine", False),
        "medicinal": api_data.get("medicinal", False),
        "poisonous_to_humans": api_data.get("poisonous_to_humans"),
        "poisonous_to_pets": api_data.get("poisonous_to_pets"),
        "is_edible": (api_data.get("edible_fruit", False) or api_data.get("edible_leaf", False) or api_data.get("cuisine", False)),
        # GROWTH
        "cycle": api_data.get("cycle"),
        "growth_rate": api_data.get("growth_rate"),
        "care_level": api_data.get("care_level") or "",
        # 🔑 IMPORTANT (used by constraint system)
        "watering": raw_watering,
        "watering_interval_days": map_watering(raw_watering),
        # ENVIRONMENT (CRITICAL)
        "sunlight": raw_sunlight,
        "soil": raw_soil,
        # OTHER ENVIRONMENT
        "drought_tolerant": api_data.get("drought_tolerant"),
        "salt_tolerant": api_data.get("salt_tolerant"),
        "thorny": api_data.get("thorny"),
        "invasive": api_data.get("invasive"),
        "tropical": api_data.get("tropical"),
        "indoor": api_data.get("indoor"),
        "propagation": safe_join(api_data.get("propagation")),
        "pest_susceptibility": safe_join(api_data.get("pest_susceptibility")),
        # HARDINESS
        "hardiness": (f"{api_data.get('hardiness', {}).get('min')} to {api_data.get('hardiness', {}).get('max')}" if api_data.get("hardiness") else None),
        "hardiness_location": (api_data.get("hardiness_location", {}).get("full_url") if api_data.get("hardiness_location") else None),
        # DIMENSIONS
        "max_height_ft": safe_float(height),
        "max_width_ft": safe_float(width),
        # MEDIA
        "default_image_url": image_data.get("regular_url") or "",
        "thumbnail_url": image_data.get("thumbnail") or "",
        # RAW
        "description": api_data.get("description") or "",
    }


# ===============================
# DATABASE CACHE LAYER (PlantSpeciesCache)
# ===============================
def get_or_create_species_cache(
    db: Session,
    external_species_id: int,
    fallback_name: str = None,
    *,
    force_refresh: bool = False,
    api_data_override: dict | None = None,
) -> PlantSpeciesCache | None:
    """
    Retrieves species from DB cache or fetches from snapshot/API and caches it.
    """
    logger.info(f"[DB CACHE] Attempting to get or create species with external_species_id={external_species_id}")

    # 1. Check DB cache first
    cached = db.query(PlantSpeciesCache).filter(PlantSpeciesCache.external_species_id == str(external_species_id)).first()

    # --- BEGIN MODIFICATION ---
    # More comprehensive needs_sync check for backfilling new columns
    needs_sync = (
        not cached
        or cached.scientific_name == "Unknown Species"  # Placeholder
        or cached.is_fruit is None  # Original check
        or cached.watering_interval_days is None  # Original check
        or
        # Add checks for newly added columns that might be "empty" but not None
        cached.description == ""
        or cached.max_height_ft == 0.0
        or cached.default_image_url == ""
        or cached.plant_type == ""
        or cached.care_level == ""
        or cached.sunlight_requirement == ""
        # You can add more checks here for other specific columns if needed
    )
    # --- END MODIFICATION ---

    if cached and not needs_sync and not force_refresh and not api_data_override:
        logger.info(f"[DB CACHE] Found species {external_species_id} in DB cache. Internal ID: {cached.id}")
        return cached
    elif cached and force_refresh:
        logger.info(f"[DB CACHE] Species {external_species_id} found; forcing Perenual refresh.")
    elif cached and needs_sync:
        logger.info(f"[DB CACHE] Species {external_species_id} found but needs sync.")
    else:
        logger.info(f"[DB CACHE] Species {external_species_id} not found in DB cache. Attempting to fetch from snapshot/API.")

    # 2. If not in DB or needs sync, get data from snapshot/API
    api_data = api_data_override or _get_species_details_from_source(external_species_id, force_api=force_refresh)

    # -------------------------------
    # DATA ACQUISITION FAILURE
    # -------------------------------
    if not api_data or not api_data.get("id"):
        logger.warning(
            "[DB CACHE] Failed to acquire valid species data for %s. Not creating placeholder cache.",
            external_species_id,
        )
        return None

    # -------------------------------
    # DATA ACQUISITION SUCCESS
    # -------------------------------
    logger.info(f"[DB CACHE] Acquired species data for {external_species_id}. Processing data.")
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
        logger.info(f"[DB CACHE] Creating new DB cached species " f"{external_species_id}. ")

        new_species = PlantSpeciesCache(
            external_species_id=str(external_species_id),
            # =====================================
            # CORE IDENTITY
            # =====================================
            scientific_name=enriched.get("species"),
            common_name=api_data.get("common_name") or enriched.get("species"),
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
            poisonous_to_humans=enriched.get("poisonous_to_humans"),
            poisonous_to_pets=enriched.get("poisonous_to_pets"),
            # =====================================
            # GROWTH & CARE
            # =====================================
            growth_rate=enriched.get("growth_rate"),
            life_cycle=enriched.get("cycle"),
            care_level=enriched.get("care_level"),
            watering=enriched.get("watering"),
            watering_interval_days=enriched.get("watering_interval_days", 4),
            drought_tolerant=enriched.get("drought_tolerant"),
            salt_tolerant=enriched.get("salt_tolerant"),
            thorny=enriched.get("thorny"),
            invasive=enriched.get("invasive"),
            tropical=enriched.get("tropical"),
            indoor=enriched.get("indoor"),
            # =====================================
            # ENVIRONMENT
            # =====================================
            sunlight_requirement=enriched.get("sunlight"),
            recommended_soil=enriched.get("soil"),
            propagation_method=enriched.get("propagation"),
            pest_susceptibility=enriched.get("pest_susceptibility"),
            hardiness=enriched.get("hardiness"),
            hardiness_location=enriched.get("hardiness_location"),
            # =====================================
            # DIMENSIONS
            # =====================================
            max_height_ft=enriched.get("max_height_ft"),
            max_width_ft=enriched.get("max_width_ft"),
            # =====================================
            # MEDIA
            # =====================================
            default_image_url=enriched.get("default_image_url"),
            thumbnail_url=enriched.get("thumbnail_url"),
            # =====================================
            # RAW API PAYLOAD
            # =====================================
            data=api_data,
        )

        db.add(new_species)
        db.commit()
        db.refresh(new_species)

        logger.info(f"[DB CACHE] Created new species " f"{external_species_id}. " f"Internal ID: {new_species.id}")

        return new_species


# ===============================
# SPECIES SUGGESTION & RESOLUTION
# ===============================


def suggest_species(
    db: Session,
    query: str,
    plant_type: str = None,
    pre_cache_limit: int = 0,
    *,
    allow_external_api: bool = True,
    preferred_scientific_names: list[str] | None = None,
    preferred_common_names: list[str] | None = None,
    preferred_genus: str | None = None,
    preferred_family: str | None = None,
):
    """
    Suggest species using one source at a time:
    DB species cache, then JSON suggestion cache, then Perenual search.
    """

    def rank_candidates(candidates: list[dict], source_name: str) -> list[dict]:
        ranked_candidates = rank_species_matches(
            query,
            candidates,
            plant_type=plant_type,
            preferred_scientific_names=preferred_scientific_names,
            preferred_common_names=preferred_common_names,
            preferred_genus=preferred_genus,
            preferred_family=preferred_family,
        )
        ranked_candidates = _filter_ranked_by_preferred_identity(
            ranked_candidates,
            preferred_scientific_names,
            preferred_common_names,
        )
        logger.info(
            "[SPECIES SUGGEST] Ranked %s candidates for query='%s' from %s. Top 5: %s",
            len(ranked_candidates),
            query,
            source_name,
            ranked_candidates[:5],
        )
        return ranked_candidates

    def db_candidates_for(search_query: str) -> list[dict]:
        search_query_like = f"%{search_query}%"
        cached_matches = (
            db.query(PlantSpeciesCache)
            .filter((PlantSpeciesCache.common_name.ilike(search_query_like)) | (PlantSpeciesCache.scientific_name.ilike(search_query_like)))
            .all()
        )
        candidates = []
        for species in cached_matches:
            if _is_search_result_only_payload(species.data):
                logger.info(
                    "[SPECIES SUGGEST] Ignoring lightweight DB cache species_id=%s for query='%s'; using suggestion cache/API if needed.",
                    species.external_species_id,
                    search_query,
                )
                continue

            candidates.append(_species_cache_candidate(species))
        return candidates

    def suggestion_items_to_candidates(items: list[dict], source_name: str) -> list[dict]:
        return [
            normalize_candidate(
                {
                    "id": item.get("id"),
                    "common_name": item.get("common_name"),
                    "scientific_name": item.get("scientific_name"),
                    "type": item.get("type"),
                    "is_fruit": item.get("is_fruit", item.get("edible_fruit")),
                    "is_veg": item.get("is_veg", item.get("edible_leaf")),
                    "genus": item.get("genus"),
                    "family": item.get("family"),
                },
                source_name,
            )
            for item in items
        ]

    # 1. Full DB species cache. If present, do not hit JSON or Perenual.
    db_candidates = db_candidates_for(query)
    if db_candidates:
        logger.info("[SPECIES SUGGEST] Using %s DB species candidates for query='%s'.", len(db_candidates), query)
        ranked = rank_candidates(db_candidates, "db_cache")[:5]
        if ranked:
            return ranked

    # 2. JSON search-result cache. If present, do not call Perenual search.
    cached_suggestions = get_cached_species_suggestions(query)
    if cached_suggestions:
        logger.info("[SPECIES SUGGEST] Using cached JSON suggestions for '%s'.", query)
        json_candidates = suggestion_items_to_candidates(cached_suggestions, "json_cache")
        ranked = rank_candidates(json_candidates, "json_cache")[:5]
        if ranked:
            return ranked

    # 3. Local spelling correction before spending an API request on a likely typo.
    effective_query = query
    corrected_query, correction_score = _correct_species_query(query)
    if corrected_query:
        corrected_db_candidates = db_candidates_for(corrected_query)
        if corrected_db_candidates:
            logger.info(
                "[SPECIES SUGGEST] Using %s DB species candidates for corrected query='%s' from original='%s'.",
                len(corrected_db_candidates),
                corrected_query,
                query,
            )
            ranked = rank_candidates(corrected_db_candidates, f"db_cache:{corrected_query}")[:5]
            if ranked:
                return ranked

        corrected_cached_suggestions = get_cached_species_suggestions(corrected_query)
        if corrected_cached_suggestions:
            logger.info(
                "[SPECIES SUGGEST] Using cached JSON suggestions for corrected query='%s' from original='%s'.",
                corrected_query,
                query,
            )
            corrected_json_candidates = suggestion_items_to_candidates(corrected_cached_suggestions, f"json_cache:{corrected_query}")
            ranked = rank_candidates(corrected_json_candidates, f"json_cache:{corrected_query}")[:5]
            if ranked:
                for candidate in ranked:
                    candidate["corrected_query"] = corrected_query
                    candidate["correction_score"] = correction_score
                return ranked

        effective_query = corrected_query

    # 4. Perenual species-list search. Details are fetched later for the winner.
    if not allow_external_api:
        logger.info(
            "[SPECIES SUGGEST] External Perenual search disabled for query='%s'; no DB/JSON candidates available.",
            query,
        )
        return []

    api_results = search_plant_species_api(effective_query)
    if api_results:
        cache_species_suggestions(effective_query, api_results)

    api_candidates = suggestion_items_to_candidates(api_results, "api")

    ranked = rank_candidates(api_candidates, "api")
    if effective_query != query:
        for candidate in ranked:
            candidate["corrected_query"] = effective_query
            candidate["correction_score"] = correction_score

    # =====================================
    # OPTIONAL DETAIL SNAPSHOT WARMUP
    # =====================================
    # Keep this disabled by default. Eagerly fetching details for every high
    # scoring suggestion quickly hits Perenual rate limits and can delay plant
    # creation by a minute or more. The resolver fetches details only for the
    # selected candidate.
    saved_count = 0
    if pre_cache_limit > 0:
        for i, suggestion in enumerate(ranked):
            if saved_count >= pre_cache_limit:
                logger.debug(f"[SUGGESTION CACHE] Reached pre_cache_limit ({pre_cache_limit}). Stopping further snapshot saves.")
                break

            species_id = suggestion.get("id")
            score = suggestion.get("score")

            logger.debug(f"[SUGGESTION CACHE] Processing suggestion {i+1}: ID={species_id}, Score={score}")

            should_cache_details = bool(species_id and (score or 0) > 70)

            if should_cache_details:
                logger.debug(f"[SUGGESTION CACHE] Score {score} > 70 for species ID {species_id}. Attempting to get details.")
                details = _get_species_details_from_source(species_id)

                if details and details.get("id"):
                    get_or_create_species_cache(
                        db,
                        species_id,
                        fallback_name=suggestion.get("scientific_name") or suggestion.get("common_name"),
                        api_data_override=details,
                    )
                    saved_count += 1
                    logger.debug(f"[SUGGESTION CACHE] Successfully cached details for species ID {species_id}.")
                else:
                    logger.warning(f"[SUGGESTION CACHE] Failed to get valid details for species ID {species_id}. Snapshot not saved.")
            else:
                logger.debug(f"[SUGGESTION CACHE] Species ID {species_id} or score {score} does not meet caching criteria (>70). Snapshot not saved.")

        logger.info(f"[SUGGESTION CACHE] Saved {saved_count} " f"species snapshots for '{query}' based on score criteria.")

    return ranked[:5]


def _primary_scientific_name(value) -> str | None:
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _names_match_selected_candidate(
    fetched_common_name: str | None,
    fetched_scientific_name: str | None,
    selected: dict,
    query: str,
    plant_type: str = None,
) -> bool:
    selected_scientific = selected.get("scientific_name")
    selected_common = selected.get("common_name")
    fetched_candidates = [
        {"common_name": fetched_common_name, "scientific_name": fetched_scientific_name},
        {"common_name": fetched_scientific_name, "scientific_name": fetched_common_name},
    ]

    expected_names = [name for name in [selected_scientific, selected_common, query] if name]
    for expected in expected_names:
        for fetched in fetched_candidates:
            if compute_match_score(expected, fetched, plant_type=plant_type) >= 80:
                return True

    logger.warning(
        "[SPECIES RESOLVE] Rejecting stale species ID %s: selected=(%s / %s), fetched=(%s / %s), query='%s'",
        selected.get("id"),
        selected_common,
        selected_scientific,
        fetched_common_name,
        fetched_scientific_name,
        query,
    )
    return False


def _species_matches_selected_candidate(species: PlantSpeciesCache, selected: dict, query: str, plant_type: str = None) -> bool:
    """
    Validate that details fetched for a selected Perenual ID still represent the
    selected suggestion. This protects against stale file-cache entries where an
    ID points to a different species than the cached search result claimed.
    """
    return _names_match_selected_candidate(
        species.common_name,
        species.scientific_name,
        selected,
        query,
        plant_type=plant_type,
    )


def _is_exact_selected_match(best_match: dict) -> bool:
    return bool(best_match.get("exact_scientific_match") or best_match.get("exact_common_match"))


def _is_trusted_selected_match(best_match: dict) -> bool:
    return _is_exact_selected_match(best_match) or (best_match.get("score") or 0) >= 90


def _should_defer_no_cache_to_next_query(best_match: dict) -> bool:
    """
    Exact scientific-name hits can be synonyms or stale Perenual IDs. If details
    cannot validate them, let the ordered resolver try the common/user query
    before giving up without caching incomplete species data.
    """
    return bool(best_match.get("exact_scientific_match") and not best_match.get("exact_common_match"))


def _skip_species_cache_without_details(best_match: dict, reason: str) -> None:
    """Avoid persisting species-list-only data as authoritative species cache."""
    species_id = best_match.get("id")
    scientific_name = best_match.get("scientific_name") or best_match.get("common_name") or "Unknown Species"
    logger.warning(
        "[SPECIES RESOLVE] Not caching species_id=%s name=%s because Perenual details were unavailable (%s).",
        species_id,
        scientific_name,
        reason,
    )


def _get_species_from_trusted_search_match(
    db: Session,
    best_match: dict,
    query: str,
    plant_type: str = None,
    *,
    force_refresh: bool = False,
    ignore_details_backoff: bool = False,
) -> PlantSpeciesCache | None:
    """
    Resolve exact/high-confidence matches without allowing broad fallback drift.

    The selected Perenual ID must validate through details or a full snapshot.
    Species-list-only data is not persisted because it can become sticky and
    prevent later enrichment.
    """
    species_id = best_match.get("id")
    if not species_id:
        return None

    cached = db.query(PlantSpeciesCache).filter(PlantSpeciesCache.external_species_id == str(species_id)).first()
    if (
        cached
        and _species_matches_selected_candidate(cached, best_match, query, plant_type=plant_type)
        and (not cached.data or cached.data.get("details_status") != "unavailable")
        and not force_refresh
    ):
        return cached

    snapshot = load_species_snapshot(species_id)
    if snapshot and snapshot.get("id") and snapshot.get("snapshot_quality") != "search_result_only":
        if _names_match_selected_candidate(
            snapshot.get("common_name"),
            _primary_scientific_name(snapshot.get("scientific_name")),
            best_match,
            query,
            plant_type=plant_type,
        ):
            return get_or_create_species_cache(
                db,
                species_id,
                fallback_name=best_match.get("scientific_name"),
                force_refresh=force_refresh,
                api_data_override=None if force_refresh else snapshot,
            )
        remove_cached_species_suggestion(query, species_id)
        return None

    details = _get_species_details_from_source(
        species_id,
        ignore_backoff=ignore_details_backoff,
        max_retries=2,
        force_api=force_refresh,
    )
    if details and details.get("id"):
        if _names_match_selected_candidate(
            details.get("common_name"),
            _primary_scientific_name(details.get("scientific_name")),
            best_match,
            query,
            plant_type=plant_type,
        ):
            return get_or_create_species_cache(
                db,
                species_id,
                fallback_name=best_match.get("scientific_name"),
                force_refresh=force_refresh,
                api_data_override=details,
            )
        remove_cached_species_suggestion(query, species_id)
        return None

    if _should_defer_no_cache_to_next_query(best_match):
        best_match["_deferred_no_cache_fallback"] = True
        logger.warning(
            "[SPECIES RESOLVE] Details unavailable for exact scientific match id=%s query='%s'; "
            "deferring to next ordered query before giving up without cache.",
            species_id,
            query,
        )
        return None

    if cached and _species_matches_selected_candidate(cached, best_match, query, plant_type=plant_type) and not _is_search_result_only_payload(cached.data):
        logger.warning(
            "[SPECIES RESOLVE] Using existing validated species cache id=%s after details retry failed.",
            species_id,
        )
        return cached

    _skip_species_cache_without_details(best_match, "trusted match details unavailable")
    return None


def _get_validated_species_for_match(
    db: Session,
    best_match: dict,
    query: str,
    plant_type: str = None,
    *,
    force_refresh: bool = False,
    ignore_details_backoff: bool = False,
) -> PlantSpeciesCache | None:
    if _is_trusted_selected_match(best_match):
        return _get_species_from_trusted_search_match(
            db,
            best_match,
            query,
            plant_type=plant_type,
            force_refresh=force_refresh,
            ignore_details_backoff=ignore_details_backoff,
        )

    details = _get_species_details_from_source(best_match["id"], ignore_backoff=ignore_details_backoff, force_api=force_refresh)
    if not details or not details.get("id"):
        logger.warning(
            "[SPECIES RESOLVE] Could not validate species ID %s for query='%s'; keeping suggestion for future retry.",
            best_match.get("id"),
            query,
        )
        return None

    if not _names_match_selected_candidate(
        details.get("common_name"),
        _primary_scientific_name(details.get("scientific_name")),
        best_match,
        query,
        plant_type=plant_type,
    ):
        remove_cached_species_suggestion(query, best_match.get("id"))
        return None

    species = get_or_create_species_cache(
        db,
        best_match["id"],
        fallback_name=best_match.get("scientific_name"),
        force_refresh=force_refresh,
        api_data_override=details,
    )
    if not species:
        return None

    if _species_matches_selected_candidate(species, best_match, query, plant_type=plant_type):
        return species

    remove_cached_species_suggestion(query, best_match.get("id"))
    return None


def _select_species_match(query: str, suggestions: list[dict], threshold: int = 75) -> dict | None:
    """Pick the highest-ranked candidate only when it meets the resolver threshold."""
    if not suggestions:
        return None

    best_match = suggestions[0]
    score = best_match.get("score") or 0
    logger.info(
        "[SPECIES RESOLVE] Best ranked candidate for '%s': %s (%s), score=%s.",
        query,
        best_match.get("common_name"),
        best_match.get("scientific_name"),
        score,
    )

    if score >= threshold:
        return best_match

    logger.info(
        "[SPECIES RESOLVE] Best candidate for '%s' is below threshold %s; skipping details fetch.",
        query,
        threshold,
    )
    return None


def resolve_species(
    db: Session,
    plant_name: str,
    plant_type: str = None,
    *,
    force_refresh: bool = False,
    preferred_scientific_names: list[str] | None = None,
    preferred_common_names: list[str] | None = None,
    preferred_genus: str | None = None,
    preferred_family: str | None = None,
) -> int | None:
    """
    Main entry used by plant_service
    to get an internal species_id.
    """

    logger.info(f"[SPECIES RESOLVE] " f"Attempting to resolve species " f"for '{plant_name}' " f"(type: {plant_type}).")

    external_block_reason = _perenual_request_block_reason(f"{PERENUAL_BASE_URL}/species-list")
    if external_block_reason:
        logger.warning(
            "[SPECIES RESOLVE] Perenual external search is unavailable (%s). Using local DB/cache suggestions only.",
            external_block_reason,
        )

    suggestions = suggest_species(
        db,
        plant_name,
        plant_type,
        allow_external_api=external_block_reason is None,
        preferred_scientific_names=preferred_scientific_names,
        preferred_common_names=preferred_common_names,
        preferred_genus=preferred_genus,
        preferred_family=preferred_family,
    )

    best_match = _select_species_match(plant_name, suggestions, threshold=75)

    # =====================================
    # NO GOOD MATCH
    # =====================================

    if not best_match:

        logger.info(f"[SPECIES RESOLVE] " f"No confident best match found " f"for '{plant_name}'.")

        return None

    logger.info(
        f"[SPECIES RESOLVE] " f"Best match for '{plant_name}': " f"{best_match['common_name']} " f"(ID: {best_match['id']}, " f"Score: {best_match['score']})."
    )

    # =====================================
    # CREATE / LOAD CACHE
    # =====================================

    try:

        species = _get_validated_species_for_match(db, best_match, plant_name, plant_type=plant_type, force_refresh=force_refresh)
        if not species and best_match.get("_deferred_no_cache_fallback"):
            _skip_species_cache_without_details(best_match, "single-query deferred details unavailable")

        if species and not _resolved_species_matches_preferred_scientific_identity(species, preferred_scientific_names):
            logger.warning(
                "[SPECIES RESOLVE] Rejecting resolved species id=%s common=%s scientific=%s because it does not match preferred scientific identity %s.",
                species.external_species_id,
                species.common_name,
                species.scientific_name,
                preferred_scientific_names,
            )
            return None

        return species.id if species else None

    except Exception as e:

        logger.error(f"[SPECIES RESOLVE] " f"Failed to get or create " f"species cache for " f"{best_match['id']}: {e}")

        return None


def _preferred_scientific_names_from_queries(
    queries: list[str],
    preferred_common_names: list[str] | None = None,
    preferred_genus: str | None = None,
) -> list[str]:
    """
    Keep the original taxonomy target available while trying later common/genus
    fallbacks. The first ordered query is produced from the normalized accepted
    scientific name when taxonomy data is available.
    """
    preferred_common_set = {_normalized_name(name) for name in preferred_common_names or [] if name}
    result: list[str] = []
    seen: set[str] = set()

    for query in queries:
        query = str(query or "").strip()
        key = _normalized_name(query)
        if len(query.split()) < 2 or key in preferred_common_set:
            continue
        if preferred_genus and not key.startswith(_normalized_name(preferred_genus)):
            # This still allows known synonym genera when preferred_genus is not
            # supplied, but prevents multi-word common names from being treated
            # as scientific names in the normal taxonomy path.
            if not result:
                continue
        if key not in seen:
            result.append(query)
            seen.add(key)

    return result


def _normalized_name(value: str | None) -> str:
    return str(value or "").strip().lower()


def _canonical_scientific_key(value: str | None) -> str:
    value = _normalized_name(value)
    if not value:
        return ""

    value = value.replace("×", " x ")
    value = value.replace("'", " ")
    value = value.replace('"', " ")
    value = re.sub(r"\(([^)]*?)\s+group\)", r"\1", value)
    value = re.sub(r"\(([^)]*)\)", r"\1", value)
    value = re.sub(r"\b(var\.?|subsp\.?|ssp\.?|spp\.?|forma|f\.|cv\.)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _scientific_keys_compatible(left: str | None, right: str | None) -> bool:
    left_key = _canonical_scientific_key(left)
    right_key = _canonical_scientific_key(right)
    if not left_key or not right_key:
        return False

    left_parts = left_key.split()
    right_parts = right_key.split()
    left_binomial = " ".join(left_parts[:2]) if len(left_parts) >= 2 else ""
    right_binomial = " ".join(right_parts[:2]) if len(right_parts) >= 2 else ""
    genus_level_match = bool(left_parts and right_parts and left_parts[0] == right_parts[0]) and (len(left_parts) == 1 or len(right_parts) == 1)

    return bool(
        left_key == right_key
        or left_key.startswith(right_key)
        or right_key.startswith(left_key)
        or (left_binomial and left_binomial == right_binomial)
        or genus_level_match
    )


def _candidate_is_safe_variant_fallback(
    primary: dict,
    candidate: dict,
    preferred_scientific_names: list[str] | None,
    preferred_common_names: list[str] | None,
) -> bool:
    if not candidate.get("id") or candidate.get("id") == primary.get("id"):
        return False

    if (candidate.get("score") or 0) < 70:
        return False

    candidate_common = _normalized_name(candidate.get("common_name"))
    primary_common = _normalized_name(primary.get("common_name"))
    candidate_scientific = _normalized_name(candidate.get("scientific_name"))

    for preferred_scientific_name in preferred_scientific_names or []:
        if _scientific_keys_compatible(candidate_scientific, preferred_scientific_name):
            return True

    if preferred_scientific_names:
        return False

    preferred_common_set = {_normalized_name(name) for name in preferred_common_names or [] if name}
    if candidate_common and (candidate_common == primary_common or candidate_common in preferred_common_set):
        return True

    return False


def _candidate_matches_preferred_identity(
    candidate: dict,
    preferred_scientific_names: list[str] | None,
    preferred_common_names: list[str] | None,
) -> bool:
    preferred_scientific_names = preferred_scientific_names or []
    preferred_common_names = preferred_common_names or []

    if not preferred_scientific_names and not preferred_common_names:
        return True

    candidate_scientific = _normalized_name(candidate.get("scientific_name"))
    candidate_common = _normalized_name(candidate.get("common_name"))

    for preferred_scientific_name in preferred_scientific_names:
        if _scientific_keys_compatible(candidate_scientific, preferred_scientific_name):
            return True

    preferred_common_set = {_normalized_name(name) for name in preferred_common_names if name}
    if candidate_common and candidate_common in preferred_common_set:
        return True

    if preferred_scientific_names:
        return False

    return bool(candidate_common and candidate_common in preferred_common_set)


def _resolved_species_matches_preferred_scientific_identity(
    species: PlantSpeciesCache,
    preferred_scientific_names: list[str] | None,
) -> bool:
    preferred_scientific_names = [name for name in preferred_scientific_names or [] if name]
    if not preferred_scientific_names:
        return True

    scientific_name = _normalized_name(species.scientific_name)
    if not scientific_name or scientific_name == "unknown":
        return False

    return any(_scientific_keys_compatible(scientific_name, preferred) for preferred in preferred_scientific_names)


def _filter_ranked_by_preferred_identity(
    ranked: list[dict],
    preferred_scientific_names: list[str] | None,
    preferred_common_names: list[str] | None,
) -> list[dict]:
    if not preferred_scientific_names and not preferred_common_names:
        return ranked

    filtered = [candidate for candidate in ranked if _candidate_matches_preferred_identity(candidate, preferred_scientific_names, preferred_common_names)]

    if len(filtered) != len(ranked):
        logger.info(
            "[SPECIES SUGGEST] Filtered %s ranked candidates that did not match preferred identity scientific=%s common=%s.",
            len(ranked) - len(filtered),
            preferred_scientific_names,
            preferred_common_names,
        )

    return filtered


def _safe_variant_fallback_candidates(
    primary: dict,
    suggestions: list[dict],
    preferred_scientific_names: list[str] | None,
    preferred_common_names: list[str] | None,
    limit: int = 4,
) -> list[dict]:
    candidates: list[dict] = []
    for suggestion in suggestions:
        if _candidate_is_safe_variant_fallback(primary, suggestion, preferred_scientific_names, preferred_common_names):
            candidates.append(suggestion)
        if len(candidates) >= limit:
            break
    return candidates


def _validation_candidates_for_ranked_suggestions(
    best_match: dict,
    suggestions: list[dict],
    preferred_scientific_names: list[str] | None,
    preferred_common_names: list[str] | None,
) -> list[dict]:
    candidates: list[dict] = []
    seen_ids: set[str] = set()

    def add(candidate: dict) -> None:
        species_id = str(candidate.get("id") or "")
        if species_id and species_id in seen_ids:
            return
        if species_id:
            seen_ids.add(species_id)
        candidates.append(candidate)

    add(best_match)

    for suggestion in suggestions:
        if suggestion is best_match:
            continue
        if (suggestion.get("score") or 0) == 100 and _candidate_matches_preferred_identity(
            suggestion,
            preferred_scientific_names,
            preferred_common_names,
        ):
            add(suggestion)

    for suggestion in _safe_variant_fallback_candidates(
        best_match,
        suggestions,
        preferred_scientific_names,
        preferred_common_names,
    ):
        add(suggestion)

    return candidates


def _has_full_species_snapshot(species_id) -> bool:
    snapshot = load_species_snapshot(species_id)
    return bool(snapshot and snapshot.get("id") and snapshot.get("snapshot_quality") != "search_result_only")


def _candidate_detail_unavailable_reason(candidate: dict) -> str | None:
    species_id = candidate.get("id")
    if not species_id:
        return "missing Perenual species id"

    if _has_full_species_snapshot(species_id):
        return None

    plan_block_reason = _species_details_plan_block_reason(species_id)
    if plan_block_reason:
        return plan_block_reason

    details_url = f"{PERENUAL_BASE_URL}/species/details/{species_id}"
    details_backoff_remaining = _endpoint_backoff_remaining(details_url)
    if details_backoff_remaining > 0:
        return f"details endpoint 429 backoff active for {details_backoff_remaining:.0f} more seconds"

    return None


def _candidate_has_fetchable_details(candidate: dict) -> bool:
    return _candidate_detail_unavailable_reason(candidate) is None


def _is_details_backoff_reason(reason: str | None) -> bool:
    return bool(reason and "details endpoint 429 backoff active" in reason)


def _scientific_binomial(value: str | None) -> str | None:
    key = _canonical_scientific_key(value)
    parts = key.split()
    if len(parts) >= 2:
        return " ".join(parts[:2])
    return None


def _species_cache_candidate(species: PlantSpeciesCache) -> dict:
    return normalize_candidate(
        {
            "id": int(species.external_species_id),
            "common_name": species.common_name,
            "scientific_name": species.scientific_name,
            "is_edible": species.is_edible,
            "is_fruit": species.is_fruit,
            "is_veg": species.is_veg,
            "growth_rate": species.growth_rate,
            "type": (species.data.get("type") if species.data else None),
            "genus": (species.data.get("genus") if species.data else None),
            "family": (species.data.get("family") if species.data else None),
        },
        "db_cache",
    )


def _find_saved_species_for_identity(
    db: Session,
    preferred_scientific_names: list[str] | None,
    preferred_common_names: list[str] | None,
    preferred_genus: str | None = None,
    preferred_family: str | None = None,
) -> PlantSpeciesCache | None:
    preferred_scientific_names = preferred_scientific_names or []
    preferred_common_names = preferred_common_names or []

    candidate_filters = []
    for common_name in preferred_common_names:
        common_name = str(common_name or "").strip()
        if common_name:
            candidate_filters.append(PlantSpeciesCache.common_name.ilike(common_name))

    for scientific_name in preferred_scientific_names:
        binomial = _scientific_binomial(scientific_name)
        if binomial:
            candidate_filters.append(PlantSpeciesCache.scientific_name.ilike(f"{binomial}%"))

    if preferred_genus:
        candidate_filters.append(PlantSpeciesCache.scientific_name.ilike(f"{preferred_genus}%"))

    if not candidate_filters:
        return None

    saved_species = db.query(PlantSpeciesCache).filter(or_(*candidate_filters)).all()
    ranked: list[tuple[int, PlantSpeciesCache]] = []

    for species in saved_species:
        if _is_search_result_only_payload(species.data):
            continue

        candidate = _species_cache_candidate(species)
        if not _candidate_matches_preferred_identity(candidate, preferred_scientific_names, preferred_common_names):
            continue

        score = compute_match_score(
            preferred_common_names[0] if preferred_common_names else (preferred_scientific_names[0] if preferred_scientific_names else species.common_name),
            candidate,
            preferred_scientific_names=preferred_scientific_names,
            preferred_common_names=preferred_common_names,
            preferred_genus=preferred_genus,
            preferred_family=preferred_family,
        )
        ranked.append((score, species))

    if not ranked:
        return None

    ranked.sort(key=lambda item: item[0], reverse=True)
    species = ranked[0][1]
    logger.info(
        "[SPECIES RESOLVE] Using saved species from DB before Perenual: species_id=%s common=%s scientific=%s internal_id=%s.",
        species.external_species_id,
        species.common_name,
        species.scientific_name,
        species.id,
    )
    return species


def resolve_species_by_queries(
    db: Session,
    queries: list[str],
    plant_type: str = None,
    *,
    force_refresh: bool = False,
    preferred_common_names: list[str] | None = None,
    preferred_genus: str | None = None,
    preferred_family: str | None = None,
) -> int | None:
    """
    Compatibility wrapper for older callers that pass taxonomy-expanded queries.

    Perenual resolution now uses the user's/common name as the search term and
    uses taxonomy as ranking and identity-validation context, not as an ordered
    external search plan.
    """
    query = next((name for name in preferred_common_names or [] if str(name or "").strip()), None)
    if not query:
        query = next((name for name in queries if str(name or "").strip()), None)
    if not query:
        return None

    preferred_scientific_names = _preferred_scientific_names_from_queries(
        queries,
        preferred_common_names=preferred_common_names,
        preferred_genus=preferred_genus,
    )
    return resolve_species(
        db,
        str(query).strip(),
        plant_type=plant_type,
        force_refresh=force_refresh,
        preferred_scientific_names=preferred_scientific_names,
        preferred_common_names=preferred_common_names,
        preferred_genus=preferred_genus,
        preferred_family=preferred_family,
    )
