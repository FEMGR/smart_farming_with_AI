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
