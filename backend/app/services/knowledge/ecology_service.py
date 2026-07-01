from typing import Any

from sqlalchemy.orm import Session

from app.services.prolog import prolog_service
from app.services.knowledge.base import display_name, enrich_plant_records, normalize_entity, rank_records


def get_beneficial_companions(db: Session, plant: str | None = None) -> dict[str, Any]:
    normalized_plant = normalize_entity(plant) if plant else None
    records = prolog_service.find_beneficial_relations(normalized_plant)
    ranked = rank_records(records, key=lambda row: (row["plant"], row["companion"]))

    enriched = enrich_plant_records(db, ranked, field="plant")
    enriched = enrich_plant_records(db, enriched, field="companion")

    return {
        "plant": display_name(normalized_plant) if normalized_plant else None,
        "normalized_plant": normalized_plant,
        "beneficial_companions": enriched,
    }


def get_harmful_companions(db: Session, plant: str | None = None) -> dict[str, Any]:
    normalized_plant = normalize_entity(plant) if plant else None
    records = prolog_service.find_harmful_relations(normalized_plant)
    ranked = rank_records(records, key=lambda row: (row["plant"], row["companion"]))

    enriched = enrich_plant_records(db, ranked, field="plant")
    enriched = enrich_plant_records(db, enriched, field="companion")

    return {
        "plant": display_name(normalized_plant) if normalized_plant else None,
        "normalized_plant": normalized_plant,
        "harmful_companions": enriched,
    }


def get_ecological_support(db: Session, plant: str | None = None) -> dict[str, Any]:
    return {
        "beneficial": get_beneficial_companions(db, plant),
        "harmful": get_harmful_companions(db, plant),
    }
