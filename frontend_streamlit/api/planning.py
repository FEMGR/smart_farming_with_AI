"""
Planning API helpers for Streamlit pages.

Key Point:
Wraps FastAPI planning endpoints used by the farm section and polyculture
planning screens.
"""

# frontend_streamlit/api/planning.py
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


def get_polyculture_plans():
    return api_request("GET", "/planning/polyculture-plans")


def delete_polyculture_plan(crop_plan_id: int):
    return api_request("DELETE", f"/planning/polyculture-plans/{crop_plan_id}")


def polyculture_confirm(payload: dict):
    return api_request("POST", "/planning/polyculture-confirm", json=payload)
