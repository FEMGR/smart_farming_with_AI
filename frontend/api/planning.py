# frontend/api/planning.py
from api.client import api_request


def get_sections():
    return api_request("GET", "/planning/sections")


def create_section(payload: dict):
    return api_request("POST", "/planning/sections", json=payload)


def update_section(section_id: int, payload: dict):
    return api_request("PATCH", f"/planning/sections/{section_id}", json=payload)


def delete_section(section_id: int):
    return api_request("DELETE", f"/planning/sections/{section_id}")


def polyculture_preview(payload: dict):
    return api_request("POST", "/planning/polyculture-preview", json=payload)


def polyculture_confirm(payload: dict):
    return api_request("POST", "/planning/polyculture-confirm", json=payload)
