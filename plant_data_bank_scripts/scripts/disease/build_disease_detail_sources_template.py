#!/usr/bin/env python3
"""
build_disease_detail_sources_template.py

Purpose:
- Read data_bank/normalized/disease_bank.json.
- Generate a complete data_bank/manual_sources/disease_detail_sources.json.
- Every disease_id from disease_bank.json is included.
- Known/common diseases get starter detail source URLs.
- Unknown/unmapped diseases get an empty list [].

This avoids using UC IPM diseases.vegies.html as a detail page,
because that page is only a mapping/index table.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402


def clean_text(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)

    return text or None


def to_snake(value: Any) -> str | None:
    text = clean_text(value)

    if not text:
        return None

    text = text.lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = re.sub(r"\([^)]*\)", "", text)
    text = re.sub(r"[^a-z0-9\s_]", "", text)
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")

    return text or None


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default

    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# Disease-centered starter sources.
# These are NOT plant-profile mappings.
# They are disease detail pages for signs/symptoms/prevention/treatment.
STARTER_DETAIL_SOURCES: Dict[str, List[Dict[str, Any]]] = {
    "alternaria_leaf_blight": [
        {
            "source_name": "Cornell Vegetables",
            "source_url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/carrot-leaf-blight-diseases-and-their-management/",
            "confidence": 0.88,
        }
    ],
    "cercospora_leaf_spot": [
        {
            "source_name": "Cornell Vegetables",
            "source_url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/carrot-leaf-blight-diseases-and-their-management/",
            "confidence": 0.88,
        }
    ],
    "leaf_spot_cercospora": [
        {
            "source_name": "Cornell Vegetables",
            "source_url": "https://www.vegetables.cornell.edu/pest-management/disease-factsheets/carrot-leaf-blight-diseases-and-their-management/",
            "confidence": 0.86,
        }
    ],
    "powdery_mildew": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/powdery-mildew-cucurbits",
            "confidence": 0.88,
        },
        {"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/tomato/powdery-mildew-on-field-grown-tomatoes/", "confidence": 0.86},
    ],
    "downy_mildew": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/downy-mildew-cucurbits",
            "confidence": 0.88,
        }
    ],
    "early_blight": [
        {"source_name": "UW Vegetable Pathology", "source_url": "https://vegpath.plantpath.wisc.edu/diseases/tomato-early-blight/", "confidence": 0.88},
        {"source_name": "NC State Extension", "source_url": "https://content.ces.ncsu.edu/early-blight-of-tomato", "confidence": 0.86},
    ],
    "late_blight": [
        {"source_name": "NC State Extension", "source_url": "https://content.ces.ncsu.edu/tomato-late-blight", "confidence": 0.88},
        {"source_name": "APS Plant Disease Lessons", "source_url": "https://www.apsnet.org/edcenter/pdlessons/Pages/LateBlight.aspx", "confidence": 0.86},
    ],
    "clubroot": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/clubroot-vegetable-crops",
            "confidence": 0.86,
        }
    ],
    "fusarium_wilt": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/fusarium-wilt-tomato",
            "confidence": 0.84,
        }
    ],
    "verticillium_wilt": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/verticillium-wilt", "confidence": 0.84}
    ],
    "bacterial_wilt": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/bacterial-wilt", "confidence": 0.84}
    ],
    "bacterial_spot": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/bacterial-spot-tomato-and-pepper",
            "confidence": 0.84,
        }
    ],
    "bacterial_leaf_spot": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/bacterial-spot-tomato-and-pepper",
            "confidence": 0.80,
        }
    ],
    "septoria_leaf_spot": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/septoria-leaf-spot",
            "confidence": 0.86,
        }
    ],
    "gray_mold": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/gray-mold", "confidence": 0.84}
    ],
    "botrytis_rot": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/gray-mold", "confidence": 0.82}
    ],
    "white_mold": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/white-mold", "confidence": 0.86}
    ],
    "cottony_soft_rot": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/white-mold", "confidence": 0.80}
    ],
    "lettuce_drop": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/lettuce/lettuce-drop/", "confidence": 0.84}],
    "common_rust": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/common-rust-sweet-corn",
            "confidence": 0.84,
        }
    ],
    "bean_rust": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/bean-rust", "confidence": 0.84}
    ],
    "common_smut": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/common-smut-sweet-corn",
            "confidence": 0.84,
        }
    ],
    "head_smut": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/corn/head-smut/", "confidence": 0.82}],
    "curly_top": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/tomato/curly-top/", "confidence": 0.84}],
    "mosaic_viruses": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/viruses-vegetables",
            "confidence": 0.80,
        }
    ],
    "virus_diseases": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/viruses-vegetables",
            "confidence": 0.80,
        }
    ],
    "viruses": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/viruses-vegetables",
            "confidence": 0.78,
        }
    ],
    "phytophthora_root_rot": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/tomato/phytophthora-root-rot/", "confidence": 0.82}],
    "phytophthora_root_and_crown_rot": [
        {"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/pepper/phytophthora-root-and-crown-rot/", "confidence": 0.82}
    ],
    "phytophthora_crown_and_spear_rot": [
        {"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/asparagus/phytophthora-crown-and-spear-rot/", "confidence": 0.82}
    ],
    "common_scab": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/common-scab-potato",
            "confidence": 0.84,
        }
    ],
    "potato_leafroll": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/potato-virus-diseases",
            "confidence": 0.82,
        }
    ],
    "damping_off": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/damping", "confidence": 0.82}
    ],
    "damping_off_and_root_rot": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/damping", "confidence": 0.80}
    ],
    "damping_off_and_root_dieback": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/damping", "confidence": 0.80}
    ],
    "damping_off_and_seed_rots": [
        {"source_name": "University of Minnesota Extension", "source_url": "https://extension.umn.edu/disease-management/damping", "confidence": 0.80}
    ],
    "bacterial_soft_rot": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/bacterial-soft-rot",
            "confidence": 0.82,
        }
    ],
    "bacterial_soft_rots": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/bacterial-soft-rot",
            "confidence": 0.82,
        }
    ],
    "bacterial_soft_rot_and_blackleg": [
        {
            "source_name": "University of Minnesota Extension",
            "source_url": "https://extension.umn.edu/disease-management/blackleg-and-bacterial-soft-rot-potato",
            "confidence": 0.82,
        }
    ],
    "black_mold": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/onion-and-garlic/black-mold/", "confidence": 0.82}],
    "blue_mold_rot": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/onion-and-garlic/blue-mold-rot/", "confidence": 0.82}],
    "botrytis_bulb_rot": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/onion-and-garlic/botrytis-neck-rot/", "confidence": 0.82}],
    "neck_rot": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/onion-and-garlic/botrytis-neck-rot/", "confidence": 0.82}],
    "stemphylium_leaf_blight": [
        {"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/onion-and-garlic/stemphylium-leaf-blight/", "confidence": 0.82}
    ],
    "pink_root": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/onion-and-garlic/pink-root/", "confidence": 0.82}],
    "basal_rot": [{"source_name": "UC IPM", "source_url": "https://ipm.ucanr.edu/agriculture/onion-and-garlic/fusarium-basal-rot/", "confidence": 0.82}],
}


# Aliases let equivalent disease IDs share one source entry.
SOURCE_ALIASES = {
    "leaf_spot_angular": "angular_leaf_spot",
    "leaf_spot_cercospora": "cercospora_leaf_spot",
    "bltva": "beet_leafhopper_transmitted_virescence_agent",
    "botrytis_leafspot": "leaf_blight",
    "leaf_blight": "botrytis_leafspot",
    "gray_mold": "botrytis_rot",
    "neck_rot": "botrytis_bulb_rot",
}


def normalize_bank(raw_bank: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(raw_bank, dict):
        raise RuntimeError("disease_bank.json must be a JSON object.")

    normalized = {}

    for key, value in raw_bank.items():
        if not isinstance(value, dict):
            continue

        disease_id = to_snake(value.get("disease_id") or key)

        if not disease_id:
            continue

        normalized[disease_id] = value

    return dict(sorted(normalized.items(), key=lambda pair: pair[0]))


def build_detail_sources(
    disease_bank: Dict[str, Dict[str, Any]],
    keep_existing: Dict[str, Any] | None = None,
) -> Dict[str, List[Dict[str, Any]]]:
    keep_existing = keep_existing or {}

    output: Dict[str, List[Dict[str, Any]]] = {}

    for disease_id in disease_bank:
        if disease_id in keep_existing and isinstance(keep_existing[disease_id], list):
            output[disease_id] = keep_existing[disease_id]
            continue

        if disease_id in STARTER_DETAIL_SOURCES:
            output[disease_id] = STARTER_DETAIL_SOURCES[disease_id]
            continue

        alias_target = SOURCE_ALIASES.get(disease_id)

        if alias_target and alias_target in STARTER_DETAIL_SOURCES:
            output[disease_id] = STARTER_DETAIL_SOURCES[alias_target]
            continue

        output[disease_id] = []

    return output


def print_summary(output: Dict[str, List[Dict[str, Any]]]) -> None:
    total = len(output)
    mapped = sum(1 for sources in output.values() if sources)
    missing = total - mapped

    print("")
    print("========== Disease Detail Source Template ==========")
    print(f"Total disease IDs : {total}")
    print(f"Mapped sources    : {mapped}")
    print(f"Empty placeholders: {missing}")
    print("====================================================")

    print("")
    print("Mapped disease IDs:")
    for disease_id, sources in output.items():
        if sources:
            print(f" - {disease_id}: {len(sources)} source(s)")

    print("")
    print("Unmapped disease IDs:")
    for disease_id, sources in output.items():
        if not sources:
            print(f" - {disease_id}")

    print("")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build complete disease_detail_sources.json template from disease_bank.json.")

    parser.add_argument(
        "--disease-bank",
        default=str(PATHS.disease_bank),
        help="Input disease_bank.json.",
    )

    parser.add_argument(
        "--output",
        default=str(PATHS.disease_detail_sources),
        help="Output disease_detail_sources.json.",
    )

    parser.add_argument(
        "--preserve-existing",
        action="store_true",
        help="Preserve existing source entries already in disease_detail_sources.json.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing output file.",
    )

    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print resolved paths.",
    )

    args = parser.parse_args()

    PATHS.ensure_dirs()

    if args.show_paths:
        PATHS.print_summary()

    disease_bank_path = Path(args.disease_bank)
    output_path = Path(args.output)

    raw_bank = load_json(disease_bank_path, default={})
    disease_bank = normalize_bank(raw_bank)

    existing = {}

    if args.preserve_existing and output_path.exists():
        existing = load_json(output_path, default={})

        if not isinstance(existing, dict):
            existing = {}

    output = build_detail_sources(
        disease_bank=disease_bank,
        keep_existing=existing,
    )

    print_summary(output)

    if args.dry_run:
        print("[DRY-RUN] No file written.")
        return

    save_json(output_path, output)
    print(f"[OK] Written: {output_path}")


if __name__ == "__main__":
    main()
