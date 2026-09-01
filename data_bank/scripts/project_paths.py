#!/usr/bin/env python3
"""
project_paths.py

Centralized path resolver for Smart Farming System.

Purpose:
- Automatically find the project root.
- Provide stable paths for backend, Prolog KB, and plant data bank scripts.
- Prevent every script from needing long manual path arguments.

Expected project structure:

smart-farming-system/
├── backend/
│   └── cache/species_snapshots/
├── logic_companion_planting/
├── data_bank/
│   ├── config/
│   ├── data_bank/
│   │   └── normalized/plants/
│   └── scripts/
│       └── project_paths.py
└── scripts/
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

PROJECT_MARKERS = (
    "backend",
    "logic_companion_planting",
    "data_bank",
)


def find_project_root(start: Optional[Path] = None) -> Path:
    """
    Walk upward from the current file/current working directory until the
    smart-farming-system project root is found.

    The root is identified by the presence of:
        backend/
        logic_companion_planting/
        data_bank/
    """

    if start is None:
        start = Path(__file__).resolve()

    start = start.resolve()

    if start.is_file():
        candidates = [start.parent, *start.parents]
    else:
        candidates = [start, *start.parents]

    for candidate in candidates:
        if all((candidate / marker).exists() for marker in PROJECT_MARKERS):
            return candidate

    raise RuntimeError("Could not find project root. Expected a parent directory containing: " + ", ".join(PROJECT_MARKERS))


def first_existing(paths: Iterable[Path]) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path

    return None


@dataclass(frozen=True)
class ProjectPaths:
    """
    Centralized project path registry.

    Use:
        from project_paths import PATHS

        PATHS.project_root
        PATHS.backend
        PATHS.ai
        PATHS.species_snapshots
        PATHS.logic_companion
        PATHS.data_bank_scripts
    """

    project_root: Path

    @property
    def backend(self) -> Path:
        return self.project_root / "backend"

    @property
    def ai(self) -> Path:
        return self.project_root / "ai"

    @property
    def backend_app(self) -> Path:
        return self.backend / "app"

    @property
    def backend_cache(self) -> Path:
        return self.backend / "cache"

    @property
    def species_snapshots(self) -> Path:
        return self.backend_cache / "species_snapshots"

    @property
    def backend_temp(self) -> Path:
        return self.backend / "temp"

    @property
    def species_suggestions(self) -> Path:
        return self.backend_temp / "species_suggestions.json"

    @property
    def logic_companion(self) -> Path:
        return self.project_root / "logic_companion_planting"

    @property
    def prolog_base(self) -> Path:
        return self.logic_companion / "base"

    @property
    def prolog_data(self) -> Path:
        return self.logic_companion / "data"

    @property
    def plant_taxonomy_pl(self) -> Path:
        return self.prolog_base / "plant_taxonomy.pl"

    @property
    def plant_fact_pl(self) -> Path:
        return self.prolog_data / "plant_fact.pl"

    @property
    def alias_fact_pl(self) -> Path:
        return self.prolog_data / "alias_fact.pl"

    @property
    def growth_facts_pl(self) -> Path:
        return self.prolog_data / "growth_facts.pl"

    @property
    def interaction_support_pl(self) -> Path:
        return self.prolog_data / "interaction_support.pl"

    @property
    def pest_interactions_pl(self) -> Path:
        return self.prolog_data / "pest_interactions.pl"

    @property
    def sources_fact_pl(self) -> Path:
        return self.prolog_data / "sources_fact.pl"

    @property
    def plant_data_bank_scripts(self) -> Path:
        return self.project_root / "data_bank"

    @property
    def plant_data_bank_config(self) -> Path:
        return self.plant_data_bank_scripts / "config"

    @property
    def plants_seed(self) -> Path:
        return self.plant_data_bank_config / "plants_seed.json"

    @property
    def plants_seed_incremental_runtime(self) -> Path:
        return self.plant_data_bank_config / "plants_seed_incremental_runtime.json"

    @property
    def missing_plant_seed(self) -> Path:
        return self.plant_data_bank_config / "missing_plant_seed.json"

    @property
    def missing_plant_seed_runtime(self) -> Path:
        return self.plant_data_bank_config / "missing_plant_seed_runtime.json"

    @property
    def data_bank(self) -> Path:
        return self.plant_data_bank_scripts / "data_bank"

    @property
    def data_bank_raw_sources(self) -> Path:
        return self.data_bank / "raw_sources"

    @property
    def data_bank_normalized(self) -> Path:
        return self.data_bank / "normalized"

    @property
    def normalized_plants(self) -> Path:
        return self.data_bank_normalized / "plants"

    @property
    def perenual_enriched_species(self) -> Path:
        return self.data_bank_normalized / "perenual_enriched_species.json"

    @property
    def data_bank_indexes(self) -> Path:
        return self.data_bank / "indexes"

    @property
    def data_bank_scripts_dir(self) -> Path:
        return self.plant_data_bank_scripts / "scripts"

    @property
    def data_bank_manual_sources(self) -> Path:
        return self.data_bank / "manual_sources"

    @property
    def disease_sources(self) -> Path:
        return self.data_bank_manual_sources / "disease_sources.json"

    @property
    def disease_detail_sources(self) -> Path:
        return self.data_bank_manual_sources / "disease_detail_sources.json"

    @property
    def disease_bank(self) -> Path:
        return self.data_bank_normalized / "disease_bank.json"

    @property
    def pest_sources(self) -> Path:
        return self.data_bank_manual_sources / "pest_sources.json"

    @property
    def pest_bank(self) -> Path:
        return self.data_bank_normalized / "pest_bank.json.bak"

    @property
    def root_scripts(self) -> Path:
        return self.project_root / "scripts"

    def ensure_dirs(self) -> None:
        """
        Create expected writable directories if missing.
        Does not create backend/prolog root folders because those should already exist.
        """

        dirs = [
            self.plant_data_bank_config,
            self.data_bank,
            self.data_bank_raw_sources,
            self.data_bank_normalized,
            self.normalized_plants,
            self.data_bank_indexes,
            self.backend_cache,
            self.species_snapshots,
            self.backend_temp,
            self.data_bank_manual_sources,
        ]

        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def as_relative_to_root(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.project_root.resolve()))
        except ValueError:
            return str(path.resolve())

    def print_summary(self) -> None:
        print("")
        print("========== Project Paths ==========")
        print(f"Project root              : {self.project_root}")
        print(f"Backend                   : {self.backend}")
        print(f"Species snapshots         : {self.species_snapshots}")
        print(f"Backend temp              : {self.backend_temp}")
        print(f"Logic companion Prolog    : {self.logic_companion}")
        print(f"Plant data bank scripts   : {self.plant_data_bank_scripts}")
        print(f"Plants seed               : {self.plants_seed}")
        print(f"Incremental runtime seed  : {self.plants_seed_incremental_runtime}")
        print(f"Missing plant seed        : {self.missing_plant_seed}")
        print(f"Perenual enriched species : {self.perenual_enriched_species}")
        print(f"Normalized plants         : {self.normalized_plants}")
        print("===================================")
        print("")


PATHS = ProjectPaths(project_root=find_project_root())


if __name__ == "__main__":
    PATHS.ensure_dirs()
    PATHS.print_summary()
