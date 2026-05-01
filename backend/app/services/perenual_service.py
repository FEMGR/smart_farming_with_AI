"""
Service layer for external API integration (Perenual).

Key Point:
Handles communication with the Perenual API to retrieve plant species data.

Responsibilities:
- Search plant species by query
- Retrieve detailed species information
- Extract scientific names from API responses
- Normalize API data for internal use
- Handle API errors and timeouts

Architecture Role:
- Integration layer between external plant data source and internal system
- Supplies species data to services and matching utilities

Layer Interaction:
- Communicates with: External API (Perenual)
- Called by: Services (e.g., plant_service, species_matching)

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
from app.core.config import PERENUAL_API_KEY

BASE_URL = "https://perenual.com/api/v2"


def search_plant_species(query: str):
    url = f"{BASE_URL}/species-list"
    params = {"key": PERENUAL_API_KEY, "q": query}

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", [])

            # Add placeholders so the Schema/Ranker don't crash
            for item in data:
                item["edible"] = "unknown"
                item["growth_rate"] = "unknown"
            return data
        return []
    except Exception:
        return []


def get_species_details(species_id: int):
    """Retrieve detailed care information for a specific species ID."""
    url = f"{BASE_URL}/species/details/{species_id}"
    params = {"key": PERENUAL_API_KEY}
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None


def get_plant_scientific_name(query: str):
    url = f"{BASE_URL}/species-list"
    params = {"key": PERENUAL_API_KEY, "q": query}

    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                # Perenual returns scientific_name as a list: ["Name"]
                # We take the first one or default to "Unknown"
                names = data[0].get("scientific_name", [])
                return names[0] if names else "Unknown Species"
        return "Unknown Species"
    except Exception:
        return "Unknown Species"
