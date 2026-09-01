from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "data_bank" / "scripts" / "prolog" / "reorder_prolog_facts_by_plant.py"

spec = importlib.util.spec_from_file_location("reorder_prolog_facts_by_plant", MODULE_PATH)
reorder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = reorder
spec.loader.exec_module(reorder)


def test_reorder_text_is_idempotent_after_generated_preamble_comments():
    text = """% FILE: logic_companion_planting/data/plant_fact.pl
%
% =========================================================
% PLANT REGISTRY
% =========================================================

% =========================================================
% PLANT FACTS BY PLANT
% Auto-organized by data_bank/scripts/prolog/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% AMARANTH
% ---------------------------------------------------------

% =========================================================
% PLANT FACTS BY PLANT
% Auto-organized by data_bank/scripts/prolog/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% AMARANTH
% ---------------------------------------------------------
plant(amaranth).
scientific_name(amaranth, 'amaranthus spp.').
"""

    once = reorder.reorder_text(text, reorder.FILE_CONFIGS["plant_fact"])
    twice = reorder.reorder_text(once, reorder.FILE_CONFIGS["plant_fact"])

    assert once == twice
    assert once.count("% PLANT FACTS BY PLANT") == 1
    assert once.count("% AMARANTH") == 1
    assert "% PLANT REGISTRY" in once
