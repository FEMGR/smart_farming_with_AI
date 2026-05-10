% FILE: logic_companion_planting/data/insect_fact.pl
%
% PURPOSE:
% This file defines facts related to insect interactions within the Smart Farming System's
% companion planting logic. It categorizes insects as pests or beneficial organisms
% and details their relationships with plants, including pest attacks, beneficial predation,
% parasitic control, and pollination activities.
%
% PREDICATES DEFINED:
% - attacks(Pest, Plant): Indicates that a specific pest attacks a particular plant.
% - eats(BeneficialInsect, Pest): Describes a beneficial insect preying on a pest.
% - parasitizes(Parasite, Host): Details a parasitic relationship between an insect and a host.
% - pollinates(Pollinator, Plant): Identifies insects that pollinate specific plants.
%
% RELATED MODULES:
% - `plant_fact.pl`: Provides the canonical list of plant names referenced in this file.
% - `companion_fact.pl`: May use these insect interactions to infer companion planting relationships.
% - `rules/companion_rules.pl`: Utilizes these facts for inference regarding pest control and pollination.
%
% USAGE:
% This file is consulted by the reasoning engine to understand the ecological roles of various
% insects and their direct impact on plants, informing companion planting recommendations.
%

% =========================================================
% INSECT ECOLOGICAL KNOWLEDGE BASE
% =========================================================

% =========================================================
% PEST ATTACK RELATIONSHIPS
% =========================================================

attacks(aphid, tomato).
attacks(aphid, pepper).
attacks(aphid, bean).

attacks(cabbage_worm, cabbage).
attacks(cabbage_worm, broccoli).

attacks(spider_mite, cucumber).
attacks(spider_mite, eggplant).

attacks(flea_beetle, eggplant).
attacks(flea_beetle, radish).

attacks(whitefly, tomato).
attacks(whitefly, cucumber).

attacks(cutworm, lettuce).
attacks(cutworm, cabbage).

attacks(thrips, onion).
attacks(thrips, pepper).

attacks(armyworm, corn).
attacks(armyworm, spinach).


% =========================================================
% BENEFICIAL PREDATION
% =========================================================

eats(ladybug, aphid).
eats(ladybug, whitefly).

eats(lacewing, aphid).
eats(lacewing, whitefly).

eats(hoverfly, aphid).
eats(hoverfly, whitefly).

eats(delphastus_beetle, whitefly).

eats(ground_beetle, cutworm).

eats(praying_mantis, grasshopper).


% =========================================================
% PARASITIC CONTROL
% =========================================================

parasitizes(parasitic_wasp, caterpillar).

parasitizes(encarsia_formosa, whitefly).


% =========================================================
% POLLINATION
% =========================================================

pollinates(honeybee, squash).
pollinates(honeybee, cucumber).

pollinates(bumblebee, tomato).
pollinates(bumblebee, pepper).

pollinates(hoverfly, strawberry).
