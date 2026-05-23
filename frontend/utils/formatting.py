# frontend/utils/formatting.py
# Shared display formatting helpers.
# - Dates, plant names, Prolog atom keys, and location select options.

from __future__ import annotations

from typing import Any

import streamlit as st


def format_date(value: Any) -> str:
    if not value:
        return "Not recorded"
    return str(value).split("T")[0]


def display_plant_name(name: str) -> str:
    return name.replace("_", " ").title()


def plant_name_key(name: str) -> str:
    return " ".join(name.replace("_", " ").lower().split())


def companion_atom_key(name: str) -> str:
    return plant_name_key(name).replace(" ", "_")


def plant_display_name(plant: dict[str, Any]) -> str:
    species = plant.get("species") or {}
    species_name = species.get("common_name") or species.get("scientific_name")

    if species_name and species_name.lower() != plant.get("name", "").lower():
        return f"{plant.get('name')} - {species_name}"

    return plant.get("name", "Unnamed plant")


def location_options() -> tuple[list[str], dict[str, int | None]]:
    options = ["No location"]
    mapping: dict[str, int | None] = {"No location": None}

    for location in st.session_state.get("locations", []):
        label = f"{location['name']} ({location.get('environment_type') or 'unspecified'})"
        options.append(label)
        mapping[label] = location["id"]

    return options, mapping
