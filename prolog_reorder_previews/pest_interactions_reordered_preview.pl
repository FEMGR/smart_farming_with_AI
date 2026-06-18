% FILE: % logic_companion_planting/data/pest_interactions.pl
%
% PURPOSE:
% This file stores facts detailing specific pest-plant interactions, beneficial insect
% attraction, and disease suppression relationships within the Smart Farming System's
% companion planting logic. It focuses on how certain plants can deter pests, attract
% beneficial insects, or prevent diseases for other plants.
%
% PREDICATES DEFINED:
% - deters(Plant, Pest, Source, Confidence): Indicates that a specific plant deters a particular pest.
% - attracts_beneficial(Plant, BeneficialInsect, Source, Confidence): Shows that a plant attracts a beneficial insect.
% - prevents(Plant, Disease, Source, Confidence): States that a plant helps prevent a specific disease.
%
% RELATED MODULES:
% - `plant_fact.pl`: Provides the canonical list of plant names.
% - `insect_fact.pl`: Provides the canonical list of insect names.
% - `disease_fact.pl`: Provides the canonical list of disease names.
% - `sources_fact.pl`: Defines the sources referenced in these facts.
% - `rules/companion_rules.pl`: Utilizes these facts for inference in companion planting recommendations.
%
% USAGE:
% This file is consulted by the reasoning engine to identify direct ecological benefits
% and deterrent effects between plants, pests, and diseases, which are crucial for
% generating effective companion planting strategies.
%

% ====================================================================================================
% COMPANION PLANTING DATA (TRACEABLE)
% Sources: attra, cornell, almanac, traditional
% ====================================================================================================

% =========================================================
% PEST-PLANT INTERACTION DATA
% =========================================================

% --- Cabbage Pests ---

% =========================================================
% PEST AND BENEFICIAL INTERACTIONS BY PLANT
% Auto-organized by plant_data_bank_scripts/scripts/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% BASIL
% ---------------------------------------------------------

% =========================================================
% PEST AND BENEFICIAL INTERACTIONS BY PLANT
% Auto-organized by plant_data_bank_scripts/scripts/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% BASIL
% ---------------------------------------------------------
deters(basil, hornworm, cornell, high).
deters(basil, hornworm, ua, high).
deters(basil, mosquito, ua, medium).

% ---------------------------------------------------------
% BORAGE
% ---------------------------------------------------------
deters(borage, hornworm, attra, high).

% ---------------------------------------------------------
% CATNIP
% ---------------------------------------------------------
deters(catnip, flea_beetle, cornell, medium).

% ---------------------------------------------------------
% CHAMOMILE
% ---------------------------------------------------------
attracts_beneficial(chamomile, hoverfly, ua, medium).
attracts_beneficial(chamomile, wasp, ua, medium).

% ---------------------------------------------------------
% CHIVE
% ---------------------------------------------------------
deters(chive, aphid, cornell, high).
deters(chive, aphid, ua, high).
deters(chive, slug, ua, medium).
deters(chive, snail, ua, medium).
prevents(chive, apple_scab, ua, high).

% ---------------------------------------------------------
% GARLIC
% ---------------------------------------------------------
deters(garlic, aphid, cornell, high).

% ---------------------------------------------------------
% HORSERADISH
% ---------------------------------------------------------
deters(horseradish, colorado_potato_beetle, attra, medium).

% ---------------------------------------------------------
% LEEK
% ---------------------------------------------------------
deters(leek, carrot_rust_fly, attra, high).

% ---------------------------------------------------------
% MARIGOLD
% ---------------------------------------------------------
deters(marigold, beetle, ua, medium).
deters(marigold, nematode, attra, high).
deters(marigold, nematode, ua, high).
deters(marigold, whitefly, attra, high).

% ---------------------------------------------------------
% MINT
% ---------------------------------------------------------
deters(mint, cabbage_moth, attra, high).
deters(mint, cabbage_moth, cornell, high).

% ---------------------------------------------------------
% NASTURTIUM
% ---------------------------------------------------------
deters(nasturtium, cucumber_beetle, attra, medium).
deters(nasturtium, squash_bug, attra, high).

% ---------------------------------------------------------
% ONION
% ---------------------------------------------------------
deters(onion, carrot_fly, ua, high).
deters(onion, carrot_rust_fly, attra, high).

% ---------------------------------------------------------
% RADISH
% ---------------------------------------------------------
deters(radish, cucumber_beetle, attra, medium).
deters(radish, cucumber_beetle, traditional, medium).

% ---------------------------------------------------------
% ROSEMARY
% ---------------------------------------------------------
deters(rosemary, bean_beetle, attra, high).
deters(rosemary, cabbage_moth, attra, high).

% ---------------------------------------------------------
% SAGE
% ---------------------------------------------------------
deters(sage, cabbage_worm, traditional, high).

% ---------------------------------------------------------
% THYME
% ---------------------------------------------------------
deters(thyme, armyworm, attra, medium).

% ---------------------------------------------------------
% TOMATO
% ---------------------------------------------------------
deters(tomato, asparagus_beetle, cornell, high).
