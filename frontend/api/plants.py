# frontend/api/plants.py
# Plant API helpers.
# - CRUD wrappers for plants.
# - Companion recommendation and duplication endpoints.

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
