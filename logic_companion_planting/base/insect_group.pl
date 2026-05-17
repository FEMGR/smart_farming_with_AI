% FILE: logic_companion_planting/base/insect_group.pl
%
% This file defines various insect groups (pests, beneficial insects, pollinators)
% and assigns specific insects to these groups.
% It helps categorize insects for companion planting logic.

% =========================================
% INSECT GROUPS
% =========================================

insect_group(pest).
insect_group(beneficial_insect).
insect_group(pollinator).

% =========================================
% PESTS
% =========================================

insect_member_of(aphid, pest).
insect_member_of(whitefly, pest).
insect_member_of(spider_mite, pest).
insect_member_of(thrips, pest).
insect_member_of(caterpillar, pest).
insect_member_of(cabbage_worm, pest).
insect_member_of(cutworm, pest).
insect_member_of(flea_beetle, pest).
insect_member_of(leaf_miner, pest).
insect_member_of(mealybug, pest).
insect_member_of(scale_insect, pest).
insect_member_of(armyworm, pest).
insect_member_of(grasshopper, pest).
insect_member_of(weevil, pest).
insect_member_of(fruit_fly, pest).

% =========================================
% BENEFICIAL INSECTS
% =========================================

insect_member_of(ladybug, beneficial_insect).
insect_member_of(lacewing, beneficial_insect).
insect_member_of(parasitic_wasp, beneficial_insect).
insect_member_of(hoverfly, beneficial_insect).
insect_member_of(ground_beetle, beneficial_insect).
insect_member_of(praying_mantis, beneficial_insect).
insect_member_of(dragonfly, beneficial_insect).
insect_member_of(spider, beneficial_insect).
insect_member_of(honeybee, beneficial_insect).
insect_member_of(bumblebee, beneficial_insect).
insect_member_of(delphastus_beetle, beneficial_insect).
insect_member_of(encarsia_formosa, beneficial_insect).

% =========================================
% POLLINATORS
% =========================================

insect_member_of(honeybee, pollinator).
insect_member_of(bumblebee, pollinator).
insect_member_of(hoverfly, pollinator).