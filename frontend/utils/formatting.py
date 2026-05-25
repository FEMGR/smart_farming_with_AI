"""
Utility functions for formatting and display in the frontend.

Key Point:
Provides helper functions for consistent data presentation, such as date formatting,
plant name display, and generating UI options for locations.

Responsibilities:
- Format date strings for user-friendly display.
- Convert internal plant names (e.g., snake_case) to display-friendly titles.
- Generate unique keys for plant names, suitable for various uses (e.g., companion planting atoms).
- Create display names for plants, incorporating species information if available.
- Prepare location options for Streamlit select boxes, including display labels and corresponding IDs.

Architecture Role:
- Centralizes common formatting logic to ensure consistency across the frontend.
- Reduces code duplication in UI components.

Layer Interaction:
- Communicates with: Various Streamlit pages and components (e.g., `plants.py`, `recommendations.py`).
- Called by: Frontend UI elements that require formatted data or dynamic options.

Data Flow:
Raw data (dates, plant objects, location objects)
        ↓
Passed to formatting functions
        ↓
Formatted strings or UI-ready data structures returned
        ↓
Used by Streamlit components for rendering
"""

# frontend/utils/formatting.py


from __future__ import annotations

from typing import Any

import streamlit as st


def format_date(value: Any) -> str:
    """
    Formats a date-like value into a 'YYYY-MM-DD' string.
    Returns "Not recorded" if the value is None or empty.
    """
    if not value:
        return "Not recorded"
    return str(value).split("T")[0]


def display_plant_name(name: str) -> str:
    """
    Converts a snake_case or similar plant name string into a human-readable title.
    Example: "tomato_plant" -> "Tomato Plant"
    """
    return name.replace("_", " ").title()


def plant_name_key(name: str) -> str:
    """
    Generates a consistent, lowercase, space-separated key for a plant name.
    Useful for comparisons or dictionary keys.
    Example: "Tomato Plant" -> "tomato plant"
    """
    return " ".join(name.replace("_", " ").lower().split())


def companion_atom_key(name: str) -> str:
    """
    Generates a key suitable for companion planting atoms (snake_case lowercase).
    Example: "Tomato Plant" -> "tomato_plant"
    """
    return plant_name_key(name).replace(" ", "_")


def plant_display_name(plant: dict[str, Any]) -> str:
    """
    Generates a display name for a plant, prioritizing its common name,
    and optionally including species common/scientific name if different.
    """
    species = plant.get("species") or {}
    species_name = species.get("common_name") or species.get("scientific_name")

    if species_name and species_name.lower() != plant.get("name", "").lower():
        return f"{plant.get('name')} - {species_name}"

    return plant.get("name", "Unnamed plant")


def location_options() -> tuple[list[str], dict[str, int | None]]:
    """
    Generates a list of display options for locations and a mapping from
    display label to location ID, suitable for Streamlit select boxes.
    Includes a "No location" option.
    """
    options = ["No location"]
    mapping: dict[str, int | None] = {"No location": None}

    for location in st.session_state.get("locations", []):
        label = f"{location['name']} ({location.get('environment_type') or 'unspecified'})"
        options.append(label)
        mapping[label] = location["id"]

    return options, mapping
