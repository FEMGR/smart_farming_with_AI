# app/services/prolog/prolog_service.py

import os
import subprocess
from collections import defaultdict
from typing import List, Dict, Any

CURRENT_FILE = os.path.abspath(__file__)

PROJECT_ROOT = os.path.dirname(  # smart-farming-system
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE))))  # backend  # app  # services
)
PROLOG_PATH = os.path.join(PROJECT_ROOT, "logic_companion_planting", "main.pl")


# ===============================
# PROLOG RUNNER
# ===============================


def run_query(query: str) -> str:
    result = subprocess.run(
        ["swipl", "-s", PROLOG_PATH, "-g", query, "-t", "halt"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(PROLOG_PATH),
    )

    if result.stderr:
        print(f"[PROLOG STDERR] {result.stderr}")

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()


# ===============================
# MAIN RECOMMENDATIONS
# ===============================


def get_recommendations(plants: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Input:
        ["tomato", "carrot"]

    Output:
        {
            "recommended": [
                {
                    "pair": "tomato-basil",
                    "plants": ["tomato", "basil"],
                    "reason_type": "companion_relationship",
                    "description": "Recommended by companion planting rules.",
                    "confidence": None,
                    "source": "prolog"
                }
            ],
            "avoid": [...]
        }
    """

    print(f"[DEBUG] Using Prolog file at: {PROLOG_PATH}")

    plant_list = "[" + ",".join(plants) + "]"

    query = f"recommend_all({plant_list}),halt"
    output = run_query(query)

    print("[PROLOG OUTPUT]")
    print(output)

    return parse_output(output)


def parse_output(output: str) -> Dict[str, List[Dict[str, Any]]]:
    recommended = []
    avoid = []

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("GOOD:"):
            content = line.replace("GOOD:", "", 1).strip()
            recommended.extend(parse_relationship_list(content, default_kind="recommended"))

        elif line.startswith("BAD:"):
            content = line.replace("BAD:", "", 1).strip()
            avoid.extend(parse_relationship_list(content, default_kind="avoid"))

    return {
        "recommended": recommended,
        "avoid": avoid,
    }


def parse_relationship_list(content: str, default_kind: str) -> List[Dict[str, Any]]:
    if not content:
        return []

    items = [item.strip() for item in content.split(",") if item.strip()]

    return [parse_relationship_item(item, default_kind) for item in items]


def parse_relationship_item(item: str, default_kind: str) -> Dict[str, Any]:
    """
    Supported formats:

    Simple:
        cucumber-nasturtium

    Rich:
        cucumber-nasturtium|pest_deterrence|Nasturtium helps deter pests|0.9|rhs
    """

    parts = [part.strip() for part in item.split("|")]

    pair = parts[0]

    plants = pair.split("-", 1) if "-" in pair else [pair]

    reason_type = parts[1] if len(parts) > 1 and parts[1] else default_reason_type(default_kind)

    description = parts[2] if len(parts) > 2 and parts[2] else default_description(default_kind)

    confidence = None
    if len(parts) > 3 and parts[3]:
        try:
            confidence = float(parts[3])
        except ValueError:
            confidence = None

    source = parts[4] if len(parts) > 4 and parts[4] else "prolog"

    return {
        "pair": pair,
        "plants": plants,
        "reason_type": reason_type,
        "description": description,
        "confidence": confidence,
        "source": source,
    }


def default_reason_type(kind: str) -> str:
    if kind == "avoid":
        return "conflict"

    return "companion_relationship"


def default_description(kind: str) -> str:
    if kind == "avoid":
        return "Avoided by companion planting rules."

    return "Recommended by companion planting rules."


# ===============================
# COMPANION SUGGESTIONS
# ===============================


def get_companion_suggestions(plants: List[str]) -> Dict:
    """
    Input:
        ["tomato", "carrot"]

    Output:
        {
            "suggest_good": {
                "tomato": [
                    {
                        "plant": "basil",
                        "reason_type": "companion_relationship",
                        "description": "Recommended by companion planting rules."
                    }
                ]
            }
        }
    """

    print(f"[DEBUG] Using Prolog file at: {PROLOG_PATH}")

    plant_list = "[" + ",".join(plants) + "]"

    query = f"suggest_companions({plant_list}),halt"
    output = run_query(query)

    print("[PROLOG SUGGESTIONS OUTPUT]")
    print(output)

    return parse_suggestions_output(output)


def parse_suggestions_output(output: str) -> Dict:
    suggest_good = defaultdict(list)
    suggest_bad = defaultdict(list)

    for line in output.splitlines():
        line = line.strip()

        if line.startswith("SUGGEST_GOOD:"):
            content = line.replace("SUGGEST_GOOD:", "", 1).strip()
            parse_suggestion_list(content, suggest_good, default_kind="recommended")

        elif line.startswith("SUGGEST_BAD:"):
            content = line.replace("SUGGEST_BAD:", "", 1).strip()
            parse_suggestion_list(content, suggest_bad, default_kind="avoid")

    return {
        "suggest_good": dict(suggest_good),
        "suggest_bad": dict(suggest_bad),
    }


def parse_suggestion_list(content: str, bucket: defaultdict, default_kind: str) -> None:
    if not content:
        return

    items = [item.strip() for item in content.split(",") if item.strip()]

    for item in items:
        relation = parse_relationship_item(item, default_kind)

        plants = relation.get("plants", [])

        if len(plants) < 2:
            continue

        existing_plant = plants[0]
        suggested_companion = plants[1]

        bucket[existing_plant].append(
            {
                "plant": suggested_companion,
                "pair": relation["pair"],
                "reason_type": relation["reason_type"],
                "description": relation["description"],
                "confidence": relation["confidence"],
                "source": relation["source"],
            }
        )
