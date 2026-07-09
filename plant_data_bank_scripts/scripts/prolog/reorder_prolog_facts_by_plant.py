#!/usr/bin/env python3

"""
reorder_prolog_facts_by_plant.py

Reorders selected Prolog fact files into tidy plant-based sections.

Default:
    Preview only.

Apply:
    Use --apply to overwrite target files after creating .bak backups.

Supported files:
    All .pl files under:
    - logic_companion_planting/base/
    - logic_companion_planting/data/

Design:
    - Keeps top file header comments.
    - Extracts one-line facts.
    - Deduplicates exact facts.
    - Groups facts by plant where possible.
    - Writes preview files first.
    - Does not edit rule files.
    - Writes previews to plant_data_bank_scripts/data_bank/prolog_preview by default.
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


AUTO_ORGANIZED_LINE = "% Auto-organized by plant_data_bank_scripts/scripts/prolog/reorder_prolog_facts_by_plant.py"


@dataclass(frozen=True)
class FileConfig:
    key: str
    path: Path
    title: str
    group_mode: str
    predicate_order: dict[str, int]


@dataclass
class ReorderResult:
    key: str
    path: Path
    preview_path: Path | None
    changed: bool
    grouped_plants: list[str]
    fact_count: int
    skipped: bool = False


FILE_CONFIGS: dict[str, FileConfig] = {
    "insect_group": FileConfig(
        key="insect_group",
        path=Path("logic_companion_planting/base/insect_group.pl"),
        title="INSECT GROUPS",
        group_mode="second_arg",
        predicate_order={
            "insect_group": 0,
            "insect_member_of": 1,
        },
    ),
    "plant_group": FileConfig(
        key="plant_group",
        path=Path("logic_companion_planting/base/plant_group.pl"),
        title="PLANT GROUPS",
        group_mode="second_arg",
        predicate_order={
            "group": 0,
            "member_of": 1,
        },
    ),
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
    "soil_profile": FileConfig(
        key="soil_profile",
        path=Path("logic_companion_planting/base/soil_profile.pl"),
        title="SOIL PROFILE FACTS",
        group_mode="first_arg",
        predicate_order={
            "is_a": 0,
            "soil_drainage": 1,
            "soil_water_retention": 2,
            "soil_nutrient_level": 3,
            "soil_ph": 4,
        },
    ),
    "weather_taxonomy": FileConfig(
        key="weather_taxonomy",
        path=Path("logic_companion_planting/base/weather_taxonomy.pl"),
        title="WEATHER TAXONOMY FACTS",
        group_mode="first_arg",
        predicate_order={
            "weather_condition": 0,
            "weather_characteristic": 1,
            "weather_category": 2,
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
    "disease_fact": FileConfig(
        key="disease_fact",
        path=Path("logic_companion_planting/data/disease_fact.pl"),
        title="DISEASE FACTS",
        group_mode="first_arg",
        predicate_order={
            "disease": 0,
            "symptom": 1,
            "treatment": 2,
            "prevention": 3,
        },
    ),
    "environment_fact": FileConfig(
        key="environment_fact",
        path=Path("logic_companion_planting/data/environment_fact.pl"),
        title="ENVIRONMENT FACTS BY PLANT",
        group_mode="first_arg",
        predicate_order={
            "water_need": 0,
            "preferred_temperature": 1,
            "sunlight_requirement": 2,
        },
    ),
    "insect_fact": FileConfig(
        key="insect_fact",
        path=Path("logic_companion_planting/data/insect_fact.pl"),
        title="INSECT FACTS",
        group_mode="first_arg",
        predicate_order={
            "pest": 0,
            "pest_type": 1,
            "pest_scientific_name": 2,
            "pest_included_species": 3,
            "attacks": 4,
            "damage_symptom": 5,
            "eats": 10,
            "parasitizes": 11,
            "pollinates": 12,
            "pest_source": 90,
            "pest_source_url": 91,
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
    "layout_fact": FileConfig(
        key="layout_fact",
        path=Path("logic_companion_planting/data/layout_fact.pl"),
        title="LAYOUT FACTS",
        group_mode="first_arg",
        predicate_order={
            "near": 0,
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
    "weather_fact": FileConfig(
        key="weather_fact",
        path=Path("logic_companion_planting/data/weather_fact.pl"),
        title="WEATHER FACTS",
        group_mode="first_arg",
        predicate_order={
            "current_weather": 0,
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
    in_generated_preamble = False
    index = 0

    while index < len(lines):
        line = lines[index]

        if is_fact(line):
            break

        if is_generated_title_block(lines, index):
            in_generated_preamble = True
            index += 4
            continue

        if in_generated_preamble and is_generated_section_block(lines, index):
            index += 3
            continue

        if in_generated_preamble:
            index += 1
            continue

        header.append(line.rstrip())
        index += 1

    while header and not header[-1].strip():
        header.pop()

    return header


def is_divider(line: str, char: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("% ") and len(stripped) > 4 and set(stripped[2:]) == {char}


def is_comment_title(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("% ") and bool(stripped[2:].strip())


def is_generated_title_block(lines: list[str], index: int) -> bool:
    return (
        index + 3 < len(lines)
        and is_divider(lines[index], "=")
        and is_comment_title(lines[index + 1])
        and lines[index + 2].strip() == AUTO_ORGANIZED_LINE
        and is_divider(lines[index + 3], "=")
    )


def is_generated_section_block(lines: list[str], index: int) -> bool:
    return index + 2 < len(lines) and is_divider(lines[index], "-") and is_comment_title(lines[index + 1]) and is_divider(lines[index + 2], "-")


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
            AUTO_ORGANIZED_LINE,
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


def grouped_plants_from_text(text: str, config: FileConfig) -> list[str]:
    if config.group_mode == "none":
        return []

    plants: set[str] = set()

    for fact in collect_facts(text.splitlines()):
        group_key = group_key_for_fact(fact, config)

        if group_key:
            plants.add(group_key)

    return sorted(plants)


# =========================================================
# RUNNER
# =========================================================


def reorder_file(
    project_root: Path,
    config: FileConfig,
    preview_dir: Path,
    apply: bool,
) -> ReorderResult:
    target_path = project_root / config.path

    if not target_path.exists():
        print(f"[SKIP] missing file: {target_path}")
        return ReorderResult(
            key=config.key,
            path=config.path,
            preview_path=None,
            changed=False,
            grouped_plants=[],
            fact_count=0,
            skipped=True,
        )

    old_text = read_text(target_path)
    new_text = reorder_text(old_text, config)
    old_facts = collect_facts(old_text.splitlines())
    changed = old_text != new_text
    grouped_plants = grouped_plants_from_text(old_text, config)

    preview_path = preview_dir / f"{config.key}_reordered_preview.pl"
    write_text(preview_path, new_text)

    print(f"[PREVIEW] wrote {preview_path}")
    print(f"[PREVIEW] {config.key}: {'would change' if changed else 'already ordered'} " f"({len(old_facts)} facts, {len(grouped_plants)} plant groups)")

    if apply:
        backup_path = target_path.with_suffix(target_path.suffix + ".bak")
        write_text(backup_path, old_text)
        write_text(target_path, new_text)

        print(f"[BACKUP] wrote {backup_path}")
        print(f"[APPLY] reordered {target_path}")

    return ReorderResult(
        key=config.key,
        path=config.path,
        preview_path=display_path(preview_path, project_root),
        changed=changed,
        grouped_plants=grouped_plants,
        fact_count=len(old_facts),
    )


def display_path(path: Path, project_root: Path) -> Path:
    try:
        return path.relative_to(project_root)
    except ValueError:
        return path


def format_atom_list(atoms: list[str], limit: int = 20) -> str:
    if not atoms:
        return "(none)"

    shown = atoms[:limit]
    suffix = f", ... +{len(atoms) - limit} more" if len(atoms) > limit else ""
    return ", ".join(shown) + suffix


def write_summary(project_root: Path, preview_dir: Path, results: list[ReorderResult], apply: bool) -> None:
    changed = [result for result in results if result.changed]
    skipped = [result for result in results if result.skipped]
    plant_groups_in_changed_files = sorted({plant for result in changed for plant in result.grouped_plants})

    lines = [
        "# Prolog reorder preview",
        "",
        "Target files were modified." if apply else "No files were modified.",
        "Run again with --apply to overwrite files after backup." if not apply else "Backups were written before overwriting target files.",
        "Reorder only rearranges existing facts; it does not add new plant facts.",
        "",
        "## Summary",
        "",
        f"Files checked: {len(results)}",
        f"Files that would be reordered: {len(changed)}",
        f"Skipped files: {len(skipped)}",
        "New plants added by reorder: (none)",
        f"Plant groups present in files that would be reordered: {format_atom_list(plant_groups_in_changed_files)}",
        "",
    ]

    for result in results:
        status = "skipped" if result.skipped else "would change" if result.changed else "already ordered"
        lines.append("=" * 80)
        lines.append(str(result.path))
        lines.append(f"Status: {status}")
        lines.append(f"Facts: {result.fact_count}")
        lines.append(f"Plant groups: {format_atom_list(result.grouped_plants)}")

        if result.preview_path:
            lines.append(f"Preview: {result.preview_path}")

        lines.append("")

    summary_path = preview_dir / "reorder_summary.txt"
    write_text(summary_path, "\n".join(lines))

    changed_keys = [result.key for result in changed]
    print(f"[SUMMARY] wrote {summary_path}")
    print(f"[SUMMARY] files that would be reordered: {', '.join(changed_keys) if changed_keys else '(none)'}")
    print("[SUMMARY] new plants added by reorder: (none)")
    print(f"[SUMMARY] plant groups in reordered files: {format_atom_list(plant_groups_in_changed_files)}")


def resolve_project_root(value: str) -> Path:
    path = Path(value).resolve()

    if (path / "logic_companion_planting").exists():
        return path

    if (path.parent / "logic_companion_planting").exists():
        return path.parent

    return path


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
        default="plant_data_bank_scripts/data_bank/prolog_preview",
        help="Preview output directory, relative to project root.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Overwrite target files after creating .bak backups.",
    )

    args = parser.parse_args()

    project_root = resolve_project_root(args.project_root)
    preview_dir = project_root / args.preview_dir
    preview_dir.mkdir(parents=True, exist_ok=True)

    selected = parse_files_arg(args.files)

    results: list[ReorderResult] = []

    for key in selected:
        results.append(
            reorder_file(
                project_root=project_root,
                config=FILE_CONFIGS[key],
                preview_dir=preview_dir,
                apply=args.apply,
            )
        )

    write_summary(
        project_root=project_root,
        preview_dir=preview_dir,
        results=results,
        apply=args.apply,
    )

    if not args.apply:
        print("[INFO] preview only. No Prolog files were modified.")
        print("[INFO] rerun with --apply to overwrite files after backup.")


if __name__ == "__main__":
    main()
