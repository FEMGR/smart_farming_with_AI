# app/services/prolog/prolog_service.py

import subprocess
from pathlib import Path
from collections import defaultdict
import re
from typing import List, Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
PROLOG_PATH = PROJECT_ROOT / "logic_companion_planting" / "main.pl"
PROLOG_ATOM_RE = re.compile(r"^[a-z][a-z0-9_]*$")


# ===============================
# PROLOG RUNNER
# ===============================


def run_query(query: str, log_stderr: bool = True) -> str:
    result = subprocess.run(
        ["swipl", "-s", str(PROLOG_PATH), "-g", query, "-t", "halt"],
        capture_output=True,
        text=True,
        cwd=PROLOG_PATH.parent,
    )

    if result.stderr and log_stderr:
        print(f"[PROLOG STDERR] {result.stderr}")

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()


def _require_atom(value: str) -> str:
    if not PROLOG_ATOM_RE.match(value):
        raise ValueError(f"Unsafe Prolog atom: {value!r}")
    return value


def _query_rows(goal: str, fields: List[str], columns: List[str]) -> List[Dict[str, Any]]:
    writes = []
    for index, field in enumerate(fields):
        if index:
            writes.append("write('\\t')")
        writes.append(f"write({field})")
    writes.append("nl")

    query = "set_prolog_flag(argv,['--quiet']), " f"style_check(-discontiguous), load_all, forall(({goal}), ({', '.join(writes)})), halt"
    output = run_query(query, log_stderr=False)
    rows: List[Dict[str, Any]] = []

    for line in output.splitlines():
        parts = line.strip().split("\t")
        if len(parts) != len(columns):
            continue
        rows.append(dict(zip(columns, parts)))

    return rows


def find_deterring_plants(pest: str) -> List[Dict[str, Any]]:
    pest = _require_atom(pest)
    return _query_rows(
        f"deters(Plant, {pest}, Source, Confidence)",
        ["Plant", "Source", "Confidence"],
        ["plant", "source", "confidence"],
    )


def find_attacked_plants(pest: str) -> List[Dict[str, Any]]:
    pest = _require_atom(pest)
    return _query_rows(
        f"attacks({pest}, Plant)",
        ["Plant"],
        ["plant"],
    )


def find_predators(pest: str | None = None) -> List[Dict[str, Any]]:
    pest_atom = _require_atom(pest) if pest else "Pest"
    return _query_rows(
        f"eats(Predator, {pest_atom})",
        ["Predator", pest_atom],
        ["predator", "pest"],
    )


def find_damage_symptoms(pest: str) -> List[Dict[str, Any]]:
    pest = _require_atom(pest)
    return _query_rows(
        f"damage_symptom({pest}, Symptom)",
        ["Symptom"],
        ["symptom"],
    )


def find_pest_sources(pest: str) -> List[Dict[str, Any]]:
    pest = _require_atom(pest)
    return _query_rows(
        f"pest_source({pest}, Source)",
        ["Source"],
        ["source"],
    )


def find_preventative_plants(disease: str) -> List[Dict[str, Any]]:
    disease = _require_atom(disease)
    return _query_rows(
        f"prevents(Plant, {disease}, Source, Confidence)",
        ["Plant", "Source", "Confidence"],
        ["plant", "source", "confidence"],
    )


def find_disease_symptoms(disease: str) -> List[Dict[str, Any]]:
    disease = _require_atom(disease)
    return _query_rows(
        f"symptom({disease}, Symptom)",
        ["Symptom"],
        ["symptom"],
    )


def find_disease_treatments(disease: str) -> List[Dict[str, Any]]:
    disease = _require_atom(disease)
    return _query_rows(
        f"treatment({disease}, Treatment, Confidence)",
        ["Treatment", "Confidence"],
        ["treatment", "confidence"],
    )


def find_disease_host_treatments(disease: str) -> List[Dict[str, Any]]:
    disease = _require_atom(disease)
    return _query_rows(
        f"disease_host_treatment({disease}, Host, Treatment)",
        ["Host", "Treatment"],
        ["host", "treatment"],
    )


def find_beneficial_relations(plant: str | None = None) -> List[Dict[str, Any]]:
    plant_atom = _require_atom(plant) if plant else "PlantA"
    return _query_rows(
        f"beneficial_relation({plant_atom}, PlantB, Source, Confidence)",
        [plant_atom, "PlantB", "Source", "Confidence"],
        ["plant", "companion", "source", "confidence"],
    )


def find_harmful_relations(plant: str | None = None) -> List[Dict[str, Any]]:
    plant_atom = _require_atom(plant) if plant else "PlantA"
    return _query_rows(
        f"harmful_relation({plant_atom}, PlantB, Source, Confidence)",
        [plant_atom, "PlantB", "Source", "Confidence"],
        ["plant", "companion", "source", "confidence"],
    )


def find_pollinators(plant: str | None = None) -> List[Dict[str, Any]]:
    plant_atom = _require_atom(plant) if plant else "Plant"
    return _query_rows(
        f"pollinates(Pollinator, {plant_atom})",
        ["Pollinator", plant_atom],
        ["pollinator", "plant"],
    )


def find_parasites(host: str | None = None) -> List[Dict[str, Any]]:
    host_atom = _require_atom(host) if host else "Host"
    return _query_rows(
        f"parasitizes(Parasite, {host_atom})",
        ["Parasite", host_atom],
        ["parasite", "host"],
    )


def find_plants_attracting(beneficial: str | None = None) -> List[Dict[str, Any]]:
    beneficial_atom = _require_atom(beneficial) if beneficial else "Beneficial"
    return _query_rows(
        f"attracts_beneficial(Plant, {beneficial_atom}, Source, Confidence)",
        ["Plant", beneficial_atom, "Source", "Confidence"],
        ["plant", "beneficial", "source", "confidence"],
    )


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
        cucumber-nasturtium|pest_deterrence|Nasturtium helps deter pests_ver01|0.9|rhs
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
