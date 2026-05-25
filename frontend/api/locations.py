"""
API client for location-related operations in the Smart Urban Farming application.

Key Point:
Provides functions to interact with the backend's location management endpoints,
enabling CRUD operations for plant locations.

Responsibilities:
- Abstract the API endpoint paths and HTTP methods for location operations.
- Facilitate data exchange for creating, retrieving, updating, and deleting location entries.

Architecture Role:
- Acts as a dedicated interface for the frontend to manage location data on the backend.
- Simplifies API calls for location-related features.

Layer Interaction:
- Communicates with: `api.client.api_request` (for underlying HTTP requests).
- Called by: Frontend pages and components that need to interact with location data.

Data Flow:
Frontend UI action (e.g., "Add Location", "View Locations")
        ↓
Corresponding function in `frontend/api/locations.py` is called
        ↓
`api_request()` sends the HTTP request to the backend `/locations` endpoints
        ↓
Backend processes the request and returns data or status
        ↓
Data (e.g., list of locations, a single location object) is returned to the frontend UI
"""

# frontend/api/locations.py
# Location API helpers for CRUD operations.

from typing import Any

from api.client import api_request


def get_locations() -> list[dict[str, Any]]:
    return api_request("GET", "/locations/") or []


def create_location(payload: dict[str, Any]) -> dict[str, Any]:
    return api_request("POST", "/locations/", json=payload)


def update_location(location_id: int, payload: dict[str, Any]) -> dict[str, Any]:
    return api_request("PATCH", f"/locations/{location_id}", json=payload)


def delete_location(location_id: int) -> dict[str, Any]:
    return api_request("DELETE", f"/locations/{location_id}")
