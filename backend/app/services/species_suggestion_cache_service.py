"""
Service layer for saving a file-based cache of each suggested species returned with score > 50.

Key Point:
Implements a temporary caching mechanism for returned species from search queries to reduce redundant

Responsibilities:
- Store search query results (suggestions) in a local JSON file for each species ID.
- Retrieve cached suggestions based on a query.
- Implement cache expiration for individual entries.
- Manage the overall size of the cache file to prevent excessive growth.

Architecture Role:
- Supports the `perenual_service` by providing a fast lookup for recent search queries.
- Reduces load on the external Perenual API for repeated searches.

Layer Interaction:
- Communicates with: Local file system.
- Used by: `perenual_service` to store and retrieve search suggestions.

Data Flow:
`perenual_service` receives a search query
        ↓
Checks this service for cached suggestions
        ↓
If cached and valid, suggestions are returned directly
        ↓
If not cached or expired, `perenual_service` calls external API
        ↓
API results are then passed to this service for caching
        ↓
Suggestions returned to `perenual_service`
"""

# app/services/species_suggestion_cache_service.py

import json
import os
import time
from typing import List, Dict, Optional

from app.core.logger import setup_logger
from app.core.constants import SUGGESTION_CACHE_FILE, SUGGESTION_MAX_AGE_SECONDS, MAX_SUGGESTION_ENTRIES # Import constants

logger = setup_logger()

# =====================================
# CACHE MANAGEMENT
# =====================================
def ensure_cache_dir():
    """
    Ensures that the directory for the cache file exists.
    Creates the 'temp' directory if it does not already exist.
    """
    cache_dir = os.path.dirname(SUGGESTION_CACHE_FILE)
    if cache_dir: # Only create if cache_dir is not empty (i.e., not just a filename)
        os.makedirs(cache_dir, exist_ok=True)


def load_suggestion_cache() -> Dict:
    """
    Loads the entire suggestion cache from the CACHE_FILE.
    Returns:
        A dictionary representing the loaded cache. Returns an empty dictionary
        if the file does not exist or an error occurs during loading.
    """
    ensure_cache_dir()
    if not os.path.exists(SUGGESTION_CACHE_FILE):
        logger.info(f"[SUGGESTION CACHE] Cache file not found at {SUGGESTION_CACHE_FILE}. Returning empty cache.")
        return {}
    try:
        with open(SUGGESTION_CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        logger.error(f"[SUGGESTION CACHE] JSON decode error loading cache from {SUGGESTION_CACHE_FILE}: {e}. Returning empty cache.")
        return {}
    except Exception as e:
        logger.error(f"[SUGGESTION CACHE] Unexpected error loading cache from {SUGGESTION_CACHE_FILE}: {e}. Returning empty cache.")
        return {}


def save_suggestion_cache(data: Dict):
    """
    Saves the current state of the suggestion cache to the CACHE_FILE.
    Args:
        data: The dictionary representing the cache to be saved.
    """
    ensure_cache_dir()
    try:
        with open(SUGGESTION_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"[SUGGESTION CACHE] Failed to save cache to {SUGGESTION_CACHE_FILE}: {e}")


def cleanup_cache(cache: Dict) -> Dict:
    """
    Cleans up the suggestion cache by removing expired entries and
    enforcing the maximum number of entries.
    Args: The current cache dictionary.
    Returns:A new dictionary with cleaned-up cache entries.
    """
    now = time.time()
    cleaned = {}

    # Remove expired entries
    for key, value in cache.items():
        timestamp = value.get("timestamp", 0)
        if now - timestamp < SUGGESTION_MAX_AGE_SECONDS:
            cleaned[key] = value
        else:
            logger.debug(f"[SUGGESTION CACHE] Expired entry for query '{key}' removed during cleanup.")

    # Enforce maximum number of entries by keeping the most recent ones
    if len(cleaned) > MAX_SUGGESTION_ENTRIES:
        logger.info(f"[SUGGESTION CACHE] Cache size ({len(cleaned)}) exceeds MAX_SUGGESTION_ENTRIES ({MAX_SUGGESTION_ENTRIES}). Trimming oldest entries.")
        sorted_items = sorted(
            cleaned.items(),
            key=lambda x: x[1].get("timestamp", 0),
            reverse=True  # Sort by most recent first
        )
        cleaned = dict(sorted_items[:MAX_SUGGESTION_ENTRIES])

    return cleaned


def cache_species_suggestions(
    query: str,
    suggestions: List[Dict]
):
    """
    Adds or updates a list of species suggestions for a given query in the cache.
    """
    cache = load_suggestion_cache()
    cache = cleanup_cache(cache)  # Clean up before adding new entry

    cache[query.lower()] = {
        "timestamp": time.time(),
        "suggestions": suggestions
    }

    save_suggestion_cache(cache)

    logger.info(
        f"[SUGGESTION CACHE] Cached {len(suggestions)} suggestions for query: '{query}'"
    )


def get_cached_species_suggestions(
    query: str
) -> Optional[List[Dict]]:
    """
    Retrieves cached species suggestions for a given query.
    Args:The search query string.
    Returns: A dictionaries representing the cached suggestions if found and valid,otherwise None.
    """
    cache = load_suggestion_cache()
    item = cache.get(query.lower())

    if not item:
        logger.debug(f"[SUGGESTION CACHE] No cache entry found for query: '{query}'")
        return None

    age = time.time() - item.get("timestamp", 0)

    if age > SUGGESTION_MAX_AGE_SECONDS:
        logger.info(f"[SUGGESTION CACHE] Cache entry for query '{query}' is expired.")
        # Optionally remove expired entry immediately, though cleanup_cache handles it too
        # del cache[query.lower()]
        # save_suggestion_cache(cache)
        return None

    logger.info(
        f"[SUGGESTION CACHE] Cache hit for query: '{query}'"
    )

    return item.get("suggestions")
