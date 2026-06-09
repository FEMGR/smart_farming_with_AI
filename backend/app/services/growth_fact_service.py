"""Import and resolve plant growth facts from local generated Prolog data."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.logger import setup_logger
from app.models.plant_growth_fact import PlantGrowthFact
from app.services.plant_taxonomy_service import PlantIdentity, get_taxonomy_by_atom
from app.utils.prolog_normalizer import clean_text

logger = setup_logger()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GROWTH_FACT_PATHS = [
    PROJECT_ROOT / "logic_companion_planting" / "data" / "growth_facts.pl",
]

_FACT_RE = re.compile(r"^\s*([a-z_]+)\(([^,]+),\s*(.+)\)\.\s*$")
SCALAR_FIELDS = {
    "germination_days_min",
    "germination_days_max",
    "germination_light",
    "stratification_required",
    "stratification_days_min",
    "stratification_days_max",
    "sowing_depth_cm",
    "minimum_soil_temp_c",
    "optimum_soil_temp_c",
    "viable_temp_min_c",
    "viable_temp_max_c",
    "confidence",
}
LIST_FIELD_MAP = {
    "special_treatment": "special_treatments",
    "source_name": "source_names",
    "source_url": "source_urls",
}
_NUMERIC_FLOAT_FIELDS = {
    "sowing_depth_cm",
    "minimum_soil_temp_c",
    "optimum_soil_temp_c",
    "viable_temp_min_c",
    "viable_temp_max_c",
}
_NUMERIC_INT_FIELDS = {
    "germination_days_min",
    "germination_days_max",
    "stratification_days_min",
    "stratification_days_max",
}


class GrowthFactMatch:
    def __init__(self, fact: PlantGrowthFact | None, match_level: str, warning: str | None = None):
        self.fact = fact
        self.match_level = match_level
        self.warning = warning


def _parse_value(raw_value: str) -> Any:
    value = raw_value.strip()
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("\\'", "'")
    if value in {"true", "false"}:
        return value == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return clean_text(value)


def _growth_fact_path() -> Path | None:
    for path in GROWTH_FACT_PATHS:
        if path.exists():
            return path
    return None


def parse_local_growth_facts() -> dict[str, dict[str, Any]]:
    path = _growth_fact_path()
    if not path:
        logger.warning("growth_facts.local_file_missing paths=%s", GROWTH_FACT_PATHS)
        return {}

    facts: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _FACT_RE.match(line)
        if not match:
            continue

        predicate, raw_plant_key, raw_value = match.groups()
        plant_key = clean_text(raw_plant_key.strip("' "))
        if not plant_key:
            continue

        value = _parse_value(raw_value)
        record = facts.setdefault(
            plant_key,
            {
                "plant_key": plant_key,
                "special_treatments": [],
                "source_names": [],
                "source_urls": [],
                "raw_facts": {},
            },
        )
        record["raw_facts"].setdefault(predicate, []).append(value)

        if predicate in SCALAR_FIELDS:
            record[predicate] = value
        elif predicate in LIST_FIELD_MAP:
            target = LIST_FIELD_MAP[predicate]
            if value not in record[target]:
                record[target].append(value)

    logger.info("growth_facts.parsed count=%s path=%s", len(facts), path)
    return facts


def _coerce_record(record: dict[str, Any]) -> dict[str, Any]:
    coerced = dict(record)

    for field in _NUMERIC_INT_FIELDS:
        if coerced.get(field) is not None:
            coerced[field] = int(coerced[field])

    for field in _NUMERIC_FLOAT_FIELDS:
        if coerced.get(field) is not None:
            coerced[field] = float(coerced[field])

    return coerced


def ensure_local_growth_facts_loaded(db: Session, force: bool = False) -> int:
    """Upsert generated Prolog growth facts into plant_growth_facts."""
    if not force and db.query(PlantGrowthFact.id).first():
        return 0

    local_facts = parse_local_growth_facts()
    if not local_facts:
        return 0

    taxonomy = get_taxonomy_by_atom()
    upserted = 0

    existing_by_key = {fact.plant_key: fact for fact in db.query(PlantGrowthFact).all()}

    for plant_key, raw_record in local_facts.items():
        record = _coerce_record(raw_record)
        taxonomy_record = taxonomy.get(plant_key, {})
        fact = existing_by_key.get(plant_key)
        if not fact:
            fact = PlantGrowthFact(plant_key=plant_key)
            db.add(fact)

        fact.scientific_name = taxonomy_record.get("scientific_name")
        fact.genus = taxonomy_record.get("genus")
        fact.family = taxonomy_record.get("family")
        fact.germination_days_min = record.get("germination_days_min")
        fact.germination_days_max = record.get("germination_days_max")
        fact.germination_light = record.get("germination_light")
        fact.stratification_required = record.get("stratification_required")
        fact.stratification_days_min = record.get("stratification_days_min")
        fact.stratification_days_max = record.get("stratification_days_max")
        fact.sowing_depth_cm = record.get("sowing_depth_cm")
        fact.minimum_soil_temp_c = record.get("minimum_soil_temp_c")
        fact.optimum_soil_temp_c = record.get("optimum_soil_temp_c")
        fact.viable_temp_min_c = record.get("viable_temp_min_c")
        fact.viable_temp_max_c = record.get("viable_temp_max_c")
        fact.special_treatments = record.get("special_treatments") or []
        fact.source_names = record.get("source_names") or []
        fact.source_urls = record.get("source_urls") or []
        fact.raw_facts = record.get("raw_facts") or {}
        fact.confidence = record.get("confidence")
        fact.source_type = "local_generated_prolog"
        upserted += 1

    db.flush()
    logger.info("growth_facts.upserted count=%s", upserted)
    return upserted


def _query_by_scientific_name(db: Session, scientific_name: str) -> PlantGrowthFact | None:
    return db.query(PlantGrowthFact).filter(func.lower(PlantGrowthFact.scientific_name) == scientific_name.lower()).order_by(PlantGrowthFact.id.asc()).first()


def resolve_growth_fact(db: Session, identity: PlantIdentity) -> GrowthFactMatch:
    """Resolve by scientific_name, plant_atom, then genus only when unambiguous."""
    ensure_local_growth_facts_loaded(db)

    if identity.scientific_name:
        fact = _query_by_scientific_name(db, identity.scientific_name)
        if fact:
            return GrowthFactMatch(fact, "scientific_name")

    if identity.plant_atom:
        fact = db.query(PlantGrowthFact).filter(PlantGrowthFact.plant_key == identity.plant_atom).first()
        if fact:
            return GrowthFactMatch(fact, "plant_atom")

    if identity.genus:
        genus_matches = db.query(PlantGrowthFact).filter(PlantGrowthFact.genus == identity.genus).all()
        if len(genus_matches) == 1:
            return GrowthFactMatch(genus_matches[0], "genus")
        if len(genus_matches) > 1:
            return GrowthFactMatch(None, "none", f"Genus fallback skipped because {identity.genus} has multiple local growth fact matches.")

    return GrowthFactMatch(None, "none", "No local growth facts found for this plant identity.")
