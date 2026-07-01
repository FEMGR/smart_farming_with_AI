from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests
from bs4 import BeautifulSoup

from project_paths import PATHS

PROJECT_ROOT = PATHS.plant_data_bank_scripts
DATA_BANK_DIR = PATHS.data_bank
RAW_DIR = PATHS.data_bank_raw_sources
NORMALIZED_DIR = PATHS.normalized_plants
INDEX_DIR = PATHS.data_bank_indexes
USER_AGENT = "SmartUrbanFarmingResearchBot/0.1 educational local research project"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    PATHS.ensure_dirs()
    for p in [
        RAW_DIR,
        NORMALIZED_DIR,
        INDEX_DIR,
        RAW_DIR / "food_plants_international",
        RAW_DIR / "pfaf",
        RAW_DIR / "perenual",
        RAW_DIR / "gbif",
        RAW_DIR / "manual",
    ]:
        p.mkdir(parents=True, exist_ok=True)


def slugify(value: str) -> str:
    value = str(value or "").strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_") or "unknown"


def plant_filename(plant: dict[str, Any]) -> str:
    return slugify(plant.get("plant_atom") or plant.get("common_name") or plant.get("scientific_name") or "unknown") + ".json"


def read_json(path: str | Path, default: Any = None) -> Any:
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_plants(path: str | Path) -> list[dict[str, Any]]:
    data = read_json(path, [])
    if not isinstance(data, list):
        raise ValueError("Plant seed file must be a JSON list.")
    return data


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def soup_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return clean_text(soup.get_text(" ")) or ""


def html_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    t = soup.find("title")
    return clean_text(t.get_text(" ")) if t else None


def response_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def http_get(url: str, params: dict[str, Any] | None = None, timeout: int = 25, delay_seconds: float = 1.0) -> requests.Response:
    time.sleep(delay_seconds)
    r = requests.get(url, params=params, timeout=timeout, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/json"})
    r.raise_for_status()
    return r


def source_snapshot(
    source_name: str, source_url: str, query: str, status: str, raw_text: str | None = None, parsed: dict[str, Any] | None = None
) -> dict[str, Any]:
    parsed = parsed or {}
    return {
        "source_name": source_name,
        "source_url": source_url,
        "query": query,
        "status": status,
        "fetched_at": utc_now(),
        "response_hash": response_hash(raw_text or json.dumps(parsed, sort_keys=True)),
        "parsed": parsed,
        "raw_text_excerpt": (raw_text or "")[:5000],
    }


def extract_sentences_containing(text: str, keywords: list[str], max_sentences: int = 6) -> str | None:
    sentences = re.split(r"(?<=[.!?])\s+", text or "")
    found = []
    for s in sentences:
        low = s.lower()
        if any(k.lower() in low for k in keywords):
            c = clean_text(s)
            if c:
                found.append(c)
        if len(found) >= max_sentences:
            break
    return " ".join(found) if found else None


def guess_life_cycle(text: str) -> str | None:
    low = (text or "").lower()
    if "perennial" in low:
        return "perennial"
    if "biennial" in low:
        return "biennial"
    if "annual" in low:
        return "annual"
    return None


def guess_propagation_methods(text: str) -> list[str]:
    low = (text or "").lower()
    out = []
    checks = {
        "seed": ["seed", "seeds", "sown", "sow", "germinat"],
        "cutting": ["cutting", "cuttings"],
        "division": ["division", "divide"],
        "grafting": ["graft"],
        "layering": ["layering"],
        "tuber": ["tuber"],
        "rhizome": ["rhizome"],
        "bulb": ["bulb"],
        "runner": ["runner"],
    }
    for method, words in checks.items():
        if any(w in low for w in words):
            out.append(method)
    return sorted(set(out))


def guess_edible_parts(text: str) -> list[str]:
    low = (text or "").lower()
    out = []
    checks = {
        "leaf": ["leaf", "leaves"],
        "fruit": ["fruit", "fruits"],
        "seed": ["seed", "seeds"],
        "flower": ["flower", "flowers"],
        "root": ["root", "roots"],
        "tuber": ["tuber"],
        "rhizome": ["rhizome"],
        "stem": ["stem", "shoot"],
        "bulb": ["bulb"],
        "pod": ["pod"],
        "sap": ["sap"],
    }
    for part, words in checks.items():
        if any(w in low for w in words):
            out.append(part)
    return sorted(set(out))


def guess_use_categories(text: str) -> list[str]:
    low = (text or "").lower()
    out = []
    checks = {
        "culinary_herb": ["herb", "flavouring", "flavoring", "seasoning"],
        "leafy_vegetable": ["leafy vegetable", "leaves are eaten", "young leaves"],
        "fruit_crop": ["fruit"],
        "root_tuber_crop": ["root", "tuber", "rhizome"],
        "grain_seed_crop": ["grain", "seed"],
        "spice_crop": ["spice", "aromatic"],
        "medicinal_plant": ["medicinal", "medicine"],
        "edible_flower": ["edible flower", "flowers are eaten"],
    }
    for cat, words in checks.items():
        if any(w in low for w in words):
            out.append(cat)
    return sorted(set(out))


def canonical_profile_template(plant: dict[str, Any]) -> dict[str, Any]:
    atom = slugify(plant.get("plant_atom") or plant.get("common_name") or plant.get("scientific_name"))
    return {
        "plant_atom": atom,
        "identity": {
            "common_name": plant.get("common_name"),
            "scientific_name": plant.get("scientific_name"),
            "genus": None,
            "family": None,
            "synonyms": [],
            "common_names": [],
        },
        "classification": {"edible": None, "use_categories": [], "edible_parts": [], "life_cycle": None, "growth_habit": None},
        "growth": {
            "sunlight": [],
            "water_need": None,
            "soil_type": [],
            "soil_ph_min": None,
            "soil_ph_max": None,
            "growth_speed": None,
            "climate_notes": None,
            "soil_notes": None,
            "water_notes": None,
            "light_notes": None,
        },
        "germination": {
            "propagation_methods": [],
            "propagation_notes": None,
            "germination_days_min": None,
            "germination_days_max": None,
            "germination_light": None,
            "sowing_depth_cm": None,
            "minimum_soil_temp_c": None,
            "optimum_soil_temp_c": None,
        },
        "spacing": {"spacing_cm": None, "root_depth_cm": None, "plant_height_cm": None, "spread_cm": None},
        "care": {
            "watering_interval_days": None,
            "watering_notes": None,
            "pruning_notes": None,
            "fertilizer_notes": None,
            "cultivation_notes": None,
            "production_notes": None,
            "nutrition_notes": None,
            "cautions": None,
        },
        "pests_and_diseases": {"known_pests": [], "known_diseases": [], "disease_notes": None, "treatment_notes": None},
        "biodiversity": {"companions": [], "conflicts": [], "repels_pests": [], "attracts_beneficial_insects": [], "pollinator_support": None},
        "field_sources": {},
        "source_metadata": {"sources": [], "last_merged_at": utc_now()},
        "missing_fields": [],
    }
