"""
API client for plant-related operations in the Smart Urban Farming application.

Key Point:
Provides a set of functions to interact with the backend's plant management endpoints,
including CRUD operations, companion plant recommendations, and plant duplication.

Responsibilities:
- Abstract the API endpoint paths and HTTP methods for plant operations.
- Facilitate data exchange for creating, retrieving, updating, and deleting plant entries.
- Provide specific functions for fetching companion plant recommendations and duplicating plants.

Architecture Role:
- Acts as a dedicated interface for the frontend to manage plant data on the backend.
- Simplifies API calls for plant-related features, making them reusable and consistent.

Layer Interaction:
- Communicates with: `api.client.api_request` (for underlying HTTP requests).
- Called by: Frontend pages and components that need to interact with plant data.

Data Flow:
Frontend UI action (e.g., "Add Plant", "View Plants", "Get Recommendations")
        ↓
Corresponding function in `frontend/api/plants.py` is called
        ↓
`api_request()` sends the HTTP request to the backend `/plants` endpoints
        ↓
Backend processes the request and returns data or status
        ↓
Data (e.g., list of plants, a single plant object, recommendations) is returned to the frontend UI
"""

# frontend/api/plants.py


from typing import Any

from api.client import api_request


def get_plants() -> list[dict[str, Any]]:
    return api_request("GET", "/plants/") or []


def create_plant(payload: dict[str, Any]) -> dict[str, Any]:
    return api_request("POST", "/plants/", json=payload)


def create_plant_with_species(payload: dict[str, Any], species_id: int) -> dict[str, Any]:
    return api_request(
        "POST",
        "/plants/with-species",
        params={"species_id": species_id},
        json=payload,
    )


def update_plant(plant_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return api_request("PATCH", f"/plants/{plant_id}", json=payload)


def delete_plant(plant_id: int) -> dict[str, Any]:
    return api_request("DELETE", f"/plants/{plant_id}")


def get_recommendations() -> dict[str, Any]:
    return api_request("GET", "/plants/recommendations")


def duplicate_plant(plant_id: int, group_id: int | None = None) -> dict:
    params = {}

    if group_id is not None:
        params["group_id"] = group_id

    return api_request(
        "POST",
        f"/plants/{plant_id}/duplicate",
        params=params,
    )
