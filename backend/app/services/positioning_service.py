# app/services/positioning_service.py

import math
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


def water_rank(value: Optional[str], interval_days: Optional[int] = None) -> int:
    rank = {
        "high": 0,
        "medium": 1,
        "low": 2,
    }
    return rank.get(normalize_water(value, interval_days), 1)


def plant_identity(plant: dict) -> str:
    return str(plant.get("name") or "").lower().strip().replace(" ", "_")


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


def is_recommended_pair(name1: str, name2: str, recommended_pairs: List[str]) -> bool:
    pair = f"{name1.lower()}-{name2.lower()}"
    return pair in recommended_pairs or reverse_pair(pair) in recommended_pairs


def has_any_avoid_pair(avoid_pairs: List[str]) -> bool:
    return bool(avoid_pairs)


def plant_conflict_count(plant: dict, plants: List[dict], avoid_pairs: List[str]) -> int:
    return sum(1 for other in plants if plant["id"] != other["id"] and is_avoid_pair(plant["name"], other["name"], avoid_pairs))


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


def has_adjacent_same_plant(plant: dict, x: int, y: int, placements: List[dict]) -> bool:
    for placed in placements:
        if plant_identity(plant) != plant_identity(placed):
            continue

        if distance((x, y), (placed["x"], placed["y"])) == 1:
            return True

    return False


def has_same_plant_in_row_or_column(plant: dict, x: int, y: int, placements: List[dict]) -> bool:
    for placed in placements:
        if plant_identity(plant) != plant_identity(placed):
            continue

        if placed["x"] == x or placed["y"] == y:
            return True

    return False


def nearest_conflict_distance(plant: dict, x: int, y: int, placements: List[dict], avoid_pairs: List[str], grid_width: int, grid_height: int) -> int:
    conflict_distances = [distance((x, y), (placed["x"], placed["y"])) for placed in placements if is_avoid_pair(plant["name"], placed["name"], avoid_pairs)]

    if not conflict_distances:
        return grid_width + grid_height

    return min(conflict_distances)


def beneficial_adjacent_count(plant: dict, x: int, y: int, placements: List[dict], recommended_pairs: List[str]) -> int:
    return sum(
        1
        for placed in placements
        if distance((x, y), (placed["x"], placed["y"])) == 1 and is_recommended_pair(plant["name"], placed["name"], recommended_pairs)
    )


def nearest_beneficial_distance(plant: dict, x: int, y: int, placements: List[dict], recommended_pairs: List[str], grid_width: int, grid_height: int) -> int:
    beneficial_distances = [
        distance((x, y), (placed["x"], placed["y"])) for placed in placements if is_recommended_pair(plant["name"], placed["name"], recommended_pairs)
    ]

    if not beneficial_distances:
        return grid_width + grid_height

    return min(beneficial_distances)


def water_similarity_to_neighbors(plant: dict, x: int, y: int, placements: List[dict]) -> int:
    neighbors = [placed for placed in placements if distance((x, y), (placed["x"], placed["y"])) == 1]

    if not neighbors:
        return 0

    plant_water = water_rank(plant.get("watering"), plant.get("watering_interval_days"))
    return -min(abs(plant_water - water_rank(neighbor.get("watering"), neighbor.get("watering_interval_days"))) for neighbor in neighbors)


def sunlight_similarity_to_neighbors(plant: dict, x: int, y: int, placements: List[dict]) -> int:
    neighbors = [placed for placed in placements if distance((x, y), (placed["x"], placed["y"])) == 1]

    if not neighbors:
        return 0

    plant_sunlight = normalize_sunlight(plant.get("sunlight"))
    return 1 if any(normalize_sunlight(neighbor.get("sunlight")) == plant_sunlight for neighbor in neighbors) else 0


def position_score(
    plant: dict,
    x: int,
    y: int,
    placements: List[dict],
    recommended_pairs: List[str],
    avoid_pairs: List[str],
    preferred_y: int | None,
    grid_width: int,
    grid_height: int,
) -> tuple:
    same_adjacent_penalty = -1 if has_adjacent_same_plant(plant, x, y, placements) else 0
    same_row_column_penalty = -1 if has_same_plant_in_row_or_column(plant, x, y, placements) else 0

    return (
        nearest_conflict_distance(plant, x, y, placements, avoid_pairs, grid_width, grid_height),
        beneficial_adjacent_count(plant, x, y, placements, recommended_pairs),
        same_adjacent_penalty,
        -nearest_beneficial_distance(plant, x, y, placements, recommended_pairs, grid_width, grid_height),
        same_row_column_penalty,
        water_similarity_to_neighbors(plant, x, y, placements),
        sunlight_similarity_to_neighbors(plant, x, y, placements),
        1 if preferred_y is not None and y == preferred_y else 0,
        -y,
        -x,
    )


def find_next_position(
    plant: dict,
    grid_width: int,
    grid_height: int,
    occupied: set,
    placements: List[dict],
    recommended_pairs: List[str],
    avoid_pairs: List[str],
    preferred_y: int | None = None,
) -> Optional[Tuple[int, int]]:
    y_values = [preferred_y] if preferred_y is not None and preferred_y < grid_height else []
    y_values.extend(y for y in range(grid_height) if y not in y_values)

    best_position = None
    best_score = None

    for y in y_values:
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
                score = position_score(
                    plant=plant,
                    x=x,
                    y=y,
                    placements=placements,
                    recommended_pairs=recommended_pairs,
                    avoid_pairs=avoid_pairs,
                    preferred_y=preferred_y,
                    grid_width=grid_width,
                    grid_height=grid_height,
                )

                if best_score is None or score > best_score:
                    best_score = score
                    best_position = (x, y)

    return best_position


def derive_grid_dimensions(groups: List[dict], default_width: int, default_height: int) -> tuple[int, int]:
    widths = []
    lengths = []
    plant_count = 0

    for group in groups:
        for plant in group.get("plants", []):
            plant_count += 1

            if plant.get("location_width_m"):
                widths.append(float(plant["location_width_m"]))

            if plant.get("location_length_m"):
                lengths.append(float(plant["location_length_m"]))

    if widths or lengths:
        width = max(1, math.ceil(max(widths) if widths else default_width))
        height = max(1, math.ceil(max(lengths) if lengths else default_height))
    else:
        width = default_width
        height = default_height

    while width * height < plant_count:
        if width <= height:
            width += 1
        else:
            height += 1

    return width, height


def arrange_group_plants(plants: List[dict], recommended_pairs: List[str], avoid_pairs: List[str]) -> List[dict]:
    if not plants:
        return []

    if has_any_avoid_pair(avoid_pairs):
        remaining = sorted(
            plants,
            key=lambda plant: (
                -plant_conflict_count(plant, plants, avoid_pairs),
                water_rank(plant.get("watering"), plant.get("watering_interval_days")),
                plant.get("name") or "",
            ),
        )
        arranged = []

        while remaining:
            if not arranged:
                arranged.append(remaining.pop(0))
                continue

            best_index = 0
            best_score = None
            for index, candidate in enumerate(remaining):
                nearest_conflict_distance = None
                for position, placed in enumerate(arranged):
                    if is_avoid_pair(candidate["name"], placed["name"], avoid_pairs):
                        distance_to_conflict = len(arranged) - position
                        if nearest_conflict_distance is None or distance_to_conflict < nearest_conflict_distance:
                            nearest_conflict_distance = distance_to_conflict

                conflict_distance_score = nearest_conflict_distance if nearest_conflict_distance is not None else len(arranged) + 1
                beneficial_with_previous = 1 if is_recommended_pair(candidate["name"], arranged[-1]["name"], recommended_pairs) else 0
                water_similarity_score = -abs(
                    water_rank(candidate.get("watering"), candidate.get("watering_interval_days"))
                    - water_rank(arranged[-1].get("watering"), arranged[-1].get("watering_interval_days"))
                )
                same_plant_penalty = -3 if plant_identity(candidate) == plant_identity(arranged[-1]) else 0
                score = (
                    conflict_distance_score,
                    beneficial_with_previous,
                    same_plant_penalty,
                    water_similarity_score,
                    candidate.get("name") or "",
                )

                if best_score is None or score > best_score:
                    best_score = score
                    best_index = index

            arranged.append(remaining.pop(best_index))

        return arranged

    sorted_plants = sorted(
        plants,
        key=lambda plant: (
            water_rank(plant.get("watering"), plant.get("watering_interval_days")),
            normalize_sunlight(plant.get("sunlight")),
            plant.get("name") or "",
        ),
    )

    arranged = []
    remaining = sorted_plants[:]

    while remaining:
        if not arranged:
            arranged.append(remaining.pop(0))
            continue

        different_index = next(
            (
                index
                for index, plant in enumerate(remaining)
                if plant_identity(plant) != plant_identity(arranged[-1]) and is_recommended_pair(plant["name"], arranged[-1]["name"], recommended_pairs)
            ),
            None,
        )

        if different_index is None:
            different_index = next((index for index, plant in enumerate(remaining) if plant_identity(plant) != plant_identity(arranged[-1])), None)

        if different_index is None:
            arranged.append(remaining.pop(0))
        else:
            arranged.append(remaining.pop(different_index))

    return arranged


def has_saved_position(plant: dict) -> bool:
    return plant.get("bed_x") is not None and plant.get("bed_y") is not None


def placement_from_saved_position(plant: dict, group_id: int, grid_width: int, grid_height: int) -> tuple[dict | None, str | None]:
    x = int(plant.get("bed_x"))
    y = int(plant.get("bed_y"))
    saved_group_id = int(plant.get("group_id") or group_id)

    if x < 0 or y < 0 or x >= grid_width or y >= grid_height:
        return None, f"Saved position for {plant['name']} is outside the current layout grid."

    return (
        {
            "plant_id": plant["id"],
            "name": plant["name"],
            "group_id": saved_group_id,
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
            "saved_position": True,
        },
        None,
    )


def placement_from_generated_position(plant: dict, group_id: int, x: int, y: int) -> dict:
    return {
        "plant_id": plant["id"],
        "name": plant["name"],
        "group_id": group_id,
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
        "saved_position": False,
    }


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
    grid_width, grid_height = derive_grid_dimensions(groups, grid_width, grid_height)

    placements = []
    occupied = set()
    warnings = []
    shade_relationships = []

    group_entries = []

    for group_index, group in enumerate(groups):
        plants = group.get("plants", [])

        group_id = int(group.get("group_id") or group_index + 1)
        preferred_y = min(group_id - 1, grid_height - 1)
        group_entries.append((group, group_id, preferred_y, plants))

        for plant in [p for p in plants if has_saved_position(p)]:
            saved_placement, warning = placement_from_saved_position(plant, group_id, grid_width, grid_height)

            if warning:
                warnings.append(warning)
                continue

            position = (saved_placement["x"], saved_placement["y"])

            if position in occupied:
                warnings.append(f"Saved position for {plant['name']} is already occupied; it was left for manual review.")
                continue

            occupied.add(position)
            placements.append(saved_placement)

    for group, group_id, preferred_y, plants in group_entries:
        plants = [p for p in plants if not has_saved_position(p)]
        plants = arrange_group_plants(plants, recommended_pairs, avoid_pairs)

        for plant in plants:
            pos = find_next_position(
                plant=plant,
                grid_width=grid_width,
                grid_height=grid_height,
                occupied=occupied,
                placements=placements,
                recommended_pairs=recommended_pairs,
                avoid_pairs=avoid_pairs,
                preferred_y=preferred_y,
            )

            if not pos:
                warnings.append(f"No valid position found for {plant['name']}.")
                continue

            x, y = pos
            occupied.add((x, y))

            placements.append(placement_from_generated_position(plant, group_id, x, y))

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
