% FILE: logic_companion_planting/base/insect_group.pl
%
% This file defines various insect groups (pests, beneficial insects, pollinators)
% and assigns specific insects to these groups.
% It helps categorize insects for companion planting logic.

% =========================================
% INSECT GROUPS
% =========================================

group(pest).
group(beneficial_insect).
group(pollinator).

% =========================================
% PESTS
% =========================================

member_of(aphid, pest).
member_of(whitefly, pest).
member_of(spider_mite, pest).
member_of(thrips, pest).
member_of(caterpillar, pest).
member_of(cabbage_worm, pest).
member_of(cutworm, pest).
member_of(flea_beetle, pest).
member_of(leaf_miner, pest).
member_of(mealybug, pest).
member_of(scale_insect, pest).
member_of(armyworm, pest).
member_of(grasshopper, pest).
member_of(weevil, pest).
member_of(fruit_fly, pest).

% =========================================
% BENEFICIAL INSECTS
% =========================================

member_of(ladybug, beneficial_insect).
member_of(lacewing, beneficial_insect).
member_of(parasitic_wasp, beneficial_insect).
member_of(hoverfly, beneficial_insect).
member_of(ground_beetle, beneficial_insect).
member_of(praying_mantis, beneficial_insect).
member_of(dragonfly, beneficial_insect).
member_of(spider, beneficial_insect).
member_of(honeybee, beneficial_insect).
member_of(bumblebee, beneficial_insect).
member_of(delphastus_beetle, beneficial_insect).
member_of(encarsia_formosa, beneficial_insect).

% =========================================
% POLLINATORS
% =========================================

member_of(honeybee, pollinator).
member_of(bumblebee, pollinator).
member_of(hoverfly, pollinator).