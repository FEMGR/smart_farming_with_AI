% FILE: logic_companion_planting/base/plant_group.pl
%
% This file defines various plant groups and assigns specific plants to these groups.
% It helps categorize plants for companion planting logic.

% =========================================
% GROUP DEFINITIONS
% =========================================

group(legume_family).
group(fruiting_crop).
group(fruit).
group(leafy_green).
group(allium_family).
group(vegetable).
group(brassica_family).
group(herb).
group(berry).
group(grain_crop).
group(root_crop).
group(rhizome_crop).
group(spice).
group(pepper_family).
group(flower).
group(vine).
group(grass).
group(weed).

% =========================================
% LEGUMES
% =========================================

member_of(bean_bush, legume_family).
member_of(bean_pole, legume_family).
member_of(pea, legume_family).
member_of(pea_english, legume_family).
member_of(peanut, legume_family).

% =========================================
% FRUITING CROPS
% =========================================

member_of(tomato, fruiting_crop).
member_of(peppers, fruiting_crop).
member_of(eggplant, fruiting_crop).
member_of(cucumber, fruiting_crop).
member_of(melons, fruiting_crop).
member_of(watermelon, fruiting_crop).
member_of(squash, fruiting_crop).
member_of(pumpkins, fruiting_crop).
member_of(gourds, fruiting_crop).
member_of(okra, fruiting_crop).

% =========================================
% FRUITS
% =========================================

member_of(melons, fruit).
member_of(watermelon, fruit).
member_of(cucumber, fruit).
member_of(grapes, fruit).
member_of(blackberries, fruit).

% =========================================
% LEAFY GREENS
% =========================================

member_of(lettuce, leafy_green).
member_of(spinach, leafy_green).
member_of(cabbage, leafy_green).
member_of(kale, leafy_green).
member_of(arugula, leafy_green).
member_of(bok_choy, leafy_green).
member_of(choy_sum, leafy_green).
member_of(mustard_greens, leafy_green).
member_of(swiss_chard, leafy_green).
member_of(water_spinach, leafy_green).

% =========================================
% ALLIUM FAMILY
% =========================================

member_of(onion, allium_family).
member_of(chives, allium_family).
member_of(garlic, allium_family).
member_of(green_onion, allium_family).
member_of(leek, allium_family).
member_of(shallot, allium_family).

% =========================================
% BRASSICAS
% =========================================

member_of(cabbage, brassica_family).
member_of(broccoli, brassica_family).
member_of(brussels_sprout, brassica_family).
member_of(cauliflower, brassica_family).
member_of(kale, brassica_family).
member_of(bok_choy, brassica_family).
member_of(choy_sum, brassica_family).
member_of(mustard_greens, brassica_family).
member_of(turnip, brassica_family).
member_of(radish, brassica_family).
member_of(arugula, brassica_family).

% =========================================
% HERBS
% =========================================

member_of(basil, herb).
member_of(parsley, herb).
member_of(rosemary, herb).
member_of(thyme, herb).
member_of(oregano, herb).
member_of(mint, herb).
member_of(sage, herb).
member_of(cilantro, herb).
member_of(dill, herb).
member_of(fennel, herb).
member_of(tarragon, herb).
member_of(lavender, herb).
member_of(lemon_balm, herb).
member_of(chamomile, herb).
member_of(comfrey, herb).
member_of(rue, herb).
member_of(summer_savory, herb).
member_of(hyssop, herb).
member_of(borage, herb).
member_of(caraway, herb).
member_of(catnip, herb).
member_of(lemongrass, herb).
member_of(tansy, herb).

% =========================================
% ROOT CROPS
% =========================================

member_of(carrot, root_crop).
member_of(beets, root_crop).
member_of(radish, root_crop).
member_of(turnip, root_crop).
member_of(potato, root_crop).
member_of(sweet_potato, root_crop).
member_of(taro, root_crop).

% =========================================
% FLOWERS
% =========================================

member_of(calendula, flower).
member_of(viola, flower).
member_of(rose, flower).
member_of(hibiscus, flower).
member_of(jasmine, flower).
member_of(chrysanthemum, flower).
member_of(cornflower, flower).
member_of(dandelion, flower).
member_of(elderflower, flower).
member_of(bee_balm, flower).
member_of(yarrow, flower).
member_of(clover, flower).
member_of(sunflower, flower).
member_of(gladiolus, flower).
member_of(nasturtium, flower).

% =========================================
% GRAINS
% =========================================

member_of(amaranth, grain_crop).
member_of(corn, grain_crop).
member_of(rice, grain_crop).
member_of(barley, grain_crop).
member_of(wheat, grain_crop).
member_of(spelt, grain_crop).

% =========================================
% SPICES
% =========================================

member_of(ginger, spice).
member_of(turmeric, spice).
member_of(galangal, spice).
member_of(kencur, spice).
member_of(cinnamon, spice).
member_of(nutmeg, spice).

% =========================================
% PEPPERS
% =========================================

member_of(bell_pepper, pepper_family).
member_of(chili_pepper, pepper_family).
member_of(black_pepper, pepper_family).
member_of(white_pepper, pepper_family).

% =========================================
% VINES
% =========================================

member_of(gourds, vine).
member_of(grapes, vine).
member_of(blackberries, vine).

% =========================================
% BERRIES
% =========================================

member_of(strawberries, berry).
member_of(blackberries, berry).
member_of(blueberries, berry).
member_of(raspberries, berry).

% =========================================
% WEEDS
% =========================================

member_of(johnson_grass, weed).