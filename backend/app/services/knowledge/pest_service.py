import re
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.services.prolog import prolog_service
from app.services.knowledge.base import display_name, enrich_plant_records, normalize_entity, rank_records
from app.utils.prolog_normalizer import clean_text, normalize_tokens


PROJECT_ROOT = Path(__file__).resolve().parents[4]
INSECT_FACT_PATH = PROJECT_ROOT / "logic_companion_planting" / "data" / "insect_fact.pl"
PEST_ALIASES = {
    "thrip": "thrips",
}

_PEST_ATOMS: set[str] | None = None


def _load_pest_atoms() -> set[str]:
    global _PEST_ATOMS
    if _PEST_ATOMS is not None:
        return _PEST_ATOMS

    try:
        insect_facts = INSECT_FACT_PATH.read_text(encoding="utf-8")
    except OSError:
        _PEST_ATOMS = set()
        return _PEST_ATOMS

    _PEST_ATOMS = {clean_text(match.group(1)) for match in re.finditer(r"^\s*pest\(([^)]+)\)\.", insect_facts, re.MULTILINE)}
    return _PEST_ATOMS


def normalize_pest(pest: str) -> str:
    cleaned = clean_text(pest or "")
    pest_atoms = _load_pest_atoms()

    candidates = [
        cleaned,
        PEST_ALIASES.get(cleaned, ""),
        normalize_tokens(cleaned),
    ]

    if cleaned.endswith("s") and len(cleaned) > 3:
        candidates.append(cleaned[:-1])

    for candidate in candidates:
        if candidate in pest_atoms:
            return candidate

    return normalize_entity(pest)


def get_deterrent_plants(db: Session, pest: str) -> dict[str, Any]:
    normalized_pest = normalize_pest(pest)
    records = prolog_service.find_deterring_plants(normalized_pest)
    ranked = rank_records(records, key=lambda row: row["plant"])

    return {
        "pest": display_name(normalized_pest),
        "normalized_pest": normalized_pest,
        "deterrents": enrich_plant_records(db, ranked),
    }


def get_host_plants(db: Session, pest: str) -> dict[str, Any]:
    normalized_pest = normalize_pest(pest)
    records = prolog_service.find_attacked_plants(normalized_pest)
    ranked = rank_records(records, key=lambda row: row["plant"])

    return {
        "pest": display_name(normalized_pest),
        "normalized_pest": normalized_pest,
        "hosts": enrich_plant_records(db, ranked),
    }


def get_predators(pest: str) -> dict[str, Any]:
    normalized_pest = normalize_pest(pest)
    records = prolog_service.find_predators(normalized_pest)
    ranked = rank_records(records, key=lambda row: row["predator"])

    return {
        "pest": display_name(normalized_pest),
        "normalized_pest": normalized_pest,
        "predators": [
            {
                **record,
                "name": display_name(record["predator"]),
            }
            for record in ranked
        ],
    }


def get_damage_symptoms(pest: str) -> dict[str, Any]:
    normalized_pest = normalize_pest(pest)
    records = prolog_service.find_damage_symptoms(normalized_pest)
    ranked = rank_records(records, key=lambda row: row["symptom"])

    return {
        "pest": display_name(normalized_pest),
        "normalized_pest": normalized_pest,
        "damage_symptoms": [
            {
                "symptom": record["symptom"],
                "name": display_name(record["symptom"]),
            }
            for record in ranked
        ],
    }


def get_profile(db: Session, pest: str) -> dict[str, Any]:
    normalized_pest = normalize_pest(pest)

    return {
        "pest": display_name(normalized_pest),
        "normalized_pest": normalized_pest,
        "sources": prolog_service.find_pest_sources(normalized_pest),
        "deterrents": get_deterrent_plants(db, normalized_pest)["deterrents"],
        "hosts": get_host_plants(db, normalized_pest)["hosts"],
        "predators": get_predators(normalized_pest)["predators"],
        "damage_symptoms": get_damage_symptoms(normalized_pest)["damage_symptoms"],
    }
