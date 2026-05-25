"""
Service layer for FastAPI (Plant Grouping).

Key Point:
Organizes plants into compatible groups based on companion planting rules and environmental constraints.

Responsibilities:
- Build a graph representing plant compatibilities.
- Identify and manage conflicts between plants within groups.
- Distribute duplicate plants across different groups if necessary.
- Enforce conflict-free grouping based on 'avoid' pairs.
- Apply user-defined group overrides.
- Generate structured plant groups with associated reasons for compatibility.

Architecture Role:
- Central logic layer for creating coherent plant groupings for layout generation.
- Delegates plant atom conversion to `constraint_service`.

Layer Interaction:
- Communicates with: Models (Plant), Constraint Service (for compatibility checks and atom conversion).
- Called by: Positioning service, Routes (for group generation endpoints).

Data Flow:
List of plants and compatibility pairs (valid/avoid) received from route
        ↓
Compatibility graph constructed
        ↓
Initial groups formed based on positive links
        ↓
Duplicate plants distributed
        ↓
Conflict-free grouping enforced
        ↓
User-defined group overrides applied
        ↓
Final structured groups (with members and reasons) returned to route
"""

# app/services/grouping_service.py

from typing import List, Dict, Set, Tuple
from app.models.plant import Plant
from app.services.constraint_service import plant_to_prolog_atom

# ===============================
# BUILD GRAPH
# ===============================


def plant_node_key(plant: Plant) -> str:
    return f"plant:{plant.id}"


def build_graph(plants: List[Plant], valid_pairs: List[str]) -> Tuple[Dict[str, Set[str]], Dict[str, str]]:
    graph = {plant_node_key(plant): set() for plant in plants}
    node_atoms = {plant_node_key(plant): plant_to_prolog_atom(plant) for plant in plants}
    atom_nodes: Dict[str, List[str]] = {}

    for node, atom in node_atoms.items():
        atom_nodes.setdefault(atom, []).append(node)

    for pair in valid_pairs:
        try:
            p1, p2 = pair.split("-")
            p1 = p1.lower().strip()
            p2 = p2.lower().strip()

            for node1 in atom_nodes.get(p1, []):
                for node2 in atom_nodes.get(p2, []):
                    if node1 == node2:
                        continue

                    graph[node1].add(node2)
                    graph[node2].add(node1)

        except ValueError:
            continue

    return graph, node_atoms


# ===============================
# FIND CONFLICT-AWARE GROUPS
# ===============================


def reverse_pair(pair: str) -> str:
    try:
        p1, p2 = pair.split("-")
        return f"{p2}-{p1}"
    except ValueError:
        return pair


def has_conflict(candidate: str, group: Set[str], avoid_pairs: Set[str], node_atoms: Dict[str, str]) -> bool:
    candidate_atom = node_atoms.get(candidate, candidate)

    for member in group:
        member_atom = node_atoms.get(member, member)
        pair = f"{candidate_atom}-{member_atom}"
        if pair in avoid_pairs or reverse_pair(pair) in avoid_pairs:
            return True
    return False


def has_positive_link(candidate: str, group: Set[str], graph: Dict[str, Set[str]]) -> bool:
    return any(member in graph.get(candidate, set()) for member in group)


def groups_have_conflict(group1: Set[str], group2: Set[str], avoid_pairs: Set[str], node_atoms: Dict[str, str]) -> bool:
    for node1 in group1:
        for node2 in group2:
            node1_atom = node_atoms.get(node1, node1)
            node2_atom = node_atoms.get(node2, node2)
            pair = f"{node1_atom}-{node2_atom}"
            if pair in avoid_pairs or reverse_pair(pair) in avoid_pairs:
                return True
    return False


def find_groups(graph: Dict[str, Set[str]], node_atoms: Dict[str, str], avoid_pairs: List[str] | None = None) -> List[Set[str]]:
    avoid_pair_set = set(avoid_pairs or [])
    groups = [{node} for node in graph]

    changed = True
    while changed:
        changed = False

        for index, group in enumerate(groups):
            merged = False

            for other_index in range(index + 1, len(groups)):
                other = groups[other_index]
                has_link = any(neighbor in other for node in group for neighbor in graph.get(node, set()))

                if has_link and not groups_have_conflict(group, other, avoid_pair_set, node_atoms):
                    group.update(other)
                    del groups[other_index]
                    changed = True
                    merged = True
                    break

            if merged:
                break

    return groups


def can_apply_saved_group_override(
    node: str,
    target_group: Set[str],
    graph: Dict[str, Set[str]],
    node_atoms: Dict[str, str],
    avoid_pairs: Set[str],
) -> bool:
    if not target_group:
        return True

    if has_conflict(node, target_group, avoid_pairs, node_atoms):
        return False

    return True


def apply_saved_group_overrides(
    raw_groups: List[Set[str]],
    plants: List[Plant],
    graph: Dict[str, Set[str]],
    node_atoms: Dict[str, str],
    avoid_pairs: List[str] | None = None,
) -> List[Set[str]]:
    plant_groups = {plant_node_key(plant): plant.group_id for plant in plants if plant.group_id is not None}

    if not plant_groups:
        return raw_groups

    groups = [set(group) for group in raw_groups]
    avoid_pair_set = set(avoid_pairs or [])

    for node, target_group_id in plant_groups.items():
        if not node or target_group_id is None:
            continue

        while len(groups) < target_group_id:
            groups.append(set())

        target_group = groups[target_group_id - 1]

        if node not in target_group and not can_apply_saved_group_override(node, target_group, graph, node_atoms, avoid_pair_set):
            continue

        for group in groups:
            group.discard(node)

        groups[target_group_id - 1].add(node)

    return [group for group in groups if group]


def group_has_same_atom(group: Set[str], node: str, node_atoms: Dict[str, str]) -> bool:
    node_atom = node_atoms.get(node, node)
    return any(node_atoms.get(member, member) == node_atom for member in group)


def distribute_duplicate_plants(
    raw_groups: List[Set[str]], graph: Dict[str, Set[str]], node_atoms: Dict[str, str], avoid_pairs: List[str] | None = None
) -> List[Set[str]]:
    avoid_pair_set = set(avoid_pairs or [])
    groups = [set(group) for group in raw_groups]

    for group in list(groups):
        atoms_seen = set()

        for node in list(group):
            atom = node_atoms.get(node, node)

            if atom not in atoms_seen:
                atoms_seen.add(atom)
                continue

            target_group = None

            for candidate_group in groups:
                if candidate_group is group:
                    continue

                if group_has_same_atom(candidate_group, node, node_atoms):
                    continue

                if has_positive_link(node, candidate_group, graph) and not has_conflict(node, candidate_group, avoid_pair_set, node_atoms):
                    target_group = candidate_group
                    break

            if target_group is None:
                target_group = set()
                groups.append(target_group)

            group.remove(node)
            target_group.add(node)

    return [group for group in groups if group]


def conflict_pairs_in_group(group: Set[str], avoid_pairs: Set[str], node_atoms: Dict[str, str]) -> List[tuple[str, str]]:
    conflicts = []
    nodes = list(group)

    for index, node1 in enumerate(nodes):
        for next_index in range(index + 1, len(nodes)):
            node2 = nodes[next_index]
            node1_atom = node_atoms.get(node1, node1)
            node2_atom = node_atoms.get(node2, node2)
            pair = f"{node1_atom}-{node2_atom}"

            if pair in avoid_pairs or reverse_pair(pair) in avoid_pairs:
                conflicts.append((node1, node2))

    return conflicts


def positive_degree_in_group(node: str, group: Set[str], graph: Dict[str, Set[str]]) -> int:
    return sum(1 for member in group if member in graph.get(node, set()))


def move_node_to_best_conflict_free_group(
    node: str,
    source_group: Set[str],
    groups: List[Set[str]],
    graph: Dict[str, Set[str]],
    node_atoms: Dict[str, str],
    avoid_pairs: Set[str],
) -> None:
    source_group.remove(node)

    best_group = None
    best_score = None

    for candidate_group in groups:
        if candidate_group is source_group:
            continue

        if has_conflict(node, candidate_group, avoid_pairs, node_atoms):
            continue

        score = (
            positive_degree_in_group(node, candidate_group, graph),
            -len(candidate_group),
        )

        if best_score is None or score > best_score:
            best_score = score
            best_group = candidate_group

    if best_group is None or best_score[0] == 0:
        best_group = set()
        groups.append(best_group)

    best_group.add(node)


def enforce_conflict_free_groups(
    raw_groups: List[Set[str]], graph: Dict[str, Set[str]], node_atoms: Dict[str, str], avoid_pairs: List[str] | None = None
) -> List[Set[str]]:
    avoid_pair_set = set(avoid_pairs or [])

    if not avoid_pair_set:
        return raw_groups

    groups = [set(group) for group in raw_groups]
    changed = True

    while changed:
        changed = False

        for group in list(groups):
            conflicts = conflict_pairs_in_group(group, avoid_pair_set, node_atoms)

            if not conflicts:
                continue

            node1, node2 = conflicts[0]
            node1_degree = positive_degree_in_group(node1, group, graph)
            node2_degree = positive_degree_in_group(node2, group, graph)
            node_to_move = node1 if node1_degree <= node2_degree else node2
            move_node_to_best_conflict_free_group(node_to_move, group, groups, graph, node_atoms, avoid_pair_set)
            changed = True
            break

        groups = [group for group in groups if group]

    return groups


# ===============================
# MAIN GROUPING FUNCTION
# ===============================


def generate_groups_internal(plants: List[Plant], valid_pairs: List[str], avoid_pairs: List[str] | None = None) -> List[dict]:
    graph, node_atoms = build_graph(plants, valid_pairs)
    raw_groups = find_groups(graph, node_atoms, avoid_pairs)
    raw_groups = distribute_duplicate_plants(raw_groups, graph, node_atoms, avoid_pairs)
    raw_groups = enforce_conflict_free_groups(raw_groups, graph, node_atoms, avoid_pairs)
    raw_groups = apply_saved_group_overrides(raw_groups, plants, graph, node_atoms, avoid_pairs)

    plant_map = {plant_node_key(plant): plant for plant in plants}

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
                    "group_id": plant.group_id,
                    "bed_x": plant.bed_x,
                    "bed_y": plant.bed_y,
                    "sunlight": species.sunlight_requirement if species else None,
                    "watering": species.watering if species else None,
                    "watering_interval_days": plant.watering_interval_days,
                    "soil": species.recommended_soil if species else None,
                    "max_height_ft": species.max_height_ft if species else None,
                    "max_width_ft": species.max_width_ft if species else None,
                    "location_id": plant.location_id,
                    "location_width_m": float(plant.location.width_m) if plant.location and plant.location.width_m is not None else None,
                    "location_length_m": float(plant.location.length_m) if plant.location and plant.location.length_m is not None else None,
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
    avoid_pairs: List[str] | None = None,
    pair_reasons: Dict[str, dict] | None = None,
) -> List[dict]:

    graph, node_atoms = build_graph(plants, valid_pairs)
    raw_groups = find_groups(graph, node_atoms, avoid_pairs)
    raw_groups = distribute_duplicate_plants(raw_groups, graph, node_atoms, avoid_pairs)
    raw_groups = enforce_conflict_free_groups(raw_groups, graph, node_atoms, avoid_pairs)
    raw_groups = apply_saved_group_overrides(raw_groups, plants, graph, node_atoms, avoid_pairs)

    plant_map = {plant_node_key(plant): plant for plant in plants}
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
                        "group_id": plant.group_id,
                        "bed_x": plant.bed_x,
                        "bed_y": plant.bed_y,
                    }
                )

        reasons = []

        for pair in valid_pairs:
            try:
                p1, p2 = pair.split("-")
                p1 = p1.lower().strip()
                p2 = p2.lower().strip()

                group_atoms = {node_atoms.get(node, node) for node in group}

                if p1 in group_atoms and p2 in group_atoms:
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
