import re
from typing import Any, Callable

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.plant_species_cache import PlantSpeciesCache
from app.utils.prolog_normalizer import clean_text, normalize_tokens

CONFIDENCE_SCORES = {
    "high": 0.9,
    "medium": 0.6,
    "low": 0.3,
}


def normalize_entity(name: str) -> str:
    return normalize_tokens(clean_text(name or ""))


def display_name(atom: str | None) -> str | None:
    if atom is None:
        return None
    return atom.replace("_", " ").strip().title()


def confidence_score(value: Any) -> float | None:
    if value is None:
        return None

    normalized = str(value).strip().lower()
    if normalized in CONFIDENCE_SCORES:
        return CONFIDENCE_SCORES[normalized]

    try:
        numeric = float(normalized)
    except ValueError:
        return None

    if numeric > 1:
        return min(numeric / 3, 1.0)
    return numeric


def source_score(source: Any) -> int:
    normalized = str(source or "").strip().lower()
    if normalized in {"cornell", "rhs", "ua", "attra", "pfaf"}:
        return 2
    if normalized:
        return 1
    return 0


def rank_records(records: list[dict[str, Any]], key: Callable[[dict[str, Any]], Any]) -> list[dict[str, Any]]:
    deduped: dict[Any, dict[str, Any]] = {}
    for record in records:
        record = dict(record)
        record["confidence_score"] = confidence_score(record.get("confidence"))
        dedupe_key = key(record)
        existing = deduped.get(dedupe_key)
        if existing is None or _rank_tuple(record) > _rank_tuple(existing):
            deduped[dedupe_key] = record

    return sorted(
        deduped.values(),
        key=lambda record: (
            -(record.get("confidence_score") or 0),
            -source_score(record.get("source")),
            str(key(record)),
        ),
    )


def _rank_tuple(record: dict[str, Any]) -> tuple[float, int, str]:
    return (
        record.get("confidence_score") or 0,
        source_score(record.get("source")),
        str(record),
    )


def enrich_plant(db: Session, atom: str) -> dict[str, Any]:
    label = atom.replace("_", " ").strip()
    species = _find_species(db, atom, label)

    enriched: dict[str, Any] = {
        "atom": atom,
        "name": display_name(atom),
        "species": None,
    }

    if species:
        enriched["species"] = {
            "id": species.id,
            "common_name": species.common_name,
            "scientific_name": species.scientific_name,
            "plant_type": species.plant_type,
            "thumbnail_url": species.thumbnail_url,
            "default_image_url": species.default_image_url,
        }

    return enriched


def enrich_plant_records(db: Session, records: list[dict[str, Any]], field: str = "plant") -> list[dict[str, Any]]:
    enriched = []
    for record in records:
        item = dict(record)
        atom = item.get(field)
        if atom:
            item[field] = enrich_plant(db, atom)
        enriched.append(item)
    return enriched


def _find_species(db: Session, atom: str, label: str) -> PlantSpeciesCache | None:
    normalized_label = re.sub(r"\s+", " ", label).lower()
    normalized_atom = atom.lower()

    return (
        db.query(PlantSpeciesCache)
        .filter(
            or_(
                func.lower(PlantSpeciesCache.common_name) == normalized_label,
                func.lower(PlantSpeciesCache.common_name) == normalized_atom,
                func.lower(PlantSpeciesCache.scientific_name) == normalized_label,
                func.lower(PlantSpeciesCache.scientific_name) == normalized_atom,
            )
        )
        .first()
    )
