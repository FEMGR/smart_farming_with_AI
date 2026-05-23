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
