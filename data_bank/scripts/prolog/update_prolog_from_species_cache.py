#!/usr/bin/env python3

"""
update_prolog_from_species_cache.py

Reads cached plant species data from the backend database table `plant_species_cache`
and appends missing Prolog facts into the existing KB.

This is meant for cached Perenual data, so it does NOT call the Perenual API.

Default:
    Preview only. No Prolog files are modified.

Apply:
    Use --apply to append missing facts.

Target files:
    logic_companion_planting/data/plant_fact.pl
    logic_companion_planting/data/alias_fact.pl
    logic_companion_planting/base/plant_taxonomy.pl
    logic_companion_planting/data/growth_facts.pl
    logic_companion_planting/data/sources_fact.pl

Examples:

    python3 scripts/update_prolog_from_species_cache.py \\
      --project-root .. \\
      --only gotu_kola

    python3 scripts/update_prolog_from_species_cache.py \\
      --project-root .. \\
      --apply
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, inspect, text

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402

# =========================================================
# TARGET PROLOG FILES
# =========================================================

TARGET_FILES = {
    "plant_fact": Path(PATHS.as_relative_to_root(PATHS.plant_fact_pl)),
    "alias_fact": Path(PATHS.as_relative_to_root(PATHS.alias_fact_pl)),
    "plant_taxonomy": Path(PATHS.as_relative_to_root(PATHS.plant_taxonomy_pl)),
    "growth_facts": Path(PATHS.as_relative_to_root(PATHS.growth_facts_pl)),
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


def normalize_space(value: Any) -> str | None:
    if value is None:
        return None

    text_value = str(value).replace("\xa0", " ").strip()
    text_value = re.sub(r"\s+", " ", text_value)

    return text_value or None


def to_atom(value: Any) -> str | None:
    text_value = normalize_space(value)

    if not text_value:
        return None

    text_value = text_value.lower()
    text_value = re.sub(r"[^a-z0-9]+", "_", text_value)
    text_value = re.sub(r"_+", "_", text_value).strip("_")

    return text_value or None


def prolog_string(value: Any) -> str | None:
    text_value = normalize_space(value)

    if not text_value:
        return None

    text_value = text_value.replace("\\", "\\\\")
    text_value = text_value.replace("'", "\\'")

    return f"'{text_value}'"


def clean_fact_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"\s*,\s*", ", ", line)
    return line


def existing_fact_set(text_value: str) -> set[str]:
    facts = set()

    for line in text_value.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("%"):
            continue

        if stripped.endswith("."):
            facts.add(clean_fact_line(stripped))

    return facts


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        values[key] = value

    return values


def resolve_database_url(project_root: Path, explicit_url: str | None) -> str:
    if explicit_url:
        return explicit_url

    for key in ["DATABASE_URL", "SQLALCHEMY_DATABASE_URL", "POSTGRES_URL"]:
        if os.environ.get(key):
            return os.environ[key]

    env_candidates = [
        project_root / ".env",
        project_root / "backend" / ".env",
        project_root / "backend" / "app" / ".env",
    ]

    for env_path in env_candidates:
        values = read_env_file(env_path)

        for key in ["DATABASE_URL", "SQLALCHEMY_DATABASE_URL", "POSTGRES_URL"]:
            if values.get(key):
                return values[key]

    raise RuntimeError("Database URL not found. Pass --database-url or define DATABASE_URL in .env.")


def parse_maybe_json(value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        return value

    if not isinstance(value, str):
        return value

    text_value = value.strip()

    if not text_value:
        return None

    if not (text_value.startswith("{") or text_value.startswith("[")):
        return value

    try:
        return json.loads(text_value)
    except Exception:
        pass

    try:
        return ast.literal_eval(text_value)
    except Exception:
        return value


def first_non_empty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value

    return None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return [item for item in value if item not in (None, "", [], {})]

    if isinstance(value, tuple):
        return [item for item in value if item not in (None, "", [], {})]

    if isinstance(value, str):
        text_value = value.strip()

        if not text_value:
            return []

        parsed = parse_maybe_json(text_value)

        if isinstance(parsed, list):
            return [item for item in parsed if item not in (None, "", [], {})]

        # Perenual sometimes stores comma-like text.
        if "," in text_value:
            return [part.strip() for part in text_value.split(",") if part.strip()]

        return [text_value]

    return [value]


def lower_source_atom(source: str) -> str:
    return to_atom(source) or "unknown_source"


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
# EXISTING PROLOG LOOKUP
# =========================================================


@dataclass
class ExistingPrologIndex:
    plants: set[str] = field(default_factory=set)
    aliases: dict[str, str] = field(default_factory=dict)
    scientific_names: dict[str, str] = field(default_factory=dict)


def parse_existing_prolog_index(project_root: Path) -> ExistingPrologIndex:
    index = ExistingPrologIndex()

    plant_fact_text = read_text(project_root / TARGET_FILES["plant_fact"])
    alias_fact_text = read_text(project_root / TARGET_FILES["alias_fact"])
    taxonomy_text = read_text(project_root / TARGET_FILES["plant_taxonomy"])

    for match in re.finditer(r"\bplant\(([a-z][a-zA-Z0-9_]*)\)\.", plant_fact_text):
        index.plants.add(match.group(1))

    for match in re.finditer(
        r"\balias\('([^']+)'\s*,\s*([a-z][a-zA-Z0-9_]*)\)\.",
        alias_fact_text,
    ):
        alias_text = normalize_space(match.group(1).lower())
        plant_atom = match.group(2)

        if alias_text:
            index.aliases[alias_text] = plant_atom

    scientific_patterns = [
        r"\bscientific_name\(([a-z][a-zA-Z0-9_]*)\s*,\s*'([^']+)'\)\.",
        r"\baccepted_scientific_name\(([a-z][a-zA-Z0-9_]*)\s*,\s*'([^']+)'\)\.",
        r"\balternate_scientific_name\(([a-z][a-zA-Z0-9_]*)\s*,\s*'([^']+)'\)\.",
    ]

    for pattern in scientific_patterns:
        for match in re.finditer(pattern, plant_fact_text + "\n" + taxonomy_text):
            plant_atom = match.group(1)
            scientific = normalize_space(match.group(2).lower())

            if scientific:
                index.scientific_names[scientific] = plant_atom

    return index


def resolve_plant_atom(
    species: dict[str, Any],
    index: ExistingPrologIndex,
    allow_new_plants: bool,
) -> str | None:
    explicit_atom = to_atom(species.get("plant_atom"))

    if explicit_atom and explicit_atom in index.plants:
        return explicit_atom

    scientific_name = normalize_space(species.get("scientific_name"))
    common_name = normalize_space(species.get("common_name"))

    if scientific_name:
        existing = index.scientific_names.get(scientific_name.lower())
        if existing:
            return existing

    if common_name:
        existing = index.aliases.get(common_name.lower())
        if existing:
            return existing

    common_atom = to_atom(common_name)
    if common_atom and common_atom in index.plants:
        return common_atom

    scientific_atom = to_atom(scientific_name)
    if scientific_atom and scientific_atom in index.plants:
        return scientific_atom

    if allow_new_plants:
        return common_atom or scientific_atom

    return None


# =========================================================
# DATABASE EXTRACTION
# =========================================================


def row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row._mapping)


def collect_nested_payloads(row: dict[str, Any]) -> list[dict[str, Any]]:
    payloads: list[dict[str, Any]] = []

    for key, value in row.items():
        parsed = parse_maybe_json(value)

        if isinstance(parsed, dict):
            payloads.append(parsed)

            # Common wrapper shapes.
            for nested_key in [
                "payload",
                "data",
                "detail",
                "details",
                "species",
                "result",
                "results",
                "raw",
                "raw_data",
                "response",
            ]:
                nested = parsed.get(nested_key)

                if isinstance(nested, dict):
                    payloads.append(nested)

                if isinstance(nested, list):
                    for item in nested:
                        if isinstance(item, dict):
                            payloads.append(item)

        elif isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    payloads.append(item)

    return payloads


def deep_get_first(payloads: list[dict[str, Any]], keys: list[str]) -> Any:
    """
    Looks for first non-empty key in direct row + nested JSON payloads.
    """
    for payload in payloads:
        for key in keys:
            if key in payload and payload[key] not in (None, "", [], {}):
                return payload[key]

    return None


def normalize_scientific_name(value: Any) -> str | None:
    values = as_list(value)

    if not values:
        return None

    first = values[0]

    if isinstance(first, dict):
        first = first.get("name") or first.get("scientific_name")

    return normalize_space(first)


def extract_species_from_row(row: dict[str, Any]) -> dict[str, Any]:
    payloads = [row] + collect_nested_payloads(row)

    common_name = first_non_empty(
        deep_get_first(payloads, ["common_name", "name", "plant_name"]),
        deep_get_first(payloads, ["display_name"]),
    )

    scientific_name = normalize_scientific_name(deep_get_first(payloads, ["scientific_name", "latin_name", "scientific"]))

    family = first_non_empty(
        deep_get_first(payloads, ["family"]),
        deep_get_first(payloads, ["family_name"]),
    )

    cycle = deep_get_first(payloads, ["cycle", "life_cycle"])
    watering = deep_get_first(payloads, ["watering", "water_need"])
    sunlight = deep_get_first(payloads, ["sunlight", "sun"])
    propagation = deep_get_first(payloads, ["propagation", "propagation_methods"])
    growth_rate = deep_get_first(payloads, ["growth_rate", "growth_speed"])

    care_level = deep_get_first(payloads, ["care_level"])
    edible = deep_get_first(payloads, ["edible", "is_edible"])
    cuisine = deep_get_first(payloads, ["cuisine"])
    medicinal = deep_get_first(payloads, ["medicinal", "is_medicinal"])

    source = first_non_empty(
        deep_get_first(payloads, ["source", "data_source", "source_name"]),
        "Perenual",
    )

    source_url = first_non_empty(
        deep_get_first(payloads, ["source_url", "url"]),
        "https://perenual.com/docs/api",
    )

    return {
        "row_id": row.get("id"),
        "plant_atom": row.get("plant_atom"),
        "common_name": normalize_space(common_name),
        "scientific_name": scientific_name,
        "family": normalize_space(family),
        "cycle": normalize_space(cycle),
        "watering": normalize_space(watering),
        "sunlight": as_list(sunlight),
        "propagation": as_list(propagation),
        "growth_rate": normalize_space(growth_rate),
        "care_level": normalize_space(care_level),
        "edible": edible,
        "cuisine": cuisine,
        "medicinal": medicinal,
        "source": normalize_space(source),
        "source_url": normalize_space(source_url),
    }


def load_species_cache_rows(database_url: str, table_name: str) -> list[dict[str, Any]]:
    engine = create_engine(database_url)
    inspector = inspect(engine)

    if table_name not in inspector.get_table_names():
        raise RuntimeError(f"Table not found: {table_name}. Existing tables: {inspector.get_table_names()}")

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name}"))
        return [row_to_dict(row) for row in result]


# =========================================================
# FACT GENERATION
# =========================================================


def generate_source_facts(out: GeneratedFacts) -> None:
    out.add("sources_fact", "source(perenual).")


def generate_facts_for_species(
    species: dict[str, Any],
    plant_atom: str,
    out: GeneratedFacts,
    allow_new_plants: bool,
) -> None:
    common_name = species.get("common_name")
    scientific_name = species.get("scientific_name")
    family = species.get("family")
    genus = scientific_name.split()[0] if scientific_name else None

    source_url = species.get("source_url") or "https://perenual.com/docs/api"

    if allow_new_plants:
        out.add("plant_fact", f"plant({plant_atom}).")

    # Basic identity.
    if scientific_name:
        out.add(
            "plant_fact",
            f"scientific_name({plant_atom}, {prolog_string(scientific_name.lower())}).",
        )

        out.add(
            "plant_taxonomy",
            f"accepted_scientific_name({plant_atom}, {prolog_string(scientific_name)}).",
        )

    if common_name:
        out.add(
            "alias_fact",
            f"alias({prolog_string(common_name.lower())}, {plant_atom}).",
        )

    if genus:
        out.add("plant_taxonomy", f"genus({plant_atom}, {to_atom(genus)}).")

    if family:
        out.add("plant_taxonomy", f"family({plant_atom}, {to_atom(family)}).")

    if scientific_name or family or genus:
        out.add("plant_taxonomy", f"taxonomy_confidence({plant_atom}, medium).")
        out.add("plant_taxonomy", f"taxonomy_source({plant_atom}, 'Perenual cache').")

    # Growth facts.
    out.add("growth_facts", f"fact_scope({plant_atom}, perenual_cache).")

    if scientific_name:
        out.add(
            "growth_facts",
            f"accepted_scientific_name({plant_atom}, {prolog_string(scientific_name)}).",
        )

    if genus:
        out.add("growth_facts", f"genus({plant_atom}, {to_atom(genus)}).")

    if family:
        out.add("growth_facts", f"family({plant_atom}, {to_atom(family)}).")

    cycle_atom = to_atom(species.get("cycle"))
    if cycle_atom:
        out.add("growth_facts", f"life_cycle({plant_atom}, {cycle_atom}).")

    watering_atom = to_atom(species.get("watering"))
    if watering_atom:
        out.add("growth_facts", f"water_need({plant_atom}, {watering_atom}).")

    growth_rate_atom = to_atom(species.get("growth_rate"))
    if growth_rate_atom:
        out.add("growth_facts", f"growth_speed({plant_atom}, {growth_rate_atom}).")

    care_level_atom = to_atom(species.get("care_level"))
    if care_level_atom:
        out.add("growth_facts", f"care_level({plant_atom}, {care_level_atom}).")

    for value in species.get("sunlight") or []:
        sunlight_atom = to_atom(value)
        if sunlight_atom:
            out.add("growth_facts", f"sunlight({plant_atom}, {sunlight_atom}).")

    for value in species.get("propagation") or []:
        propagation_atom = to_atom(value)
        if propagation_atom:
            out.add("growth_facts", f"propagation_method({plant_atom}, {propagation_atom}).")

    out.add("growth_facts", f"source_name({plant_atom}, 'Perenual cache').")
    out.add("growth_facts", f"source_url({plant_atom}, {prolog_string(source_url)}).")
    out.add("growth_facts", f"confidence({plant_atom}, medium).")

    # Plant classification traits.
    edible = species.get("edible")
    if edible is True or str(edible).lower() == "true":
        out.add("plant_fact", f"edible({plant_atom}, true).")

    medicinal = species.get("medicinal")
    if medicinal is True or str(medicinal).lower() == "true":
        out.add("plant_fact", f"trait({plant_atom}, medicinal).")

    cuisine = species.get("cuisine")
    if cuisine is True or str(cuisine).lower() == "true":
        out.add("plant_fact", f"use_category({plant_atom}, culinary_plant).")


# =========================================================
# APPLY / PREVIEW
# =========================================================


def filter_missing_facts(project_root: Path, generated: GeneratedFacts) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}

    for key, relative_path in TARGET_FILES.items():
        path = project_root / relative_path
        existing = existing_fact_set(read_text(path))

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
        f"% AUTO-GENERATED FROM PLANT SPECIES CACHE: {title}",
        "% Cached Perenual data. Review before editing manually.",
        "% =========================================================",
        "",
    ]

    lines.extend(facts)

    return "\n".join(lines) + "\n"


def write_preview(project_root: Path, missing: dict[str, list[str]], preview_path: Path) -> None:
    lines = [
        "# Prolog species-cache update preview",
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

        if old_text and not old_text.endswith("\n"):
            old_text += "\n"

        write_text(path, old_text + format_generated_block(facts, key))

        print(f"[APPLY] appended {len(facts)} facts -> {path}")


# =========================================================
# MAIN
# =========================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Update Prolog facts from backend plant_species_cache.")

    parser.add_argument(
        "--project-root",
        default=str(PATHS.project_root),
        help="Project root containing backend/ and logic_companion_planting/.",
    )

    parser.add_argument(
        "--database-url",
        default=None,
        help="Optional database URL. If omitted, reads DATABASE_URL from env/backend/.env.",
    )

    parser.add_argument(
        "--table",
        default="plant_species_cache",
        help="Species cache table name.",
    )

    parser.add_argument(
        "--preview-path",
        default="prolog_species_cache_update_preview.txt",
        help="Preview output path, relative to project root.",
    )

    parser.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Optional plant_atom/common/scientific filter.",
    )

    parser.add_argument(
        "--allow-new-plants",
        action="store_true",
        help="Allow creating plant/1 facts for species not already in Prolog.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually append missing facts to Prolog files.",
    )

    args = parser.parse_args()

    PATHS.ensure_dirs()
    project_root = Path(args.project_root).resolve()
    database_url = resolve_database_url(project_root, args.database_url)

    print(f"[INFO] project root: {project_root}")
    print(f"[INFO] table: {args.table}")

    rows = load_species_cache_rows(database_url, args.table)
    print(f"[INFO] rows loaded from species cache: {len(rows)}")

    index = parse_existing_prolog_index(project_root)

    generated = GeneratedFacts()
    generate_source_facts(generated)

    only = {to_atom(item) for item in (args.only or []) if to_atom(item)}
    used = 0
    skipped_no_match = 0

    for row in rows:
        species = extract_species_from_row(row)

        plant_atom = resolve_plant_atom(
            species=species,
            index=index,
            allow_new_plants=args.allow_new_plants,
        )

        if not plant_atom:
            skipped_no_match += 1
            continue

        filter_values = {
            plant_atom,
            to_atom(species.get("common_name")),
            to_atom(species.get("scientific_name")),
        }

        if only and not (only & filter_values):
            continue

        generate_facts_for_species(
            species=species,
            plant_atom=plant_atom,
            out=generated,
            allow_new_plants=args.allow_new_plants,
        )
        used += 1

    print(f"[INFO] matched species used: {used}")
    print(f"[INFO] skipped because no existing plant match: {skipped_no_match}")

    missing = filter_missing_facts(project_root, generated)
    write_preview(project_root, missing, Path(args.preview_path))

    if args.apply:
        apply_missing_facts(project_root, missing)
    else:
        print("[INFO] preview only. No Prolog files were modified.")
        print("[INFO] rerun with --apply to append missing facts.")


if __name__ == "__main__":
    main()
