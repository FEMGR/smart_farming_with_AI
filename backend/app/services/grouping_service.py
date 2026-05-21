# app/services/grouping_service.py

from typing import List, Dict, Set
from app.models.plant import Plant


# ===============================
# BUILD GRAPH
# ===============================


def build_graph(plants: List[Plant], valid_pairs: List[str]) -> Dict[str, Set[str]]:
    graph = {plant.name.lower(): set() for plant in plants}

    for pair in valid_pairs:
        try:
            p1, p2 = pair.split("-")
            p1 = p1.lower().strip()
            p2 = p2.lower().strip()

            if p1 in graph and p2 in graph:
                graph[p1].add(p2)
                graph[p2].add(p1)

        except ValueError:
            continue

    return graph


# ===============================
# FIND CONNECTED COMPONENTS
# ===============================


def find_groups(graph: Dict[str, Set[str]]) -> List[Set[str]]:
    visited = set()
    groups = []

    for node in graph:
        if node in visited:
            continue

        stack = [node]
        group = set()

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            group.add(current)

            for neighbor in graph.get(current, set()):
                if neighbor not in visited:
                    stack.append(neighbor)

        groups.append(group)

    return groups


# ===============================
# MAIN GROUPING FUNCTION
# ===============================


def generate_groups_internal(plants: List[Plant], valid_pairs: List[str]) -> List[dict]:
    graph = build_graph(plants, valid_pairs)
    raw_groups = find_groups(graph)

    plant_map = {plant.name.lower(): plant for plant in plants}

    groups = []

    for index, group in enumerate(raw_groups, start=1):
        members = []

        for name in group:
            plant = plant_map.get(name)
            if not plant:
                continue

            species = plant.species

            members.append(
                {
                    "id": plant.id,
                    "name": plant.name,
                    "plant_type": plant.plant_type,
                    "species_id": plant.species_id,
                    "sunlight": species.sunlight_requirement if species else None,
                    "watering": species.watering if species else None,
                    "watering_interval_days": plant.watering_interval_days,
                    "soil": species.recommended_soil if species else None,
                    "max_height_ft": species.max_height_ft if species else None,
                    "max_width_ft": species.max_width_ft if species else None,
                    "location_id": plant.location_id,
                }
            )

        groups.append(
            {
                "group_id": index,
                "member_count": len(members),
                "plants": members,
            }
        )

    return groups


def generate_groups_display(
    plants: List[Plant],
    valid_pairs: List[str],
    pair_reasons: Dict[str, dict] | None = None,
) -> List[dict]:

    graph = build_graph(plants, valid_pairs)
    raw_groups = find_groups(graph)

    plant_map = {plant.name.lower(): plant for plant in plants}
    pair_reasons = pair_reasons or {}

    groups = []

    for index, group in enumerate(raw_groups, start=1):
        members = []

        for name in group:
            plant = plant_map.get(name)
            if plant:
                members.append(
                    {
                        "id": plant.id,
                        "name": plant.name,
                    }
                )

        reasons = []

        for pair in valid_pairs:
            try:
                p1, p2 = pair.split("-")
                p1 = p1.lower().strip()
                p2 = p2.lower().strip()

                if p1 in group and p2 in group:
                    reason_data = pair_reasons.get(pair, {})

                    reasons.append(
                        {
                            "pair": pair,
                            "plants": [p1, p2],
                            "reason_type": reason_data.get(
                                "reason_type",
                                "companion_relationship",
                            ),
                            "description": reason_data.get(
                                "description",
                                "Recommended by companion planting rules.",
                            ),
                        }
                    )

            except ValueError:
                continue

        groups.append(
            {
                "group_id": index,
                "member_count": len(members),
                "plants": members,
                "reasons": reasons,
            }
        )

    return groups
