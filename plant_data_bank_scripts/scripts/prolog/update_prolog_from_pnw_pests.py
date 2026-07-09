#!/usr/bin/env python3
"""
update_prolog_from_pnw_pests.py

Safely appends generated PNW pest facts into the live Prolog knowledge base.

Input:
    plant_data_bank_scripts/data_bank/exports/prolog/generated_pnw_pest_interactions.pl

Targets:
    logic_companion_planting/data/insect_fact.pl
    logic_companion_planting/base/insect_group.pl
    logic_companion_planting/data/sources_fact.pl

Default behavior:
    Preview only. No files are modified.

Apply behavior:
    Use --apply to append missing facts.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from project_paths import PATHS  # noqa: E402

TARGET_FILES = {
    "insect_fact": Path(PATHS.as_relative_to_root(PATHS.prolog_data / "insect_fact.pl")),
    "insect_group": Path(PATHS.as_relative_to_root(PATHS.prolog_base / "insect_group.pl")),
    "sources_fact": Path(PATHS.as_relative_to_root(PATHS.sources_fact_pl)),
}

GENERATED_FACT_RE = re.compile(r"^([a-z][a-z0-9_]*)\((.*)\)\.$")
SOURCE_RE = re.compile(r"^pest_source\([^,]+,\s*([^,\)\s]+)\)\.$")
PEST_RE = re.compile(r"^pest\(([^,\)\s]+)\)\.$")
PEST_TYPE_RE = re.compile(r"^pest_type\(([^,\)\s]+),\s*([^,\)\s]+)\)\.$")

INSECT_FACT_PREDICATES = {
    "attacks",
    "damage_symptom",
    "pest",
    "pest_included_species",
    "pest_scientific_name",
    "pest_source",
    "pest_source_url",
    "pest_type",
}

PREDICATE_ORDER = {
    "pest": 10,
    "pest_type": 20,
    "pest_scientific_name": 30,
    "pest_included_species": 40,
    "damage_symptom": 50,
    "attacks": 60,
    "pest_source": 70,
    "pest_source_url": 80,
    "insect_group": 90,
    "insect_member_of": 100,
    "source": 110,
}


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


def read_text(path: Path) -> str:
    if not path.exists():
        return ""

    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def clean_fact_line(line: str) -> str:
    line = line.strip()
    return re.sub(r"\s+", " ", line)


def existing_fact_set(text: str) -> set[str]:
    facts = set()

    for line in text.splitlines():
        stripped = clean_fact_line(line)

        if not stripped or stripped.startswith("%"):
            continue

        if stripped.endswith("."):
            facts.add(stripped)

    return facts


def iter_generated_facts(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Generated PNW Prolog file not found: {path}")

    facts = []

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = clean_fact_line(line)

        if not stripped or stripped.startswith("%"):
            continue

        if not stripped.endswith("."):
            continue

        if GENERATED_FACT_RE.match(stripped):
            facts.append(stripped)
        else:
            print(f"[SKIP] Unsupported generated Prolog line: {stripped}")

    return facts


def route_generated_facts(facts: list[str]) -> GeneratedFacts:
    routed = GeneratedFacts()

    for fact in facts:
        match = GENERATED_FACT_RE.match(fact)
        if not match:
            continue

        predicate = match.group(1)

        if predicate in INSECT_FACT_PREDICATES:
            routed.add("insect_fact", fact)

        source_match = SOURCE_RE.match(fact)
        if source_match:
            routed.add("sources_fact", f"source({source_match.group(1)}).")

        pest_match = PEST_RE.match(fact)
        if pest_match:
            pest = pest_match.group(1)
            routed.add("insect_group", f"insect_member_of({pest}, pest).")

        type_match = PEST_TYPE_RE.match(fact)
        if type_match:
            pest = type_match.group(1)
            pest_type = type_match.group(2)

            if pest_type and pest_type != "insect":
                routed.add("insect_group", f"insect_group({pest_type}).")
                routed.add("insect_group", f"insect_member_of({pest}, {pest_type}).")

    return routed


def predicate_name(fact: str) -> str:
    match = GENERATED_FACT_RE.match(fact)
    return match.group(1) if match else ""


def sort_generated_facts(generated: GeneratedFacts) -> None:
    for key, facts in generated.facts.items():
        generated.facts[key] = sorted(
            facts,
            key=lambda fact: (PREDICATE_ORDER.get(predicate_name(fact), 999), fact),
        )


def filter_missing_facts(project_root: Path, generated: GeneratedFacts) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}

    for key, relative_path in TARGET_FILES.items():
        path = project_root / relative_path
        existing = existing_fact_set(read_text(path))

        missing[key] = [fact for fact in generated.facts[key] if clean_fact_line(fact) not in existing]

    return missing


def format_generated_block(facts: list[str], title: str) -> str:
    if not facts:
        return ""

    lines = [
        "",
        "",
        "% =========================================================",
        f"% AUTO-GENERATED FROM PNW PEST EXPORT: {title}",
        "% Review before editing manually.",
        "% =========================================================",
        "",
    ]
    lines.extend(facts)

    return "\n".join(lines) + "\n"


def write_preview(project_root: Path, missing: dict[str, list[str]], preview_path: Path) -> None:
    total = sum(len(facts) for facts in missing.values())
    lines = [
        "# PNW pest Prolog update preview",
        f"Total missing facts: {total}",
        "",
        "No files were modified.",
        "Run again with --apply to append these facts.",
        "",
    ]

    for key, facts in missing.items():
        relative_path = TARGET_FILES[key]

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

    output_path = project_root / preview_path
    write_text(output_path, "\n".join(lines))

    print(f"[PREVIEW] wrote {output_path}")
    print(f"[PREVIEW] total missing facts: {total}")


def apply_missing_facts(project_root: Path, missing: dict[str, list[str]]) -> None:
    for key, facts in missing.items():
        if not facts:
            continue

        path = project_root / TARGET_FILES[key]
        old_text = read_text(path)

        if old_text and not old_text.endswith("\n"):
            old_text += "\n"

        write_text(path, old_text + format_generated_block(facts, key))
        print(f"[APPLY] appended {len(facts)} facts -> {path}")


def print_summary(generated: GeneratedFacts, missing: dict[str, list[str]]) -> None:
    print("")
    print("========== PNW PEST PROLOG UPDATE SUMMARY ==========")

    for key in TARGET_FILES:
        print(f"{key:14} generated={len(generated.facts[key]):4} " f"missing={len(missing[key]):4}")

    print("====================================================")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update live Prolog files from generated PNW pest facts.")

    parser.add_argument(
        "--input",
        default=str(PATHS.data_bank / "exports" / "prolog" / "generated_pnw_pest_interactions.pl"),
        help="Generated PNW pest Prolog export file.",
    )

    parser.add_argument(
        "--project-root",
        default=str(PATHS.project_root),
        help="Project root containing logic_companion_planting/.",
    )

    parser.add_argument(
        "--preview-path",
        default="pnw_pest_prolog_update_preview.txt",
        help="Preview report path relative to project root.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually append missing facts to Prolog files.",
    )

    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    input_path = Path(args.input).expanduser()

    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()

    generated_facts = iter_generated_facts(input_path)
    routed = route_generated_facts(generated_facts)
    sort_generated_facts(routed)
    missing = filter_missing_facts(project_root, routed)

    print(f"[INFO] input facts read: {len(generated_facts)}")
    print_summary(routed, missing)
    write_preview(project_root, missing, Path(args.preview_path))

    if args.apply:
        apply_missing_facts(project_root, missing)
    else:
        print("[INFO] preview only. No Prolog files were modified.")
        print("[INFO] rerun with --apply to append missing facts.")


if __name__ == "__main__":
    main()
