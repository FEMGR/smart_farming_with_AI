from typing import Any

from sqlalchemy.orm import Session

from app.services.prolog import prolog_service
from app.services.knowledge.base import display_name, enrich_plant_records, normalize_entity, rank_records


def get_symptoms(disease: str) -> dict[str, Any]:
    normalized_disease = normalize_entity(disease)
    records = prolog_service.find_disease_symptoms(normalized_disease)
    ranked = rank_records(records, key=lambda row: row["symptom"])

    return {
        "disease": display_name(normalized_disease),
        "normalized_disease": normalized_disease,
        "symptoms": [
            {
                "symptom": record["symptom"],
                "name": display_name(record["symptom"]),
            }
            for record in ranked
        ],
    }


def get_treatments(disease: str) -> dict[str, Any]:
    normalized_disease = normalize_entity(disease)
    records = prolog_service.find_disease_treatments(normalized_disease)
    host_records = prolog_service.find_disease_host_treatments(normalized_disease)
    ranked = rank_records(records, key=lambda row: row["treatment"])

    return {
        "disease": display_name(normalized_disease),
        "normalized_disease": normalized_disease,
        "treatments": [
            {
                **record,
                "name": display_name(record["treatment"]),
            }
            for record in ranked
        ],
        "host_treatments": [
            {
                **record,
                "host_name": display_name(record["host"]),
                "treatment_name": display_name(record["treatment"]),
            }
            for record in rank_records(host_records, key=lambda row: (row["host"], row["treatment"]))
        ],
    }


def get_preventative_plants(db: Session, disease: str) -> dict[str, Any]:
    normalized_disease = normalize_entity(disease)
    records = prolog_service.find_preventative_plants(normalized_disease)
    ranked = rank_records(records, key=lambda row: row["plant"])

    return {
        "disease": display_name(normalized_disease),
        "normalized_disease": normalized_disease,
        "preventative_plants": enrich_plant_records(db, ranked),
    }


def get_profile(db: Session, disease: str) -> dict[str, Any]:
    normalized_disease = normalize_entity(disease)

    return {
        "disease": display_name(normalized_disease),
        "normalized_disease": normalized_disease,
        "symptoms": get_symptoms(normalized_disease)["symptoms"],
        "treatments": get_treatments(normalized_disease)["treatments"],
        "host_treatments": get_treatments(normalized_disease)["host_treatments"],
        "preventative_plants": get_preventative_plants(db, normalized_disease)["preventative_plants"],
    }
