from typing import Any

from sqlalchemy.orm import Session

from app.services.prolog import prolog_service
from app.services.knowledge.base import display_name, enrich_plant_records, normalize_entity, rank_records


def get_predators(pest: str | None = None) -> dict[str, Any]:
    normalized_pest = normalize_entity(pest) if pest else None
    records = prolog_service.find_predators(normalized_pest)
    ranked = rank_records(records, key=lambda row: (row["predator"], row["pest"]))

    return {
        "pest": display_name(normalized_pest) if normalized_pest else None,
        "normalized_pest": normalized_pest,
        "predators": [
            {
                **record,
                "predator_name": display_name(record["predator"]),
                "pest_name": display_name(record["pest"]),
            }
            for record in ranked
        ],
    }


def get_pollinators(db: Session, plant: str | None = None) -> dict[str, Any]:
    normalized_plant = normalize_entity(plant) if plant else None
    records = prolog_service.find_pollinators(normalized_plant)
    ranked = rank_records(records, key=lambda row: (row["pollinator"], row["plant"]))

    return {
        "plant": display_name(normalized_plant) if normalized_plant else None,
        "normalized_plant": normalized_plant,
        "pollinators": enrich_plant_records(db, ranked, field="plant"),
    }


def get_parasites(host: str | None = None) -> dict[str, Any]:
    normalized_host = normalize_entity(host) if host else None
    records = prolog_service.find_parasites(normalized_host)
    ranked = rank_records(records, key=lambda row: (row["parasite"], row["host"]))

    return {
        "host": display_name(normalized_host) if normalized_host else None,
        "normalized_host": normalized_host,
        "parasites": [
            {
                **record,
                "parasite_name": display_name(record["parasite"]),
                "host_name": display_name(record["host"]),
            }
            for record in ranked
        ],
    }


def get_plants_attracting(db: Session, beneficial: str | None = None) -> dict[str, Any]:
    normalized_beneficial = normalize_entity(beneficial) if beneficial else None
    records = prolog_service.find_plants_attracting(normalized_beneficial)
    ranked = rank_records(records, key=lambda row: (row["plant"], row["beneficial"]))

    return {
        "beneficial": display_name(normalized_beneficial) if normalized_beneficial else None,
        "normalized_beneficial": normalized_beneficial,
        "plants": enrich_plant_records(db, ranked, field="plant"),
    }
