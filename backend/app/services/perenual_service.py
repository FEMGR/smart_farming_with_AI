import requests
import os
from app.core.config import PERENUAL_API_KEY

BASE_URL = "https://perenual.com/api/v2"

def search_plant_species(query: str):
    """Search for a plant species by common or scientific name."""
    url = f"{BASE_URL}/species-list"
    params = {
        "key": PERENUAL_API_KEY,
        "q": query
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
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
