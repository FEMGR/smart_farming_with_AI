
#logic_companion_planting/base/plant_taxonomy.pl

% ===== LEGUMES =====
is_a(beans, legume).
is_a(beans_bush, legume).
is_a(beans_pole, legume).
is_a(pea, legume).
is_a(pea_english, legume).
is_a(peanut, legume).

% ===== FRUITING CROPS =====
is_a(tomato, fruiting_crop).
is_a(peppers, fruiting_crop).
is_a(eggplant, fruiting_crop).
is_a(cucumber, fruiting_crop).
is_a(melons, fruiting_crop).
is_a(watermelon, fruiting_crop).
is_a(squash, fruiting_crop).
is_a(pumpkins, fruiting_crop).
is_a(gourds, fruiting_crop).
is_a(okra, fruiting_crop).

% ===== FRUITS =====
is_a(melons, fruit).
is_a(watermelon, fruit).
is_a(cucumber, fruit).
is_a(grapes, fruit).
is_a(blackberries, fruit).

% ===== LEAFY GREENS =====
is_a(lettuce, leafy_green).
is_a(spinach, leafy_green).
is_a(cabbage, leafy_green).
is_a(kale, leafy_green).
is_a(arugula, leafy_green).
is_a(bok_choy, leafy_green).
is_a(choy_sum, leafy_green).
is_a(mustard_greens, leafy_green).
is_a(swiss_chard, leafy_green).
is_a(water_spinach, leafy_green).

% ===== ALLIUM FAMILY =====
is_a(onion, allium).
is_a(chives, allium).
is_a(garlic, allium).
is_a(green_onion, allium).
is_a(leek, allium).
is_a(shallot, allium).

% ===== VEGETABLES =====
is_a(celery, vegetable).
is_a(asparagus, vegetable).
is_a(artichokes, vegetable).
is_a(zucchini, vegetable).
is_a(eggplant, vegetable).
is_a(cucumber, vegetable).
is_a(pumpkin, vegetable).
is_a(bell_pepper, vegetable).
is_a(chili_pepper, vegetable).
is_a(cauliflower, vegetable).
is_a(broccoli, vegetable).
is_a(okra, vegetable).
is_a(green_beans, vegetable).
is_a(sweet_corn, vegetable).

% ===== BRASSICAS =====
is_a(cabbage, brassica).
is_a(broccoli, brassica).
is_a(brussels_sprout, brassica).
is_a(cauliflower, brassica).
is_a(kale, brassica).
is_a(bok_choy, brassica).
is_a(choy_sum, brassica).
is_a(mustard_greens, brassica).
is_a(turnip, brassica).
is_a(radish, brassica).
is_a(arugula, brassica).

% ===== HERBS =====
is_a(basil, herb).
is_a(parsley, herb).
is_a(rosemary, herb).
is_a(thyme, herb).
is_a(oregano, herb).
is_a(mint, herb).
is_a(sage, herb).
is_a(chives, herb).
is_a(cilantro, herb).
is_a(dill, herb).
is_a(fennel, herb).
is_a(tarragon, herb).
is_a(lavender, herb).
is_a(lemon_balm, herb).
is_a(chamomile, herb).

% ===== BRASSICAS =====
is_a(cabbage, brassica).
is_a(broccoli, brassica).
is_a(brussel sprout, brassica).

% ===== BERRIES =====
is_a(strawberries, berry).
is_a(blackberries, berry).
is_a(blueberries, berry).
is_a(raspberries, berry).

% ===== CROPS =====
is_a(amaranth, grain_crop).
is_a(corn, grain_crop).
is_a(rice, grain_crop).
is_a(barley, grain_crop).
is_a(wheat, grain_crop).
is_a(spelt, grain_crop).

% ===== ROOT CROPS =====
is_a(carrots, root_crop).
is_a(beets, root_crop).
is_a(radish, root_crop).
is_a(turnip, root_crop).
is_a(potato, root_crop).
is_a(sweet_potato, root_crop).
is_a(taro, root_crop).

% ===== RHIZOMES (INDONESIAN SPICES) =====
is_a(ginger, rhizome_crop).
is_a(turmeric, rhizome_crop).
is_a(galangal, rhizome_crop).
is_a(lesser_galangal, rhizome_crop).
is_a(fingerroot, rhizome_crop).
is_a(temulawak, rhizome_crop).
is_a(temu_ireng, rhizome_crop).
is_a(temu_kunci, rhizome_crop).
is_a(temu_mangga, rhizome_crop).
is_a(kencur, rhizome_crop).
is_a(lengkuas, rhizome_crop).

% ===== SPICES =====
is_a(ginger, spice).
is_a(turmeric, spice).
is_a(galangal, spice).
is_a(kencur, spice).
is_a(temulawak, spice).
is_a(cinnamon, spice).
is_a(cinnamon, tree_crop).
is_a(nutmeg, spice).
is_a(nutmeg, tree_crop).

% ===== PEPPERS =====
is_a(black_pepper, spice).
is_a(black_pepper, vine).
is_a(white_pepper, spice).
is_a(bell_pepper, peppers).
is_a(chili_pepper, peppers).

% ===== EDIBLE FLOWERS  =====
is_a(calendula, flowering_crop).
is_a(viola, flowering_crop).
is_a(rose, flowering_crop).
is_a(hibiscus, flowering_crop).
is_a(jasmine, flowering_crop).
is_a(chrysanthemum, flowering_crop).
is_a(cornflower, flowering_crop).
is_a(dandelion, flowering_crop).
is_a(elderflower, flowering_crop).
is_a(bee_balm, flowering_crop).
is_a(yarrow, flowering_crop).
is_a(clover, flowering_crop).


% ===== VINES =====
is_a(gourds, vine).
is_a(grapes, vine).
is_a(blackberries, vine).

% =========================
% CATEGORICAL
% =========================

% =========================
% LEGUMES
% =========================

belongs_to(bean, bean).
belongs_to(bean_bush, bean).
belongs_to(bean_pole, bean).
belongs_to(pea, bean).
belongs_to(pea_english, bean).
belongs_to(peanut, bean).


% =========================
% FRUITING CROPS
% =========================

belongs_to(tomato, vegetable).
belongs_to(melons, vegetable).
belongs_to(watermelon, vegetable).
belongs_to(squash, vegetable).
belongs_to(gourd, vegetable).


% =========================
% ROOT CROPS
% =========================

belongs_to(carrot, vegetable).
belongs_to(beets, vegetable).
belongs_to(radish, vegetable).
belongs_to(turnip, vegetable).
belongs_to(sweet_potato, vegetable).
belongs_to(taro, vegetable).
belongs_to(horseradish, vegetable).


% =========================
% LEAFY GREENS
% =========================

belongs_to(lettuce, vegetable).
belongs_to(spinach, vegetable).
belongs_to(cabbage, brassica).
belongs_to(kale, brassica).
belongs_to(arugula, brassica).
belongs_to(bok_choy, brassica).
belongs_to(choy_sum, brassica).
belongs_to(mustard_greens, brassica).
belongs_to(swiss_chard, vegetable).
belongs_to(water_spinach, vegetable).
belongs_to(purslane, vegetable).


% =========================
% ALLIUMS
% =========================

belongs_to(onion, allium).
belongs_to(chives, allium).
belongs_to(garlic, allium).
belongs_to(green_onion, allium).
belongs_to(leek, allium).
belongs_to(shallot, allium).


% =========================
% VEGETABLES (GENERAL)
% =========================

belongs_to(celery, vegetable).
belongs_to(asparagus, vegetable).
belongs_to(artichokes, vegetable).
belongs_to(zucchini, vegetable).
belongs_to(eggplant, vegetable).
belongs_to(cucumber, vegetable).
belongs_to(pumpkin, vegetable).
belongs_to(okra, vegetable).
belongs_to(sweet_corn, grain).

belongs_to(bell_pepper, pepper).
belongs_to(chili_pepper, pepper).


% =========================
% BRASSICAS
% =========================

belongs_to(broccoli, brassica).
belongs_to(brussels_sprout, brassica).
belongs_to(cauliflower, brassica).
belongs_to(kohlrabi, brassica).
belongs_to(mustard, brassica).


% =========================
% HERBS
% =========================

belongs_to(basil, herb).
belongs_to(parsley, herb).
belongs_to(rosemary, herb).
belongs_to(thyme, herb).
belongs_to(oregano, herb).
belongs_to(mint, herb).
belongs_to(sage, herb).
belongs_to(cilantro, herb).
belongs_to(dill, herb).
belongs_to(fennel, herb).
belongs_to(tarragon, herb).
belongs_to(lavender, herb).
belongs_to(lemon_balm, herb).
belongs_to(chamomile, herb).
belongs_to(comfrey, herb).
belongs_to(rue, herb).
belongs_to(summer_savory, herb).
belongs_to(hyssop, herb).
belongs_to(borage, herb).
belongs_to(caraway, herb).
belongs_to(catnip, herb).
belongs_to(lemongrass, herb).
belongs_to(tansy, herb).

% =========================
% RHIZOMES (INDONESIAN SPICES)
% =========================

belongs_to(ginger, herb).
belongs_to(turmeric, herb).
belongs_to(galangal, herb).
belongs_to(lesser_galangal, herb).
belongs_to(fingerroot, herb).
belongs_to(temulawak, herb).
belongs_to(temu_ireng, herb).
belongs_to(temu_kunci, herb).
belongs_to(temu_mangga, herb).
belongs_to(kencur, herb).


% =========================
% GRAIN CROPS
% =========================

belongs_to(amaranth, grain).
belongs_to(corn, grain).
belongs_to(rice, grain).
belongs_to(barley, grain).
belongs_to(wheat, grain).
belongs_to(spelt, grain).
belongs_to(sorghum, grain).

belongs_to(sugarcane, grass).



% =========================
% FLOWERS
% =========================

belongs_to(calendula, flower).
belongs_to(viola, flower).
belongs_to(rose, flower).
belongs_to(hibiscus, flower).
belongs_to(jasmine, flower).
belongs_to(chrysanthemum, flower).
belongs_to(cornflower, flower).
belongs_to(dandelion, flower).
belongs_to(elderflower, flower).
belongs_to(bee_balm, flower).
belongs_to(yarrow, flower).
belongs_to(clover, flower).
belongs_to(sunflower, flower).
belongs_to(gladiolus, flower).
belongs_to(nasturtium, flower).
belongs_to(pyrethrum, flower).
belongs_to(dahlia, flower).
belongs_to(tulip, flower).


% =========================
% FRUITS / VINES
% =========================
belongs_to(grapes, fruit).


% =========================
% BERRIES
% =========================

belongs_to(strawberries, fruit).
belongs_to(blackberries, fruit).
belongs_to(blueberries, fruit).
belongs_to(raspberries, fruit).


% =========================
% SPICES
% =========================

belongs_to(cinnamon, herb).
belongs_to(nutmeg, herb).
belongs_to(black_pepper, pepper).
belongs_to(white_pepper, pepper).


% =========================
% WEEDS / INVASIVE
% =========================

belongs_to(johnson_grass, weed).