
#app/services/prolog/prolog_service.py

import subprocess
from typing import List, Dict
from app.utils.prolog_normalizer import to_prolog_atom
import os
from collections import defaultdict

CURRENT_FILE = os.path.abspath(__file__)

PROJECT_ROOT = os.path.dirname(  # smart-farming-system
    os.path.dirname(             # backend
        os.path.dirname(         # app
            os.path.dirname(     # services
                os.path.dirname(CURRENT_FILE)
            )
        )
    )
)
PROLOG_PATH = os.path.join(PROJECT_ROOT, "logic_companion_planting", "main.pl")

def run_query(query: str) -> str:
    result = subprocess.run(
        ["swipl", "-s", PROLOG_PATH, "-g", query, "-t", "halt"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(PROLOG_PATH)
    )

    if result.stderr:
        print(f"[PROLOG STDERR] {result.stderr}") # Print stderr for debugging

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()

def get_recommendations(plants: List[str]) -> Dict:
    """
    Input: ["tomato", "carrot"]  (already normalized atoms)
    Output: { "recommended": [...], "avoid": [...] }
    """
    print(f"[DEBUG] Using Prolog file at: {PROLOG_PATH}")

    atoms = plants

    plant_list = "[" + ",".join(atoms) + "]"

    query = f"recommend_all({plant_list}),halt"
    output = run_query(query)

    print("[PROLOG OUTPUT]")
    print(output)

    return parse_output(output)


def parse_output(output: str) -> Dict:
    good = []
    bad = []

    for line in output.splitlines():
        if line.startswith("GOOD:"):
            content = line.replace("GOOD:", "").strip()
            if content:
                good = content.split(",")
        elif line.startswith("BAD:"):
            content = line.replace("BAD:", "").strip()
            if content:
                bad = content.split(",")

    return {
        "recommended": [g for g in good if g],
        "avoid": [b for b in bad if b]
    }

def get_companion_suggestions(plants: List[str]) -> Dict:
    """
    Input: ["tomato", "carrot"]  (already normalized atoms)
    Output: { "suggest_good": { "plant_a": ["comp_x", "comp_y"], ... }, "suggest_bad": { ... } }
    """
    print(f"[DEBUG] Using Prolog file at: {PROLOG_PATH}")

    atoms = plants

    plant_list = "[" + ",".join(atoms) + "]"

    query = f"suggest_companions({plant_list}),halt"
    output = run_query(query)

    print("[PROLOG SUGGESTIONS OUTPUT]")
    print(output)

    return parse_suggestions_output(output)


def parse_suggestions_output(output: str) -> Dict:
    suggest_good = defaultdict(list)
    suggest_bad = defaultdict(list)

    for line in output.splitlines():
        if line.startswith("SUGGEST_GOOD:"):
            content = line.replace("SUGGEST_GOOD:", "").strip()
            if content:
                pairs = content.split(",")
                for pair in pairs:
                    if '-' in pair:
                        existing_plant, suggested_companion = pair.split('-', 1)
                        suggest_good[existing_plant].append(suggested_companion)
        elif line.startswith("SUGGEST_BAD:"):
            content = line.replace("SUGGEST_BAD:", "").strip()
            if content:
                pairs = content.split(",")
                for pair in pairs:
                    if '-' in pair:
                        existing_plant, suggested_companion = pair.split('-', 1)
                        suggest_bad[existing_plant].append(suggested_companion)

    return {
        "suggest_good": dict(suggest_good),
        "suggest_bad": dict(suggest_bad)
    }
