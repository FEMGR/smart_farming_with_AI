# frontend/utils/recommendation_helpers.py
# Helper functions for recommendation display.
# - Converts backend recommendation payloads into user-facing labels.
# - Aggregates suggested additions by value and supporting plants.

from __future__ import annotations

from typing import Any

from utils.formatting import companion_atom_key, display_plant_name


def recommendation_purpose(item: dict[str, Any]) -> str:
    reason_type = item.get("reason_type") or "companion"
    source = item.get("source") or "prolog"

    source_labels = {
        "attra": "ATTRA companion planting data",
        "ua": "University of Arizona companion planting data",
        "rhs": "RHS horticultural data",
        "cornell": "Cornell agricultural data",
        "uc_anr": "UC ANR pest management data",
        "usda": "USDA plant data",
        "traditional": "Traditional companion planting knowledge",
        "prolog": "Local Prolog rules",
    }

    reason_labels = {
        "companion": "General companion support",
        "companion_relationship": "General companion support",
        "protection": "Pest or disease protection",
        "beneficial_insect": "Attracts beneficial insects",
        "trait": "Shared ecological trait",
        "conflict": "Known companion planting conflict",
    }

    reason = reason_labels.get(reason_type, reason_type.replace("_", " ").title())
    source_label = source_labels.get(source, source.replace("_", " ").upper())

    return f"{reason} from {source_label}"


def aggregate_companion_suggestions(
    good_suggestions: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    ranked: dict[str, dict[str, Any]] = {}

    for existing_plant, items in good_suggestions.items():
        for item in items:
            companion = item.get("plant")
            if not companion:
                continue

            bucket = ranked.setdefault(
                companion,
                {
                    "plant": companion,
                    "supports": set(),
                    "purposes": set(),
                    "sources": set(),
                    "scores": [],
                },
            )

            bucket["supports"].add(existing_plant)
            bucket["purposes"].add(item.get("reason_type") or "companion")
            bucket["sources"].add(item.get("source") or "prolog")

            if isinstance(item.get("confidence"), (int, float)):
                bucket["scores"].append(float(item["confidence"]))

    ranked_items = []

    for item in ranked.values():
        scores = item["scores"]
        average_score = sum(scores) / len(scores) if scores else 0

        ranked_items.append(
            {
                "plant": item["plant"],
                "supports": sorted(item["supports"]),
                "support_count": len(item["supports"]),
                "purposes": sorted(item["purposes"]),
                "sources": sorted(item["sources"]),
                "average_score": average_score,
            }
        )

    return sorted(
        ranked_items,
        key=lambda item: (
            item["support_count"],
            item["average_score"],
            item["plant"],
        ),
        reverse=True,
    )


def recommended_group_options_for_plant(
    plant: dict[str, Any],
    recommendations: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not recommendations:
        return []

    plant_key = companion_atom_key(plant.get("name") or "")
    groups = recommendations.get("groups") or []
    interactions = recommendations.get("existing_plant_interactions") or {}
    suggestions = recommendations.get("new_companion_suggestions") or {}

    beneficial_pairs = interactions.get("recommended", [])
    avoid_pairs = interactions.get("avoid", [])
    suggested_by_plant = suggestions.get("suggest_good") or {}
    suggested_bad_by_plant = suggestions.get("suggest_bad") or {}

    options = []
    seen_groups = set()

    for group in groups:
        group_id = group.get("group_id")
        members = group.get("plants") or []
        member_keys = {companion_atom_key(member.get("name") or "") for member in members}

        if plant_key in member_keys or group_id in seen_groups:
            continue

        has_conflict = False

        for pair in avoid_pairs:
            pair_plants = {companion_atom_key(name) for name in pair.get("plants", [])}
            if plant_key in pair_plants and any(member_key in pair_plants for member_key in member_keys):
                has_conflict = True
                break

        if not has_conflict:
            for member_key in member_keys:
                for bad_suggestion in suggested_bad_by_plant.get(member_key, []):
                    if companion_atom_key(bad_suggestion.get("plant") or "") == plant_key:
                        has_conflict = True
                        break
                if has_conflict:
                    break

        if has_conflict:
            continue

        reasons = []

        for pair in beneficial_pairs:
            pair_plants = [companion_atom_key(name) for name in pair.get("plants", [])]
            if plant_key in pair_plants and any(member_key in pair_plants for member_key in member_keys):
                reasons.append(pair.get("description") or pair.get("pair") or "Recommended companion pair")

        for member_key in member_keys:
            for suggestion in suggested_by_plant.get(member_key, []):
                if companion_atom_key(suggestion.get("plant") or "") == plant_key:
                    reasons.append(suggestion.get("description") or "Suggested companion addition")

        if reasons:
            member_names = ", ".join(display_plant_name(member.get("name") or "Plant") for member in members)

            options.append(
                {
                    "group_id": group_id,
                    "label": f"Group {group_id}: {member_names}",
                    "reason": "; ".join(dict.fromkeys(reasons)),
                }
            )

            seen_groups.add(group_id)

    return options
