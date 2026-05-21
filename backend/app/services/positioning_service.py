# app/services/positioning_service.py

from typing import List, Optional, Tuple

# ===============================
# NORMALIZATION
# ===============================


def normalize_sunlight(value: Optional[str]) -> str:
    if not value:
        return "unknown"

    value = value.lower()

    if "full" in value:
        return "full_sun"

    if "partial" in value or "part shade" in value:
        return "partial_sun"

    if "shade" in value:
        return "shade"

    return "unknown"


def normalize_water(value: Optional[str], interval_days: Optional[int] = None) -> str:
    if value:
        value = value.lower()

        if "frequent" in value:
            return "high"

        if "average" in value:
            return "medium"

        if "minimum" in value or "low" in value:
            return "low"

    if interval_days is not None:
        if interval_days <= 2:
            return "high"

        if interval_days <= 5:
            return "medium"

        return "low"

    return "medium"


def get_zone(plant: dict) -> str:
    sunlight = normalize_sunlight(plant.get("sunlight"))
    water = normalize_water(
        plant.get("watering"),
        plant.get("watering_interval_days"),
    )

    return f"{sunlight}_{water}_water"


# ===============================
# PAIR HELPERS
# ===============================


def reverse_pair(pair: str) -> str:
    try:
        a, b = pair.split("-")
        return f"{b}-{a}"
    except ValueError:
        return pair


def is_avoid_pair(name1: str, name2: str, avoid_pairs: List[str]) -> bool:
    pair = f"{name1.lower()}-{name2.lower()}"
    return pair in avoid_pairs or reverse_pair(pair) in avoid_pairs


def distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


# ===============================
# SHADE SUPPORT
# ===============================


def can_provide_shade(provider: dict, receiver: dict) -> bool:
    provider_height = provider.get("max_height_ft") or 0
    receiver_height = receiver.get("max_height_ft") or 0

    provider_sun = normalize_sunlight(provider.get("sunlight"))
    receiver_sun = normalize_sunlight(receiver.get("sunlight"))

    return provider_height > receiver_height and provider_sun == "full_sun" and receiver_sun in ["partial_sun", "shade"]


# ===============================
# POSITION VALIDATION
# ===============================


def is_position_valid(
    plant: dict,
    x: int,
    y: int,
    placements: List[dict],
    avoid_pairs: List[str],
    min_avoid_distance: int = 2,
) -> bool:
    for placed in placements:
        if is_avoid_pair(plant["name"], placed["name"], avoid_pairs):
            if distance((x, y), (placed["x"], placed["y"])) < min_avoid_distance:
                return False

    return True


def find_next_position(
    plant: dict,
    grid_width: int,
    grid_height: int,
    occupied: set,
    placements: List[dict],
    avoid_pairs: List[str],
) -> Optional[Tuple[int, int]]:
    for y in range(grid_height):
        for x in range(grid_width):
            if (x, y) in occupied:
                continue

            if is_position_valid(
                plant=plant,
                x=x,
                y=y,
                placements=placements,
                avoid_pairs=avoid_pairs,
            ):
                return x, y

    return None


# ===============================
# MAIN LAYOUT GENERATOR
# ===============================


def generate_layout(
    groups: List[dict],
    recommended_pairs: List[str],
    avoid_pairs: List[str],
    grid_width: int = 10,
    grid_height: int = 10,
) -> dict:
    placements = []
    occupied = set()
    warnings = []
    shade_relationships = []

    for group in groups:
        plants = group.get("plants", [])

        # Tall plants first: useful for shade support
        plants = sorted(
            plants,
            key=lambda p: p.get("max_height_ft") or 0,
            reverse=True,
        )

        for plant in plants:
            pos = find_next_position(
                plant=plant,
                grid_width=grid_width,
                grid_height=grid_height,
                occupied=occupied,
                placements=placements,
                avoid_pairs=avoid_pairs,
            )

            if not pos:
                warnings.append(f"No valid position found for {plant['name']}.")
                continue

            x, y = pos
            occupied.add((x, y))

            placements.append(
                {
                    "plant_id": plant["id"],
                    "name": plant["name"],
                    "group_id": group["group_id"],
                    "x": x,
                    "y": y,
                    "zone": get_zone(plant),
                    "sunlight": normalize_sunlight(plant.get("sunlight")),
                    "water": normalize_water(
                        plant.get("watering"),
                        plant.get("watering_interval_days"),
                    ),
                    "soil": plant.get("soil"),
                    "max_height_ft": plant.get("max_height_ft"),
                    "max_width_ft": plant.get("max_width_ft"),
                }
            )

        # Detect shade relationships inside the same group
        for provider in plants:
            for receiver in plants:
                if provider["id"] == receiver["id"]:
                    continue

                if can_provide_shade(provider, receiver):
                    shade_relationships.append(
                        {
                            "provider_id": provider["id"],
                            "provider": provider["name"],
                            "receiver_id": receiver["id"],
                            "receiver": receiver["name"],
                            "reason": (f"{provider['name']} is taller and tolerates full sun; " f"{receiver['name']} may benefit from nearby shade."),
                        }
                    )

    return {
        "grid_width": grid_width,
        "grid_height": grid_height,
        "placements": placements,
        "shade_relationships": shade_relationships,
        "warnings": warnings,
    }
