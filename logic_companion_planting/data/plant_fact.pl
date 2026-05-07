#logic_companion_planting/data/plant_fact.pl


% =========================
% LEGUMES
% =========================
plant(bean).
plant(bean_bush).
plant(bean_pole).
plant(pea).
plant(pea_english).
plant(peanut).

% =========================
% FRUITING CROPS
% =========================
plant(tomato).
plant(melons).
plant(watermelon).
plant(squash).
plant(gourd).

% =========================
% ROOT CROPS
% =========================
plant(carrot).
plant(beets).
plant(radish).
plant(turnip).
plant(sweet_potato).
plant(taro).
plant(horseradish).
plant(potato). % Added

% =========================
% LEAFY GREENS
% =========================
plant(lettuce).
plant(spinach).
plant(cabbage).
plant(kale).
plant(arugula).
plant(bok_choy).
plant(choy_sum).
plant(mustard_greens).
plant(swiss_chard).
plant(water_spinach).
plant(purslane).

% =========================
% ALLIUMS
% =========================
plant(onion).
plant(chives).
plant(garlic).
plant(green_onion).
plant(leek).
plant(shallot).

% =========================
% VEGETABLES (GENERAL)
% =========================
plant(celery).
plant(asparagus).
plant(artichokes).
plant(zucchini).
plant(eggplant).
plant(cucumber).
plant(pumpkin).
plant(bell_pepper).
plant(chili_pepper).
plant(okra).
plant(sweet_corn).

% =========================
% BRASSICAS (subset already included above)
% =========================
plant(broccoli).
plant(brussels_sprout).
plant(cauliflower).
plant(kohlrabi).
plant(mustard).

% =========================
% HERBS
% =========================
plant(basil).
plant(parsley).
plant(rosemary).
plant(thyme).
plant(oregano).
plant(mint).
plant(sage).
plant(cilantro).
plant(dill).
plant(fennel).
plant(tarragon).
plant(lavender).
plant(lemon_balm).
plant(chamomile).
plant(comfrey).
plant(rue).
plant(summer_savory).
plant(hyssop).
plant(borage).
plant(caraway).
plant(catnip).
plant(lemongrass).
plant(tansy).


% =========================
% GRAIN CROPS
% =========================
plant(amaranth).
plant(corn).
plant(rice).
plant(barley).
plant(wheat).
plant(spelt).
plant(sorghum).
plant(sugarcane).


% =========================
% RHIZOMES (INDONESIAN SPICES)
% =========================
plant(ginger).
plant(turmeric).
plant(galangal).
alias(lengkuas, galangal).
plant(lesser_galangal).
plant(fingerroot).
plant(temulawak).
plant(temu_ireng).
plant(temu_kunci).
plant(temu_mangga).
plant(kencur).


% =========================
% EDIBLE FLOWERS (EXTENDED)
% =========================
plant(calendula).
plant(viola).
plant(rose).
plant(hibiscus).
plant(jasmine).
plant(chrysanthemum).
plant(cornflower).
plant(dandelion).
plant(elderflower).
plant(bee_balm).
plant(yarrow).
plant(clover).
plant(sunflower).
plant(gladiolus).
plant(nasturtium).
plant(pyrethrum).
plant(tulip).
plant(dahlia).

% =========================
% FRUITS
% =========================
plant(grapes).
plant(apple).
plant(pear).


% =========================
% BERRIES
% =========================
plant(strawberries).
plant(blackberries).
plant(blueberries).
plant(raspberries).

% =========================
% SPICES
% =========================
plant(cinnamon).
plant(nutmeg).
plant(black_pepper).
plant(white_pepper).
plant(juniper).

% =========================
% ORNAMENTALS / FRUIT TREES
% =========================
plant(privet). % Added
plant(lilac). % Added
plant(viburnum). % Added
plant(prunus). % Added
plant(phlox). % Added
plant(cotoneaster). % Added
plant(buxus). % Added
plant(rhododendron). % Added
plant(yew). % Added
plant(cyclamen). % Added

% =========================
% WEEDS / INVASIVE
% =========================
plant(johnson_grass).


% ====================================================================================================
% PLANT FUNCTIONAL TRAITS
% ====================================================================================================

% Pest repellents
function(lemongrass, pest_repellent).
function(catnip, pest_repellent).
function(rue, pest_repellent).
function(tansy, pest_repellent).
function(chives, pest_repellent).
function(garlic, pest_repellent).

% Trap crops
function(nasturtium, pest_trap).

% Pollinator attractors
function(borage, pollinator_attractor).
function(clover, pollinator_attractor).
function(yarrow, pollinator_attractor).

% Soil improvers
function(comfrey, nutrient_accumulator).
function(bean, nitrogen_fixer).
function(bean_bush, nitrogen_fixer).
function(bean_pole, nitrogen_fixer).
function(pea, nitrogen_fixer).
function(peanut, nitrogen_fixer).

% Ground cover
function(sweet_potato, ground_cover).
function(squash, ground_cover).

% Tropical rhizomes (key for YOUR system)
function(ginger, pest_repellent).
function(turmeric, pest_repellent).
function(galangal, pest_repellent).
function(kencur, pest_repellent).
function(temulawak, pest_repellent).

% Aggressive / invasive
function(johnson_grass, invasive).
