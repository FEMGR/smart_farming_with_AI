"""
API client for irrigation-related operations in the Smart Urban Farming application.

Key Point:
Provides functions to interact with the backend's irrigation endpoints,
allowing the frontend to retrieve plants that need watering and to mark plants as watered.

Responsibilities:
- Abstract the API endpoint paths and HTTP methods for irrigation operations.
- Facilitate data exchange for checking watering needs and updating watering status.

Architecture Role:
- Acts as a dedicated interface for the frontend to manage irrigation data on the backend.
- Simplifies API calls for irrigation features.

Layer Interaction:
- Communicates with: `api.client.api_request` (for underlying HTTP requests).
- Called by: Frontend pages and components that display watering schedules or allow watering actions.

Data Flow:
Frontend UI needs to display plants requiring water
        ↓
`get_needs_water()` is called
        ↓
`api_request()` sends a GET request to the backend `/irrigation/needs-water` endpoint
        ↓
Backend processes the request and returns a list of plants needing water
        ↓
List of plants is returned to the frontend UI for display

User waters a plant (or all due plants)
        ↓
`water_plant()` or `water_all_due()` is called
        ↓
`api_request()` sends a POST request to the backend `/irrigation/water/{plant_id}` or `/irrigation/water-all` endpoint
        ↓
Backend updates the watering status
        ↓
Confirmation message or updated data is returned to the frontend UI
"""

# frontend/api/irrigation.py
# Irrigation API helpers.
# - Reads plants that need water.
# - Marks one plant or all due plants as watered.

from typing import Any

from api.client import api_request


def get_needs_water() -> list[dict[str, Any]]:
    return api_request("GET", "/irrigation/needs-water") or []


def water_plant(plant_id: int) -> dict[str, Any]:
    return api_request("POST", f"/irrigation/water/{plant_id}")


def water_all_due() -> dict[str, Any]:
    return api_request("POST", "/irrigation/water-all")
