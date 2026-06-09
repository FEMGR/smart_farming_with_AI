"""
Plant taxonomy normalization backed by local Prolog facts.

This module parses logic_companion_planting/base/plant_taxonomy.pl once and keeps an
in-memory dictionary for plant identity normalization.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.logger import setup_logger
from app.utils.prolog_normalizer import clean_text, normalize_tokens, to_prolog_atom

logger = setup_logger()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TAXONOMY_PATH = PROJECT_ROOT / "logic_companion_planting" / "base" / "plant_taxonomy.pl"

_FACT_RE = re.compile(r"^\s*([a-z_]+)\(([^,]+),\s*(.+)\)\.\s*$")
_INFRASPECIFIC_RANK_RE = re.compile(
    r"\b(var\.?|subsp\.?|ssp\.?|f\.|forma|cv\.)\s+([A-Za-z-]+)",
    re.IGNORECASE,
)

_TAXONOMY_BY_ATOM: dict[str, dict[str, Any]] = {}
_ATOM_BY_SCIENTIFIC: dict[str, str] = {}
_LOADED = False


@dataclass(frozen=True)
class PlantIdentity:
    plant_atom: str
    scientific_name: str | None = None
    alternate_scientific_names: list[str] | None = None
    genus: str | None = None
    family: str | None = None
    taxonomy_confidence: str | None = None
    taxonomy_source: str | None = None
    taxonomy_note: str | None = None

    def as_dict(self) -> dict[str, str | None]:
        return {
            "plant_atom": self.plant_atom,
            "scientific_name": self.scientific_name,
            "alternate_scientific_names": self.alternate_scientific_names or [],
            "genus": self.genus,
            "family": self.family,
            "taxonomy_confidence": self.taxonomy_confidence,
            "taxonomy_source": self.taxonomy_source,
            "taxonomy_note": self.taxonomy_note,
        }


def _parse_prolog_value(value: str) -> str:
    value = value.strip()
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1].replace("\\'", "'")
    return clean_text(value)


def load_plant_taxonomy_cache(force: bool = False) -> dict[str, dict[str, Any]]:
    """Parse plant_taxonomy.pl into a Python dictionary."""
    global _LOADED

    if _LOADED and not force:
        return _TAXONOMY_BY_ATOM

    _TAXONOMY_BY_ATOM.clear()
    _ATOM_BY_SCIENTIFIC.clear()

    try:
        lines = TAXONOMY_PATH.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        logger.warning("plant_taxonomy.load_failed path=%s error=%s", TAXONOMY_PATH, exc)
        _LOADED = True
        return _TAXONOMY_BY_ATOM

    field_map = {
        "accepted_scientific_name": "scientific_name",
        "alternate_scientific_name": "alternate_scientific_names",
        "genus": "genus",
        "family": "family",
        "taxonomy_confidence": "taxonomy_confidence",
        "taxonomy_source": "taxonomy_source",
        "taxonomy_note": "taxonomy_note",
    }

    for line in lines:
        match = _FACT_RE.match(line)
        if not match:
            continue

        predicate, raw_atom, raw_value = match.groups()
        field = field_map.get(predicate)
        if not field:
            continue

        atom = clean_text(raw_atom.strip("' "))
        value = _parse_prolog_value(raw_value)
        if not atom or not value:
            continue

        record = _TAXONOMY_BY_ATOM.setdefault(atom, {})
        if field == "alternate_scientific_names":
            record.setdefault(field, [])
            if value not in record[field]:
                record[field].append(value)
        else:
            record[field] = value

    for atom, data in _TAXONOMY_BY_ATOM.items():
        scientific_name = data.get("scientific_name")
        if scientific_name:
            _ATOM_BY_SCIENTIFIC[clean_text(scientific_name)] = atom
        for alternate_scientific_name in data.get("alternate_scientific_names") or []:
            _ATOM_BY_SCIENTIFIC[clean_text(alternate_scientific_name)] = atom

    _LOADED = True
    logger.info("plant_taxonomy.loaded count=%s path=%s", len(_TAXONOMY_BY_ATOM), TAXONOMY_PATH)
    return _TAXONOMY_BY_ATOM


def get_taxonomy_by_atom() -> dict[str, dict[str, Any]]:
    return load_plant_taxonomy_cache()


def normalize_plant_input(plant_name: str) -> PlantIdentity:
    """Normalize user input into a stable plant identity."""
    taxonomy = load_plant_taxonomy_cache()
    raw_name = str(plant_name or "").strip()
    cleaned = clean_text(raw_name)

    atom = None
    if cleaned in _ATOM_BY_SCIENTIFIC:
        atom = _ATOM_BY_SCIENTIFIC[cleaned]

    if not atom:
        atom = to_prolog_atom({"name": raw_name}) or None

    if atom not in taxonomy:
        normalized = normalize_tokens(cleaned)
        if normalized in taxonomy:
            atom = normalized

    if not atom:
        atom = normalize_tokens(cleaned)

    data = taxonomy.get(atom, {})
    return PlantIdentity(
        plant_atom=atom,
        scientific_name=data.get("scientific_name"),
        alternate_scientific_names=data.get("alternate_scientific_names") or [],
        genus=data.get("genus"),
        family=data.get("family"),
        taxonomy_confidence=data.get("taxonomy_confidence"),
        taxonomy_source=data.get("taxonomy_source"),
        taxonomy_note=data.get("taxonomy_note"),
    )


def normalize_scientific_name_for_perenual(scientific_name: str | None) -> list[str]:
    """
    Build Perenual-friendly scientific-name search variants.

    Perenual often does not match formal infraspecific ranks like
    "Brassica oleracea var. gemmifera", while it may match rankless or
    common-name queries. Keep the full scientific name stored on the plant; only
    normalize the external search terms.
    """
    scientific_name = str(scientific_name or "").strip()
    if not scientific_name:
        return []

    variants: list[str] = []
    rankless = _INFRASPECIFIC_RANK_RE.sub(r"\2", scientific_name)
    rankless = re.sub(r"\s+", " ", rankless).strip()
    rank_was_removed = rankless.lower() != scientific_name.lower()
    if rankless:
        variants.append(rankless)

    parts = scientific_name.split()
    if len(parts) >= 2:
        binomial = " ".join(parts[:2])
        variants.append(binomial)

    if not rank_was_removed:
        variants.append(scientific_name)

    result: list[str] = []
    seen: set[str] = set()
    for variant in variants:
        key = variant.lower()
        if key not in seen:
            result.append(variant)
            seen.add(key)
    return result


def build_perenual_search_queries(identity: PlantIdentity, user_input: str) -> list[str]:
    """Return Perenual search queries in the required priority order."""
    scientific_queries = normalize_scientific_name_for_perenual(identity.scientific_name)
    alternate_scientific_queries = []
    for alternate_name in identity.alternate_scientific_names or []:
        alternate_scientific_queries.extend(normalize_scientific_name_for_perenual(alternate_name))
    primary_scientific = scientific_queries[:1]
    fallback_scientific = scientific_queries[1:]
    candidates = [*primary_scientific, user_input, *alternate_scientific_queries, *fallback_scientific, identity.genus]
    queries: list[str] = []
    seen: set[str] = set()

    for candidate in candidates:
        candidate = str(candidate or "").strip()
        key = candidate.lower()
        if candidate and key not in seen:
            queries.append(candidate)
            seen.add(key)

    return queries
