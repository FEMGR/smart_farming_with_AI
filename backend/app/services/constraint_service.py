"""
Service layer for FastAPI (Plant Constraints and Compatibility).

Key Point:
Manages the rules and logic for determining environmental compatibility between plants.

Responsibilities:
- Normalize various plant environmental requirements (water, sunlight, soil).
- Extract species-specific constraint data for individual plants.
- Implement compatibility checks for water, sunlight, and soil between plant pairs.
- Filter and validate plant compatibility pairs based on environmental constraints.

Architecture Role:
- Provides a central module for evaluating if plants can co-exist based on their needs.
- Delegates data normalization to internal helper functions.

Layer Interaction:
- Communicates with: Models (Plant, Species).
- Called by: Positioning service, Grouping service, Routes (for compatibility checks).

Data Flow:
Plant objects received for compatibility assessment
        ↓
Environmental constraints (water, sunlight, soil) extracted and normalized for each plant
        ↓
Compatibility rules applied to plant pairs
        ↓
Boolean result (compatible/not compatible) or filtered list of valid pairs returned
"""

# app/services/constraint_service.py

from typing import List
from app.models.plant import Plant
from app.utils.prolog_normalizer import to_prolog_atom

# ===============================
# NORMALIZATION
# ===============================


def normalize_sunlight(value: str) -> str:
    if not value:
        return "unknown"

    v = value.lower()

    if "full" in v:
        return "full_sun"
    if "partial" in v:
        return "partial"
    if "shade" in v:
        return "shade"

    return "unknown"


def normalize_water(value: str) -> str:
    if not value:
        return "medium"

    v = value.lower()

    if "frequent" in v or "high" in v:
        return "high"
    if "minimum" in v or "low" in v:
        return "low"
    if "average" in v:
        return "medium"

    return "medium"


def normalize_soil(value: str) -> str:
    if not value:
        return "unknown"

    v = value.lower()

    if "well-drained" in v:
        return "well_drained"
    if "loamy" in v:
        return "loamy"
    if "sandy" in v:
        return "sandy"

    return "unknown"


# ===============================
# EXTRACT SPECIES DATA
# ===============================


def get_species_constraints(plant: Plant):
    if not plant.species:
        return {
            "water": "medium",
            "sunlight": "unknown",
            "soil": "unknown",
        }

    return {
        "water": normalize_water(plant.species.watering),
        "sunlight": normalize_sunlight(plant.species.sunlight_requirement),
        "soil": normalize_soil(plant.species.recommended_soil),
    }


# ===============================
# COMPATIBILITY RULES
# ===============================

WATER_COMPATIBILITY = {
    "high": ["high", "medium"],
    "medium": ["high", "medium", "low"],
    "low": ["low", "medium"],
}

SUNLIGHT_COMPATIBILITY = {
    "full_sun": ["full_sun"],
    "partial": ["partial", "shade"],
    "shade": ["shade", "partial"],
}


def is_water_compatible(p1, p2) -> bool:
    c1 = get_species_constraints(p1)
    c2 = get_species_constraints(p2)

    return c2["water"] in WATER_COMPATIBILITY.get(c1["water"], [])


def is_sunlight_compatible(p1, p2) -> bool:
    c1 = get_species_constraints(p1)
    c2 = get_species_constraints(p2)

    return c2["sunlight"] in SUNLIGHT_COMPATIBILITY.get(c1["sunlight"], [])


def is_soil_compatible(p1, p2) -> bool:
    c1 = get_species_constraints(p1)
    c2 = get_species_constraints(p2)

    # simple rule for now
    if c1["soil"] == "unknown" or c2["soil"] == "unknown":
        return True

    return c1["soil"] == c2["soil"]


def is_fully_compatible(p1, p2) -> bool:
    return is_water_compatible(p1, p2) and is_sunlight_compatible(p1, p2) and is_soil_compatible(p1, p2)


# ===============================
# FILTER PROLOG OUTPUT
# ===============================


def plant_to_prolog_atom(plant: Plant) -> str:
    return to_prolog_atom(
        {
            "name": plant.name,
            "species": (
                {
                    "common_name": plant.species.common_name if plant.species else None,
                    "scientific_name": plant.species.scientific_name if plant.species else None,
                }
                if plant.species
                else None
            ),
        }
    )


def filter_valid_pairs(plants: List[Plant], pairs: List[str]) -> List[str]:
    """
    pairs = ["tomato-basil", "cabbage-tomato"]
    """

    plant_map = {plant_to_prolog_atom(p): p for p in plants}

    valid = []

    for pair in pairs:
        try:
            p1_name, p2_name = pair.split("-")

            p1 = plant_map.get(p1_name)
            p2 = plant_map.get(p2_name)

            if not p1 or not p2:
                continue

            if is_fully_compatible(p1, p2):
                valid.append(pair)

        except Exception:
            continue

    return valid
