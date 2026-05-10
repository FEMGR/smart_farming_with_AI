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
deters(sage, cabbage_worm, traditional, high).
deters(mint, cabbage_moth, attra, high).

% --- Tomato Pests ---
deters(basil, hornworm, cornell, high).
deters(marigold, whitefly, attra, high).
deters(borage, hornworm, attra, high).

% --- Cucumber & Squash Pests ---
deters(nasturtium, cucumber_beetle, attra, medium).
deters(nasturtium, squash_bug, attra, high).
deters(radish, cucumber_beetle, traditional, medium).

% --- Carrot & Bean Pests ---
deters(onion, carrot_rust_fly, attra, high).
deters(rosemary, bean_beetle, attra, high).

% --- General Pest Interactions ---
deters(garlic, aphid, cornell, high).
deters(marigold, nematode, attra, high).

deters(mint, cabbage_moth, cornell, high).
deters(rosemary, cabbage_moth, attra, high).
deters(borage, hornworm, attra, high).
deters(radish, cucumber_beetle, attra, medium).
deters(catnip, flea_beetle, cornell, medium).
deters(leek, carrot_rust_fly, attra, high).
deters(horseradish, colorado_potato_beetle, attra, medium).
deters(chives, aphid, cornell, high).
deters(tomato, asparagus_beetle, cornell, high).
deters(thyme, armyworm, attra, medium).


% =========================================================
% UNIVERSITY OF ARIZONA (UA) COMPANION DATA
% =========================================================

% --- Scent Masking & Deterrents ---
deters(onion, carrot_fly, ua, high).
deters(chives, aphid, ua, high).
deters(chives, slug, ua, medium).
deters(chives, snail, ua, medium).

% --- General Pest Protection ---
deters(marigold, nematode, ua, high).
deters(marigold, beetle, ua, medium).
deters(basil, hornworm, ua, high).
deters(basil, mosquito, ua, medium).

% --- Beneficial Attraction (Arizona Guide) ---
attracts_beneficial(chamomile, hoverfly, ua, medium).
attracts_beneficial(chamomile, wasp, ua, medium).
attracts_beneficial(carrot, ladybug, ua, high). % Carrots in flower

% --- Disease Suppression ---
prevents(chives, apple_scab, ua, high).
