% FILE: % logic_companion_planting/data/interaction_support.pl
%
% PURPOSE:
% This file defines direct beneficial and harmful relationships between various plants
% or plant families within the Smart Farming System's companion planting logic.
% These facts are often derived from specific research or traditional knowledge and
% serve as foundational data for more complex reasoning.
%
% PREDICATES DEFINED:
% - beneficial_relation(PlantA, PlantB, Source, Confidence): States that PlantA has a beneficial effect on PlantB.
% - harmful_relation(PlantA, PlantB, Source, Confidence): States that PlantA has a harmful effect on PlantB.
%   - PlantA, PlantB: Can be specific plant names or broader plant families (e.g., `allium_family`).
%   - Source: The origin of the information (e.g., `attra`, `cornell`).
%   - Confidence: A numerical value indicating the reliability of the relationship (e.g., 3=high, 2=medium, 1=low).
%
% RELATED MODULES:
% - `plant_fact.pl`: Provides the canonical list of plant names.
% - `base/plant_group.pl`: Provides the canonical list of plant group or family.
% - `sources_fact.pl`: Defines the sources referenced in these facts.
% - `rules/companion_rules.pl`: Utilizes these direct relationships to infer and generate
%   companion planting recommendations.
%
% USAGE:
% This file is consulted by the reasoning engine to understand explicit positive and
% negative interactions between plants, forming a core part of the companion planting
% recommendation system.
%
% =========================================================
% ECOLOGICAL SUPPORT RELATIONSHIPS
%
% Predicate:
% beneficial_relation(PlantA, PlantB, Source, Confidence).
%
% Confidence Scale:
% 3 = high
% 2 = medium
% 1 = low
%
% Sources:
% attra
% rhs
% cornell
% ua
% traditional
% =========================================================

% =========================================================
% ALLIUM (ONION, GARLIC, CHIVE)
% =========================================================

beneficial_relation(allium_family, carrot, ua, 3).
beneficial_relation(allium_family, rose, cornell, 3).
beneficial_relation(allium_family, lettuce, ua, 2).

harmful_relation(allium_family, asparagus, traditional, 1).


% =========================================================
% AMARANTH
% =========================================================

beneficial_relation(amaranth, corn, attra, 3).
beneficial_relation(amaranth, onion, attra, 3).
beneficial_relation(amaranth, potato, attra, 3).

harmful_relation(amaranth, brassica_family, attra, 3).


% =========================================================
% ASPARAGUS
% =========================================================

beneficial_relation(asparagus, basil, attra, 3).
beneficial_relation(asparagus, cilantro, attra, 3).
beneficial_relation(asparagus, parsley, attra, 3).
beneficial_relation(asparagus, tomato, attra, 3).
beneficial_relation(asparagus, comfrey, attra, 3).

harmful_relation(asparagus, allium_family, attra, 3).


% =========================================================
% BASIL
% =========================================================

beneficial_relation(basil, vegetable, attra, 3).
beneficial_relation(basil, tomato, ua, 2).

harmful_relation(basil, rue, attra, 3).


% =========================================================
% BEAN
% =========================================================

beneficial_relation(bean, vegetable, attra, 3).
beneficial_relation(bean, herb, attra, 3).
beneficial_relation(bean, marigold, attra, 3).

harmful_relation(bean, allium_family, attra, 3).
harmful_relation(bean, gladiolus, attra, 3).


% =========================================================
% BEAN BUSH
% =========================================================

beneficial_relation(bean_bush, potato, attra, 3).
beneficial_relation(bean_bush, cucumber, attra, 3).
beneficial_relation(bean_bush, corn, attra, 3).
beneficial_relation(bean_bush, strawberries, attra, 3).
beneficial_relation(bean_bush, celery, attra, 3).
beneficial_relation(bean_bush, summer_savory, attra, 3).

harmful_relation(bean_bush, allium_family, attra, 3).


% =========================================================
% BEAN POLE
% =========================================================

beneficial_relation(bean_pole, corn, attra, 3).
beneficial_relation(bean_pole, marigold, attra, 3).
beneficial_relation(bean_pole, summer_savory, attra, 3).
beneficial_relation(bean_pole, radish, attra, 3).

harmful_relation(bean_pole, allium_family, attra, 3).
harmful_relation(bean_pole, beets, attra, 3).
harmful_relation(bean_pole, kohlrabi, attra, 3).
harmful_relation(bean_pole, sunflower, attra, 3).


% =========================================================
% BEETS
% =========================================================

beneficial_relation(beets, brassica_family, attra, 3).
beneficial_relation(beets, allium_family, attra, 3).
beneficial_relation(beets, lettuce, attra, 3).

harmful_relation(beets, bean_pole, attra, 3).


% =========================================================
% BRASSICA (CABBAGE, BROCCOLI, KALE)
% =========================================================

beneficial_relation(brassica, sage, cornell, 3).
beneficial_relation(brassica, mint, ua, 2).

harmful_relation(brassica, strawberries, traditional, 1).


% =========================================================
% CABBAGE
% =========================================================

beneficial_relation(cabbage, allium_family, attra, 3).
beneficial_relation(cabbage, chamomile, attra, 3).
beneficial_relation(cabbage, celery, attra, 3).
beneficial_relation(cabbage, clover, attra, 3).
beneficial_relation(cabbage, spinach, attra, 3).

harmful_relation(cabbage, dill, attra, 3).
harmful_relation(cabbage, bean_pole, attra, 3).
harmful_relation(cabbage, strawberries, attra, 3).
harmful_relation(cabbage, tomato, attra, 3).


% =========================================================
% CARROT
% =========================================================

beneficial_relation(carrot, allium_family, attra, 3).
beneficial_relation(carrot, pea_english, attra, 3).
beneficial_relation(carrot, lettuce, attra, 3).
beneficial_relation(carrot, rosemary, attra, 3).
beneficial_relation(carrot, sage, attra, 3).
beneficial_relation(carrot, tomato, attra, 3).

harmful_relation(carrot, dill, attra, 3).
harmful_relation(carrot, fennel, attra, 3).


% =========================================================
% CORN
% =========================================================

beneficial_relation(corn, bean, attra, 3).
beneficial_relation(corn, cucumber, attra, 3).
beneficial_relation(corn, pea_english, attra, 3).
beneficial_relation(corn, potato, attra, 3).
beneficial_relation(corn, pumpkin, attra, 3).
beneficial_relation(corn, squash, attra, 3).

harmful_relation(corn, tomato, attra, 3).


% =========================================================
% CUCUMBER
% =========================================================

beneficial_relation(cucumber, bean, attra, 3).
beneficial_relation(cucumber, cabbage, attra, 3).
beneficial_relation(cucumber, corn, attra, 3).
beneficial_relation(cucumber, pea_english, attra, 3).
beneficial_relation(cucumber, radish, attra, 3).
beneficial_relation(cucumber, sunflower, attra, 3).
beneficial_relation(cucumber, nasturtium, ua, 2).

harmful_relation(cucumber, herb, attra, 2).
harmful_relation(cucumber, potato, attra, 3).
harmful_relation(cucumber, sage, ua, 2).


% =========================================================
% FENNEL
% =========================================================

harmful_relation(fennel, vegetable, attra, 3).


% =========================================================
% LETTUCE
% =========================================================

beneficial_relation(lettuce, carrot, attra, 3).
beneficial_relation(lettuce, cucumber, attra, 3).
beneficial_relation(lettuce, radish, attra, 3).
beneficial_relation(lettuce, strawberries, attra, 3).

% =========================================================
% MELONS
% =========================================================

beneficial_relation(melons, amaranth, attra, 3).
beneficial_relation(melons, bean, attra, 3).
beneficial_relation(melons, chamomile, attra, 3).
beneficial_relation(melons, corn, attra, 3).

harmful_relation(melons, brassica_family, attra, 3).

% =========================================================
% OKRA
% =========================================================

beneficial_relation(okra, pepper, attra, 3).
beneficial_relation(okra, squash, attra, 3).
beneficial_relation(okra, sweet_potato, attra, 3).

harmful_relation(okra, bean, attra, 3).
harmful_relation(okra, pea_english, attra, 3).

% =========================================================
% ONION
% =========================================================

beneficial_relation(onion, beets, attra, 3).
beneficial_relation(onion, brassica_family, attra, 3).
beneficial_relation(onion, carrot, attra, 3).
beneficial_relation(onion, lettuce, attra, 3).
beneficial_relation(onion, summer_savory, attra, 3).


% =========================================================
% PEPPER
% =========================================================

beneficial_relation(pepper, basil, attra, 3).
beneficial_relation(pepper, clover, attra, 3).
beneficial_relation(pepper, tomato, attra, 3).

harmful_relation(pepper, brassica_family, attra, 3).


% =========================================================
% POTATO
% =========================================================

beneficial_relation(potato, basil, attra, 3).
beneficial_relation(potato, bean, attra, 3).
beneficial_relation(potato, brassica_family, attra, 3).
beneficial_relation(potato, horseradish, attra, 3).
beneficial_relation(potato, marigold, attra, 3).
beneficial_relation(potato, tansy, ua, 3).

harmful_relation(potato, tomato, traditional, 3).
harmful_relation(potato, sunflower, ua, 2).
harmful_relation(potato, cucumber, traditional, 1).
harmful_relation(potato, squash, traditional, 1).


% =========================================================
% PUMPKIN
% =========================================================

beneficial_relation(pumpkin, corn, attra, 3).
beneficial_relation(pumpkin, marigold, attra, 3).

harmful_relation(pumpkin, squash, attra, 3).
harmful_relation(pumpkin, tomato, attra, 3).
harmful_relation(pumpkin, sunflower, attra, 3).

% =========================================================
% RADISH
% =========================================================

beneficial_relation(radish, cucumber, attra, 3).
beneficial_relation(radish, pea_english, attra, 3).
beneficial_relation(radish, lettuce, attra, 3).
beneficial_relation(radish, nasturtium, attra, 3).

harmful_relation(radish, potato, attra, 3).


% =========================================================
% SPINACH
% =========================================================

beneficial_relation(spinach, celery, attra, 3).
beneficial_relation(spinach, strawberries, attra, 3).

harmful_relation(spinach, hyssop, attra, 3).


% =========================================================
% STRAWBERRIES
% =========================================================

beneficial_relation(strawberries, borage, attra, 3).
beneficial_relation(strawberries, bean_bush, attra, 3).
beneficial_relation(strawberries, lettuce, attra, 3).
beneficial_relation(strawberries, pyrethrum, attra, 3).
beneficial_relation(strawberries, caraway, attra, 3).

harmful_relation(strawberries, potato, attra, 3).

% =========================================================
% SUNFLOWER
% =========================================================

beneficial_relation(sunflower, bean, attra, 3).
beneficial_relation(sunflower, corn, attra, 3).
beneficial_relation(sunflower, cucumber, attra, 3).
beneficial_relation(sunflower, melons, attra, 3).
beneficial_relation(sunflower, peanut, attra, 3).

harmful_relation(sunflower, potato, attra, 3).

% =========================================================
% SQUASH
% =========================================================

beneficial_relation(squash, nasturtium, attra, 3).
beneficial_relation(squash, corn, traditional, 1).
beneficial_relation(squash, marigold, attra, 3).

harmful_relation(squash, potato, traditional, 1).


% =========================================================
% TOMATO
% =========================================================

beneficial_relation(tomato, allium_family, attra, 3).
beneficial_relation(tomato, asparagus, attra, 3).
beneficial_relation(tomato, basil, attra, 3).
beneficial_relation(tomato, carrot, attra, 3).
beneficial_relation(tomato, cucumber, attra, 3).
beneficial_relation(tomato, marigold, attra, 3).
beneficial_relation(tomato, nasturtium, attra, 3).
beneficial_relation(tomato, parsley, attra, 3).
beneficial_relation(tomato, rosemary, attra, 3).

harmful_relation(tomato, bean_pole, attra, 3).


% =========================================================
% WATERMELON
% =========================================================

beneficial_relation(watermelon, nasturtium, attra, 3).
beneficial_relation(watermelon, marigold, attra, 3).

harmful_relation(watermelon, potato, attra, 3).
harmful_relation(watermelon, mustard, attra, 3).
