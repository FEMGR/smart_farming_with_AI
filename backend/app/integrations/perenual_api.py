"""
Database model for Plant Species Cache.

Key Point:
Stores normalized plant species data retrieved from external APIs (e.g., Perenual).

Responsibilities:
- Persist species-level plant data (scientific name, sunlight, soil, etc.)
- Avoid duplicate external API calls through caching
- Serve as a single source of truth for species-related information
- Support linking multiple plant instances to one species record

Architecture Role:
- Data normalization layer separating plant instances from species knowledge
- Enables scalable integration with external plant data providers

Layer Interaction:
- Communicates with: External API integration (Perenual), Plant model
- Used by: Services (plant creation, enrichment, caching logic)

Data Flow:
External API response fetched
        ↓
Data normalized into structured format
        ↓
Stored in species cache table
        ↓
Plant instances reference species via foreign key
        ↓
Cached data reused for future operations
"""


#app/integrations/perenual_api.py

import requests
from typing import List, Dict
from app.core.config import PERENUAL_API_KEY

BASE_URL = "https://perenual.com/api/v2"


# =========================================
# SEARCH SPECIES (PHASE 1)
# =========================================
def search_species(query: str, limit: int = 5) -> List[Dict]:
    """
    Search plant species by name.
    Returns:
        List of dicts:
        [
            {
                "id": int,
                "common_name": str,
                "scientific_name": str
            }
        ]
    """
    url = f"{BASE_URL}/species-list"
    params = {
        "key": PERENUAL_API_KEY,
        "q": query
    }

    try:
        response = requests.get(url, params=params, timeout=5)

        if response.status_code != 200:
            return []

        data = response.json().get("data", [])

        results = []

        for plant in data[:limit]:
            scientific_names = plant.get("scientific_name", [])

            results.append({
                "id": plant.get("id"),
                "common_name": plant.get("common_name", "Unknown"),
                "scientific_name": scientific_names[0] if scientific_names else "Unknown"
            })

        return results

    except Exception:
        return []


# =========================================
# GET SPECIES DETAILS
# =========================================
def get_species_details(species_id: int) -> Dict:
    """
    Fetch detailed plant data from Perenual.
    """
    url = f"{BASE_URL}/species/details/{species_id}"
    params = {"key": PERENUAL_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return {}
        return response.json()
    except Exception:
        return {}

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

    # ===============================
    # FIXED SCIENTIFIC NAME HANDLING
    # ===============================
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

        "sunlight": safe_join(api_data.get("sunlight")),
        "soil": safe_join(api_data.get("soil")),
        "propagation": safe_join(api_data.get("propagation")),
        "pest_susceptibility": safe_join(api_data.get("pest_susceptibility")),

        "watering_interval_days": map_watering(
            api_data.get("watering", "Average")
        ),
    }

