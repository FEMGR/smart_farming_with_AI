#!/usr/bin/env python3

"""
reorder_prolog_facts_by_plant.py

Reorders selected Prolog fact files into tidy plant-based sections.

Default:
    Preview only.

Apply:
    Use --apply to overwrite target files after creating .bak backups.

Supported files:
    - plant_fact.pl
    - alias_fact.pl
    - plant_taxonomy.pl
    - growth_facts.pl
    - interaction_support.pl
    - pest_interactions.pl
    - sources_fact.pl

Design:
    - Keeps top file header comments.
    - Extracts one-line facts.
    - Deduplicates exact facts.
    - Groups facts by plant where possible.
    - Writes preview files first.
    - Does not edit rule files.
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


# =========================================================
# CONFIG
# =========================================================


@dataclass(frozen=True)
class FileConfig:
    key: str
    path: Path
    title: str
    group_mode: str
    predicate_order: dict[str, int]


FILE_CONFIGS: dict[str, FileConfig] = {
    "plant_fact": FileConfig(
        key="plant_fact",
        path=Path("logic_companion_planting/data/plant_fact.pl"),
        title="PLANT FACTS BY PLANT",
        group_mode="first_arg",
        predicate_order={
            "plant": 0,
            "scientific_name": 1,
            "edible": 2,
            "edible_part": 3,
            "use_category": 4,
            "trait": 5,
        },
    ),
    "alias_fact": FileConfig(
        key="alias_fact",
        path=Path("logic_companion_planting/data/alias_fact.pl"),
        title="ALIASES BY PLANT",
        # alias('gotu kola', gotu_kola). -> group by second argument
        group_mode="second_arg",
        predicate_order={
            "alias": 0,
        },
    ),
    "plant_taxonomy": FileConfig(
        key="plant_taxonomy",
        path=Path("logic_companion_planting/base/plant_taxonomy.pl"),
        title="TAXONOMY FACTS BY PLANT",
        group_mode="first_arg",
        predicate_order={
            "accepted_scientific_name": 0,
            "alternate_scientific_name": 1,
            "genus": 2,
            "family": 3,
            "taxonomy_confidence": 4,
            "taxonomy_source": 5,
            "taxonomy_note": 6,
        },
    ),
    "growth_facts": FileConfig(
        key="growth_facts",
        path=Path("logic_companion_planting/data/growth_facts.pl"),
        title="GROWTH FACTS BY PLANT",
        group_mode="first_arg",
        predicate_order={
            "fact_scope": 0,
            "accepted_scientific_name": 1,
            "genus": 2,
            "family": 3,
            "life_cycle": 4,
            "botanical_life_cycle": 5,
            "crop_life_cycle": 6,
            "germination_days_min": 10,
            "germination_days_max": 11,
            "germination_light": 12,
            "stratification_required": 13,
            "stratification_days_min": 14,
            "stratification_days_max": 15,
            "sowing_depth_cm": 16,
            "minimum_soil_temp_c": 20,
            "optimum_soil_temp_c": 21,
            "viable_temp_min_c": 22,
            "viable_temp_max_c": 23,
            "propagation_method": 30,
            "preferred_propagation_method": 31,
            "propagation_warning": 32,
            "sunlight": 40,
            "soil_type": 41,
            "soil_ph_min": 42,
            "soil_ph_max": 43,
            "water_need": 44,
            "growth_speed": 45,
            "special_treatment": 50,
            "source_name": 90,
            "source_url": 91,
            "confidence": 92,
        },
    ),
    "interaction_support": FileConfig(
        key="interaction_support",
        path=Path("logic_companion_planting/data/interaction_support.pl"),
        title="INTERACTION SUPPORT BY SOURCE PLANT",
        # beneficial_relation(PlantA, PlantB, Source, Score).
        # harmful_relation(PlantA, PlantB, Source, Score).
        group_mode="first_arg",
        predicate_order={
            "beneficial_relation": 0,
            "harmful_relation": 1,
        },
    ),
    "pest_interactions": FileConfig(
        key="pest_interactions",
        path=Path("logic_companion_planting/data/pest_interactions.pl"),
        title="PEST AND BENEFICIAL INTERACTIONS BY PLANT",
        # deters(Plant, Pest, Source, Confidence).
        # attracts_beneficial(Plant, Insect, Source, Confidence).
        # prevents(Plant, Disease, Source, Confidence).
        group_mode="first_arg",
        predicate_order={
            "deters": 0,
            "attracts_beneficial": 1,
            "prevents": 2,
        },
    ),
    "sources_fact": FileConfig(
        key="sources_fact",
        path=Path("logic_companion_planting/data/sources_fact.pl"),
        title="SOURCES",
        group_mode="none",
        predicate_order={
            "source": 0,
        },
    ),
}


# =========================================================
# BASIC PARSING
# =========================================================


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def is_fact(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped and not stripped.startswith("%") and stripped.endswith("."))


def predicate_name(fact: str) -> str | None:
    match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\(", fact.strip())
    return match.group(1) if match else None


def argument_string(fact: str) -> str | None:
    match = re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*\((.*)\)\.$", fact.strip())
    return match.group(1).strip() if match else None


def split_top_level_args(arg_text: str) -> list[str]:
    """
    Splits simple Prolog arguments while respecting quoted strings.

    Example:
        "'gotu kola', gotu_kola" -> ["'gotu kola'", "gotu_kola"]
    """
    args: list[str] = []
    current: list[str] = []
    in_single_quote = False
    escape = False

    for char in arg_text:
        if escape:
            current.append(char)
            escape = False
            continue

        if char == "\\":
            current.append(char)
            escape = True
            continue

        if char == "'":
            current.append(char)
            in_single_quote = not in_single_quote
            continue

        if char == "," and not in_single_quote:
            args.append("".join(current).strip())
            current = []
            continue

        current.append(char)

    if current:
        args.append("".join(current).strip())

    return args


def fact_args(fact: str) -> list[str]:
    args = argument_string(fact)
    if not args:
        return []
    return split_top_level_args(args)


def is_atom(value: str | None) -> bool:
    if not value:
        return False

    value = value.strip()

    if value.startswith("'") or value.startswith('"'):
        return False

    return bool(re.match(r"^[a-z][a-zA-Z0-9_]*$", value))


def first_arg(fact: str) -> str | None:
    args = fact_args(fact)
    if not args:
        return None

    value = args[0]
    return value if is_atom(value) else None


def second_arg(fact: str) -> str | None:
    args = fact_args(fact)
    if len(args) < 2:
        return None

    value = args[1]
    return value if is_atom(value) else None


def extract_header(lines: list[str]) -> list[str]:
    """
    Keeps file-level comments before the first fact.
    Old middle section comments are intentionally removed because the file is being reorganized.
    """
    header: list[str] = []

    for line in lines:
        if is_fact(line):
            break
        header.append(line.rstrip())

    while header and not header[-1].strip():
        header.pop()

    return header


def collect_facts(lines: list[str]) -> list[str]:
    facts: list[str] = []

    for line in lines:
        if not is_fact(line):
            continue

        fact = clean_line(line)

        if fact not in facts:
            facts.append(fact)

    return facts


def plant_title(plant: str) -> str:
    return plant.replace("_", " ").upper()


# =========================================================
# REORDERING
# =========================================================


def fact_sort_key(fact: str, config: FileConfig) -> tuple[int, str]:
    pred = predicate_name(fact) or ""
    return (config.predicate_order.get(pred, 999), fact)


def group_key_for_fact(fact: str, config: FileConfig) -> str | None:
    if config.group_mode == "first_arg":
        return first_arg(fact)

    if config.group_mode == "second_arg":
        return second_arg(fact)

    if config.group_mode == "none":
        return None

    raise ValueError(f"Unsupported group_mode: {config.group_mode}")


def reorder_text(text: str, config: FileConfig) -> str:
    lines = text.splitlines()
    header = extract_header(lines)
    facts = collect_facts(lines)

    grouped: dict[str, list[str]] = defaultdict(list)
    ungrouped: list[str] = []

    for fact in facts:
        group_key = group_key_for_fact(fact, config)

        if config.group_mode == "none":
            ungrouped.append(fact)
            continue

        if group_key:
            grouped[group_key].append(fact)
        else:
            ungrouped.append(fact)

    output: list[str] = []

    if header:
        output.extend(header)
        output.append("")

    output.extend(
        [
            "% =========================================================",
            f"% {config.title}",
            "% Auto-organized by plant_data_bank_scripts/scripts/reorder_prolog_facts_by_plant.py",
            "% =========================================================",
            "",
        ]
    )

    if config.group_mode == "none":
        for fact in sorted(ungrouped, key=lambda item: fact_sort_key(item, config)):
            output.append(fact)

        return "\n".join(output).rstrip() + "\n"

    for plant in sorted(grouped):
        facts_for_plant = sorted(
            grouped[plant],
            key=lambda item: fact_sort_key(item, config),
        )

        output.extend(
            [
                "% ---------------------------------------------------------",
                f"% {plant_title(plant)}",
                "% ---------------------------------------------------------",
            ]
        )

        output.extend(facts_for_plant)
        output.append("")

    if ungrouped:
        output.extend(
            [
                "",
                "% =========================================================",
                "% UNGROUPED / NON-PLANT FACTS",
                "% =========================================================",
                "",
            ]
        )

        for fact in sorted(ungrouped, key=lambda item: fact_sort_key(item, config)):
            output.append(fact)

        output.append("")

    return "\n".join(output).rstrip() + "\n"


# =========================================================
# RUNNER
# =========================================================


def reorder_file(
    project_root: Path,
    config: FileConfig,
    preview_dir: Path,
    apply: bool,
) -> None:
    target_path = project_root / config.path

    if not target_path.exists():
        print(f"[SKIP] missing file: {target_path}")
        return

    old_text = read_text(target_path)
    new_text = reorder_text(old_text, config)

    preview_path = preview_dir / f"{config.key}_reordered_preview.pl"
    write_text(preview_path, new_text)

    print(f"[PREVIEW] wrote {preview_path}")

    if apply:
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        write_text(backup_path, old_text)
        write_text(target_path, new_text)

        print(f"[BACKUP] wrote {backup_path}")
        print(f"[APPLY] reordered {target_path}")


def parse_files_arg(values: list[str] | None) -> list[str]:
    if not values:
        return list(FILE_CONFIGS.keys())

    result: list[str] = []

    for value in values:
        if value == "all":
            return list(FILE_CONFIGS.keys())

        if value not in FILE_CONFIGS:
            valid = ", ".join(FILE_CONFIGS)
            raise ValueError(f"Unknown file key: {value}. Valid keys: {valid}")

        result.append(value)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Reorder Prolog fact files by plant.")

    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root containing logic_companion_planting/.",
    )

    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help=("Which files to reorder. Use all or any of: " + ", ".join(FILE_CONFIGS.keys())),
    )

    parser.add_argument(
        "--preview-dir",
        default="prolog_reorder_previews",
        help="Preview output directory, relative to project root.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Overwrite target files after creating .bak backups.",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    preview_dir = project_root / args.preview_dir
    preview_dir.mkdir(parents=True, exist_ok=True)

    selected = parse_files_arg(args.files)

    for key in selected:
        reorder_file(
            project_root=project_root,
            config=FILE_CONFIGS[key],
            preview_dir=preview_dir,
            apply=args.apply,
        )

    if not args.apply:
        print("[INFO] preview only. No Prolog files were modified.")
        print("[INFO] rerun with --apply to overwrite files after backup.")


if __name__ == "__main__":
    main()
