#logic_companion_planting/data/insect_fact.pl

% -----------------------------
% INSECTS KNOWLEDGE BASE
% -----------------------------


% =========================
% PESTS
% =========================
insect(aphid).
insect(whitefly).
insect(spider_mite).
insect(thrips).
insect(caterpillar).
insect(cabbage_worm).
insect(cutworm).
insect(flea_beetle).
insect(leaf_miner).
insect(mealybug).
insect(scale_insect).
insect(armyworm).
insect(grasshopper).
insect(weevil).
insect(fruit_fly).

% =========================
% BENEFICIAL INSECTS
% =========================
insect(ladybug).
insect(lacewing).
insect(parasitic_wasp).
insect(hoverfly).
insect(ground_beetle).
insect(praying_mantis).
insect(dragonfly).
insect(spider).
insect(honeybee).
insect(bumblebee).


% =========================
% PEST TARGETS
% =========================
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

% =========================
% BENEFICIAL ACTIONS
% =========================
% =========================
% BENEFICIAL ACTIONS (EXTENDED)
% =========================
eats(ladybug, aphid).
eats(ladybug, whitefly).
eats(lacewing, aphid).
eats(lacewing, whitefly).
eats(hoverfly, aphid).
eats(hoverfly, whitefly).
eats(delphastus_beetle, whitefly).

parasitizes(parasitic_wasp, caterpillar).
parasitizes(encarsia_formosa, whitefly).
