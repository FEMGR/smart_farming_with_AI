#!/usr/bin/env python3

"""
update_prolog_from_profiles.py

Safely updates Prolog knowledge-base files from normalized extracted plant profiles.

Default behavior:
    Preview only. No files are modified.

Apply behavior:
    Use --apply to append missing facts into the existing Prolog files.

What it updates:
    logic_companion_planting/data/plant_fact.pl
    logic_companion_planting/data/alias_fact.pl
    logic_companion_planting/base/plant_taxonomy.pl
    logic_companion_planting/data/growth_facts.pl
    logic_companion_planting/data/interaction_support.pl
    logic_companion_planting/data/pest_interactions.pl
    logic_companion_planting/data/sources_fact.pl

Design:
    - Never deletes facts.
    - Never rewrites existing hand-written facts.
    - Appends only missing facts.
    - Creates a preview file before applying.
    - Checks duplicate facts across the whole target file.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from project_paths import PATHS


# =========================================================
# PATH CONFIG
# =========================================================

TARGET_FILES = {
    "plant_fact": Path(PATHS.as_relative_to_root(PATHS.plant_fact_pl)),
    "alias_fact": Path(PATHS.as_relative_to_root(PATHS.alias_fact_pl)),
    "plant_taxonomy": Path(PATHS.as_relative_to_root(PATHS.plant_taxonomy_pl)),
    "growth_facts": Path(PATHS.as_relative_to_root(PATHS.growth_facts_pl)),
    "interaction_support": Path(PATHS.as_relative_to_root(PATHS.interaction_support_pl)),
    "pest_interactions": Path(PATHS.as_relative_to_root(PATHS.pest_interactions_pl)),
    "sources_fact": Path(PATHS.as_relative_to_root(PATHS.sources_fact_pl)),
}


# =========================================================
# BASIC HELPERS
# =========================================================


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[SKIP] Invalid JSON: {path} | {exc}")
        return None

    if not isinstance(data, dict):
        print(f"[SKIP] JSON is not an object: {path}")
        return None

    return data


def normalize_space(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).replace("\xa0", " ").strip()
    text = re.sub(r"\s+", " ", text)

    return text or None


def to_atom(value: Any) -> str | None:
    """
    Converts text into safe Prolog atom style.

    Examples:
        "Gotu Kola" -> gotu_kola
        "Apiaceae" -> apiaceae
        "Plants For A Future" -> plants_for_a_future
    """
    text = normalize_space(value)

    if not text:
        return None

    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")

    return text or None


def prolog_string(value: Any) -> str | None:
    """
    Returns safely quoted Prolog string-like atom using single quotes.

    Example:
        Centella asiatica -> 'Centella asiatica'
    """
    text = normalize_space(value)

    if not text:
        return None

    text = text.replace("\\", "\\\\")
    text = text.replace("'", "\\'")

    return f"'{text}'"


def prolog_bool(value: Any) -> str | None:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return None


def prolog_number(value: Any) -> str | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return str(value)

    if isinstance(value, float):
        return str(round(value, 4))

    return None


def confidence_atom(value: Any, default: str = "medium") -> str:
    """
    Normalizes confidence into your KB style.

    Existing examples:
        high
        medium
        low
        numerical support in interaction_support
    """
    if isinstance(value, (int, float)):
        if value >= 0.75:
            return "high"
        if value >= 0.45:
            return "medium"
        return "low"

    text = str(value or "").lower().strip()

    if text in {"high", "medium", "low"}:
        return text

    return default


def support_score(value: Any, default: int = 2) -> int:
    """
    Converts confidence into interaction_support score style.

    Existing examples:
        beneficial_relation(amaranth, corn, attra, 3).
        harmful_relation(amaranth, brassica_family, attra, 3).
    """
    if isinstance(value, (int, float)):
        if value >= 0.75:
            return 3
        if value >= 0.45:
            return 2
        return 1

    text = str(value or "").lower().strip()

    if text == "high":
        return 3
    if text == "medium":
        return 2
    if text == "low":
        return 1

    return default


def clean_fact_line(line: str) -> str:
    """
    Normalizes spacing for duplicate comparison.
    """
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def existing_fact_set(text: str) -> set[str]:
    """
    Extracts complete one-line Prolog facts.

    This script intentionally writes one-line facts only.
    """
    facts = set()

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("%"):
            continue

        if stripped.endswith("."):
            facts.add(clean_fact_line(stripped))

    return facts


@dataclass
class GeneratedFacts:
    facts: dict[str, list[str]] = field(default_factory=lambda: {key: [] for key in TARGET_FILES})

    def add(self, target: str, fact: str | None) -> None:
        if not fact:
            return

        fact = clean_fact_line(fact)

        if not fact.endswith("."):
            fact += "."

        if fact not in self.facts[target]:
            self.facts[target].append(fact)


# =========================================================
# PROFILE SOURCE HELPERS
# =========================================================


def iter_profile_files(profiles_dir: Path) -> list[Path]:
    return sorted(path for path in profiles_dir.rglob("*.json") if path.is_file())


def get_primary_source_url(profile: dict[str, Any], preferred_source: str) -> str | None:
    sources = (profile.get("source_metadata") or {}).get("sources") or []

    for source in sources:
        if source.get("source_name") == preferred_source and source.get("status") == "trusted_detail":
            return source.get("source_url")

    for source in sources:
        if source.get("source_name") == preferred_source:
            return source.get("source_url")

    return None


def has_source(profile: dict[str, Any], source_name: str) -> bool:
    sources = (profile.get("source_metadata") or {}).get("sources") or []
    return any(source.get("source_name") == source_name for source in sources)


# =========================================================
# FACT GENERATION
# =========================================================


def generate_source_facts(out: GeneratedFacts) -> None:
    """
    Adds source atoms that are not currently in your sources_fact.pl examples.
    """
    for source in ["pfaf", "perenual", "gbif", "fpi"]:
        out.add("sources_fact", f"source({source}).")


def generate_plant_identity_facts(profile: dict[str, Any], out: GeneratedFacts) -> None:
    plant = to_atom(profile.get("plant_atom"))
    identity = profile.get("identity") or {}

    if not plant:
        return

    common_name = identity.get("common_name")
    scientific_name = identity.get("scientific_name")
    genus = identity.get("genus")
    family = identity.get("family")
    synonyms = identity.get("synonyms") or []
    common_names = identity.get("common_names") or []

    # plant_fact.pl
    out.add("plant_fact", f"plant({plant}).")

    if scientific_name:
        # Existing plant_fact.pl uses lowercase scientific_name strings.
        out.add(
            "plant_fact",
            f"scientific_name({plant}, {prolog_string(str(scientific_name).lower())}).",
        )

    # alias_fact.pl
    for name in common_names:
        alias = normalize_space(name)
        if alias:
            out.add("alias_fact", f"alias({prolog_string(alias.lower())}, {plant}).")

    if common_name:
        alias = normalize_space(common_name)
        if alias:
            out.add("alias_fact", f"alias({prolog_string(alias.lower())}, {plant}).")

    # Scientific synonyms are also useful aliases for normalization.
    for synonym in synonyms:
        alias = normalize_space(synonym)
        if alias:
            out.add("alias_fact", f"alias({prolog_string(alias.lower())}, {plant}).")

    # plant_taxonomy.pl
    if scientific_name:
        out.add(
            "plant_taxonomy",
            f"accepted_scientific_name({plant}, {prolog_string(scientific_name)}).",
        )

    for synonym in synonyms:
        if synonym:
            out.add(
                "plant_taxonomy",
                f"alternate_scientific_name({plant}, {prolog_string(synonym)}).",
            )

    genus_atom = to_atom(genus)
    if genus_atom:
        out.add("plant_taxonomy", f"genus({plant}, {genus_atom}).")

    family_atom = to_atom(family)
    if family_atom:
        out.add("plant_taxonomy", f"family({plant}, {family_atom}).")

    if scientific_name or genus_atom or family_atom:
        out.add("plant_taxonomy", f"taxonomy_confidence({plant}, high).")

        if has_source(profile, "GBIF") and has_source(profile, "Plants For A Future"):
            out.add(
                "plant_taxonomy",
                f"taxonomy_source({plant}, 'GBIF / Plants For A Future').",
            )
        elif has_source(profile, "GBIF"):
            out.add("plant_taxonomy", f"taxonomy_source({plant}, 'GBIF').")
        elif has_source(profile, "Plants For A Future"):
            out.add("plant_taxonomy", f"taxonomy_source({plant}, 'Plants For A Future').")


def generate_classification_facts(profile: dict[str, Any], out: GeneratedFacts) -> None:
    plant = to_atom(profile.get("plant_atom"))
    classification = profile.get("classification") or {}

    if not plant:
        return

    edible = classification.get("edible")
    edible_bool = prolog_bool(edible)

    if edible_bool:
        out.add("plant_fact", f"edible({plant}, {edible_bool}).")

    for part in classification.get("edible_parts") or []:
        part_atom = to_atom(part)
        if part_atom:
            out.add("plant_fact", f"edible_part({plant}, {part_atom}).")

    for category in classification.get("use_categories") or []:
        category_atom = to_atom(category)
        if category_atom:
            out.add("plant_fact", f"use_category({plant}, {category_atom}).")

            # Map useful high-level categories to trait/2 where appropriate.
            if category_atom == "medicinal_plant":
                out.add("plant_fact", f"trait({plant}, medicinal).")
            elif category_atom == "repellent_plant":
                out.add("plant_fact", f"trait({plant}, pest_repellent).")
            elif category_atom == "companion_plant":
                out.add("plant_fact", f"trait({plant}, companion_plant).")
            elif category_atom == "culinary_herb":
                out.add("plant_fact", f"trait({plant}, culinary_herb).")

    life_cycle = to_atom(classification.get("life_cycle"))
    botanical_life_cycle = to_atom(classification.get("botanical_life_cycle"))
    crop_life_cycle = to_atom(classification.get("crop_life_cycle"))

    if life_cycle:
        out.add("growth_facts", f"life_cycle({plant}, {life_cycle}).")

    if botanical_life_cycle:
        out.add("growth_facts", f"botanical_life_cycle({plant}, {botanical_life_cycle}).")

    if crop_life_cycle:
        out.add("growth_facts", f"crop_life_cycle({plant}, {crop_life_cycle}).")


def generate_growth_facts(profile: dict[str, Any], out: GeneratedFacts) -> None:
    plant = to_atom(profile.get("plant_atom"))
    identity = profile.get("identity") or {}
    growth = profile.get("growth") or {}
    germination = profile.get("germination") or {}

    if not plant:
        return

    # Keep this compatible with your existing growth_facts.pl pattern.
    out.add("growth_facts", f"fact_scope({plant}, extracted_profile).")

    scientific_name = identity.get("scientific_name")
    genus = to_atom(identity.get("genus"))
    family = to_atom(identity.get("family"))

    if scientific_name:
        out.add(
            "growth_facts",
            f"accepted_scientific_name({plant}, {prolog_string(scientific_name)}).",
        )

    if genus:
        out.add("growth_facts", f"genus({plant}, {genus}).")

    if family:
        out.add("growth_facts", f"family({plant}, {family}).")

    # Structured germination fields.
    for key in [
        "germination_days_min",
        "germination_days_max",
        "sowing_depth_cm",
        "minimum_soil_temp_c",
        "optimum_soil_temp_c",
        "viable_temp_min_c",
        "viable_temp_max_c",
    ]:
        value = germination.get(key)
        number = prolog_number(value)

        if number:
            out.add("growth_facts", f"{key}({plant}, {number}).")

    germination_light = to_atom(germination.get("germination_light"))
    if germination_light:
        out.add("growth_facts", f"germination_light({plant}, {germination_light}).")

    for method in germination.get("propagation_methods") or []:
        method_atom = to_atom(method)
        if method_atom:
            out.add("growth_facts", f"propagation_method({plant}, {method_atom}).")

    for method in germination.get("preferred_propagation_methods") or []:
        method_atom = to_atom(method)
        if method_atom:
            out.add("growth_facts", f"preferred_propagation_method({plant}, {method_atom}).")

    warning = germination.get("propagation_warning")
    if warning:
        out.add("growth_facts", f"propagation_warning({plant}, {prolog_string(warning)}).")

    # Growth conditions.
    for sunlight in growth.get("sunlight") or []:
        sunlight_atom = to_atom(sunlight)
        if sunlight_atom:
            out.add("growth_facts", f"sunlight({plant}, {sunlight_atom}).")

    for soil_type in growth.get("soil_type") or []:
        soil_atom = to_atom(soil_type)
        if soil_atom:
            out.add("growth_facts", f"soil_type({plant}, {soil_atom}).")

    water_need = to_atom(growth.get("water_need"))
    if water_need:
        out.add("growth_facts", f"water_need({plant}, {water_need}).")

    growth_speed = to_atom(growth.get("growth_speed"))
    if growth_speed:
        out.add("growth_facts", f"growth_speed({plant}, {growth_speed}).")

    for key in ["soil_ph_min", "soil_ph_max"]:
        value = growth.get(key)
        number = prolog_number(value)
        if number:
            out.add("growth_facts", f"{key}({plant}, {number}).")

    # Source tracking.
    pfaf_url = get_primary_source_url(profile, "Plants For A Future")

    if pfaf_url:
        out.add("growth_facts", f"source_name({plant}, 'Plants For A Future').")
        out.add("growth_facts", f"source_url({plant}, {prolog_string(pfaf_url)}).")
        out.add("growth_facts", f"confidence({plant}, high).")


def generate_biodiversity_facts(profile: dict[str, Any], out: GeneratedFacts) -> None:
    plant = to_atom(profile.get("plant_atom"))
    biodiversity = profile.get("biodiversity") or {}

    if not plant:
        return

    # Companion/support relationships.
    for item in biodiversity.get("companions") or []:
        other = to_atom(item.get("plant"))
        score = support_score(item.get("confidence"))

        if other:
            out.add(
                "interaction_support",
                f"beneficial_relation({plant}, {other}, pfaf, {score}).",
            )

    for item in biodiversity.get("conflicts") or []:
        other = to_atom(item.get("plant"))
        score = support_score(item.get("confidence"))

        if other:
            out.add(
                "interaction_support",
                f"harmful_relation({plant}, {other}, pfaf, {score}).",
            )

    # Pest deterrence.
    for item in biodiversity.get("repels_pests") or []:
        target = to_atom(item.get("target"))
        confidence = confidence_atom(item.get("confidence"))

        if target:
            out.add(
                "pest_interactions",
                f"deters({plant}, {target}, pfaf, {confidence}).",
            )

    # Beneficial insects / pollinators.
    # Your KB uses trait(Plant, pollinator_attractor) for broad pollinator support.
    # attracts_beneficial/4 should only be used for concrete beneficial insects.
    known_beneficial_insects = {
        "ladybug",
        "lacewing",
        "hoverfly",
        "delphastus_beetle",
        "ground_beetle",
        "praying_mantis",
        "dragonfly",
        "spider",
        "honeybee",
        "bumblebee",
        "encarsia_formosa",
        "parasitic_wasp",
    }

    generic_pollinator_terms = {
        "pollinator",
        "pollinators",
        "insect",
        "insects",
        "beneficial_insect",
        "beneficial_insects",
    }

    for item in biodiversity.get("attracts_beneficial_insects") or []:
        insect_group = to_atom(item.get("insect_group"))
        confidence = confidence_atom(item.get("confidence"))

        if not insect_group:
            continue

        if insect_group in generic_pollinator_terms:
            out.add("plant_fact", f"trait({plant}, pollinator_attractor).")
            continue

        if insect_group in known_beneficial_insects:
            out.add(
                "pest_interactions",
                f"attracts_beneficial({plant}, {insect_group}, pfaf, {confidence}).",
            )
            continue

        # Unknown broad labels should not become fake insect atoms.
        out.add("plant_fact", f"trait({plant}, pollinator_attractor).")

    # Broad pollinator support from normalized profile.
    # Example: PFAF says flowers are pollinated by insects.
    pollinator_support = biodiversity.get("pollinator_support")
    if pollinator_support is True:
        out.add("plant_fact", f"trait({plant}, pollinator_attractor).")

    pest_confuser = biodiversity.get("pest_confuser")
    if pest_confuser is True:
        out.add("plant_fact", f"trait({plant}, pest_confuser).")


def generate_facts_for_profile(profile: dict[str, Any], out: GeneratedFacts) -> None:
    generate_plant_identity_facts(profile, out)
    generate_classification_facts(profile, out)
    generate_growth_facts(profile, out)
    generate_biodiversity_facts(profile, out)


# =========================================================
# APPLY / PREVIEW
# =========================================================


def filter_missing_facts(project_root: Path, generated: GeneratedFacts) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}

    for key, relative_path in TARGET_FILES.items():
        path = project_root / relative_path
        text = read_text(path)
        existing = existing_fact_set(text)

        missing[key] = []

        for fact in generated.facts[key]:
            if clean_fact_line(fact) not in existing:
                missing[key].append(fact)

    return missing


def format_generated_block(facts: list[str], title: str) -> str:
    if not facts:
        return ""

    lines = [
        "",
        "",
        "% =========================================================",
        f"% AUTO-GENERATED FROM NORMALIZED PLANT PROFILES: {title}",
        "% Review before editing manually.",
        "% =========================================================",
        "",
    ]

    lines.extend(facts)

    return "\n".join(lines) + "\n"


def write_preview(project_root: Path, missing: dict[str, list[str]], preview_path: Path) -> None:
    lines = [
        "# Prolog update preview",
        "",
        "No files were modified.",
        "Run again with --apply to append these facts.",
        "",
    ]

    total = 0

    for key, facts in missing.items():
        relative_path = TARGET_FILES[key]
        total += len(facts)

        lines.append("=" * 80)
        lines.append(str(relative_path))
        lines.append(f"Missing facts: {len(facts)}")
        lines.append("=" * 80)
        lines.append("")

        if facts:
            lines.extend(facts)
        else:
            lines.append("(none)")

        lines.append("")

    lines.insert(1, f"Total missing facts: {total}")

    write_text(project_root / preview_path, "\n".join(lines))
    print(f"[PREVIEW] wrote {project_root / preview_path}")
    print(f"[PREVIEW] total missing facts: {total}")


def apply_missing_facts(project_root: Path, missing: dict[str, list[str]]) -> None:
    for key, facts in missing.items():
        if not facts:
            continue

        relative_path = TARGET_FILES[key]
        path = project_root / relative_path
        old_text = read_text(path)

        block = format_generated_block(facts, key)

        if old_text and not old_text.endswith("\n"):
            old_text += "\n"

        write_text(path, old_text + block)

        print(f"[APPLY] appended {len(facts)} facts -> {path}")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Prolog facts from normalized plant profiles.")

    parser.add_argument(
        "--profiles",
        default=str(PATHS.normalized_plants),
        help="Directory containing normalized plant JSON profiles.",
    )

    parser.add_argument(
        "--project-root",
        default=str(PATHS.project_root),
        help="Project root containing logic_companion_planting/.",
    )

    parser.add_argument(
        "--preview-path",
        default="prolog_update_preview.txt",
        help="Where to write the preview report, relative to project root.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually append missing facts to Prolog files.",
    )

    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Optional plant_atom filter, e.g. --only gotu_kola tomato mint",
    )

    args = parser.parse_args()

    PATHS.ensure_dirs()
    project_root = Path(args.project_root).resolve()
    profiles_dir = Path(args.profiles).expanduser()

    if not profiles_dir.is_absolute():
        # Resolve profiles relative to the current working directory,
        # not project_root, because plant_data_bank_scripts may live inside the project.
        profiles_dir = profiles_dir.resolve()

    if not profiles_dir.exists():
        raise FileNotFoundError(f"Profiles directory not found: {profiles_dir}")

    only = set(args.only or [])

    generated = GeneratedFacts()
    generate_source_facts(generated)

    profile_files = iter_profile_files(profiles_dir)
    used_count = 0

    for path in profile_files:
        profile = load_json(path)

        if not profile:
            continue

        plant_atom = profile.get("plant_atom")

        if only and plant_atom not in only:
            continue

        generate_facts_for_profile(profile, generated)
        used_count += 1

    print(f"[INFO] profiles scanned: {len(profile_files)}")
    print(f"[INFO] profiles used: {used_count}")

    missing = filter_missing_facts(project_root, generated)
    write_preview(project_root, missing, Path(args.preview_path))

    if args.apply:
        apply_missing_facts(project_root, missing)
    else:
        print("[INFO] preview only. No Prolog files were modified.")
        print("[INFO] rerun with --apply to append missing facts.")


if __name__ == "__main__":
    main()
