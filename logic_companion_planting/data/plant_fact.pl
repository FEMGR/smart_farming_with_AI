% FILE: logic_companion_planting/data/plant_fact.pl
%
% PURPOSE:
% This file serves as the central registry for all plant entities within the Smart Farming System's
% companion planting logic. It declares individual plant names using the `plant/1` predicate.
%
% It also defines aliases for certain plants using the `alias/2` predicate and
% ecological traits using the `trait/2` predicate.
%
% PREDICATES:
% - plant(PlantName): Declares a unique plant by its atom name.
% - alias(AliasName, CanonicalName): Defines an alternative name for a plant.
% - trait(PlantName, Trait): Associates an ecological trait (e.g., pest_repellent, nitrogen_fixer) with a plant.
%
% RELATED MODULES:
% - `category_fact.pl`: Defines categories and assigns plants to them using `belongs_to/2`.
% - `insect_fact.pl`: References plant names for pest-plant interactions.
% - `disease_fact.pl`: References plant names for disease-host relationships.
% - `companion_fact.pl`: Uses plant names to define beneficial and antagonistic relationships.
%
% USAGE:
% This file is consulted by other Prolog modules to retrieve a comprehensive list of plants,
% their aliases, and their inherent ecological traits. It ensures a consistent and
% canonical representation of plant entities across the system.

% =========================================================
% PLANT REGISTRY
% =========================================================

plant(bean_bush).
plant(bean_pole).
plant(pea).
plant(pea_english).
plant(peanut).

plant(tomato).
plant(melons).
plant(watermelon).
plant(squash).
plant(gourd).

plant(carrot).
plant(beets).
plant(radish).
plant(turnip).
plant(sweet_potato).
plant(taro).
plant(horseradish).
plant(potato).

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

plant(onion).
plant(chives).
plant(garlic).
plant(green_onion).
plant(leek).
plant(shallot).

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

plant(broccoli).
plant(brussels_sprout).
plant(cauliflower).
plant(kohlrabi).
plant(mustard).

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

plant(amaranth).
plant(corn).
plant(rice).
plant(barley).
plant(wheat).
plant(spelt).
plant(sorghum).
plant(sugarcane).

plant(ginger).
plant(turmeric).
plant(galangal).
plant(lesser_galangal).
plant(fingerroot).
plant(temulawak).
plant(temu_ireng).
plant(temu_kunci).
plant(temu_mangga).
plant(kencur).

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

plant(grapes).
plant(apple).
plant(pear).

plant(strawberries).
plant(blackberries).
plant(blueberries).
plant(raspberries).

plant(cinnamon).
plant(nutmeg).
plant(black_pepper).
plant(white_pepper).
plant(juniper).

plant(privet).
plant(lilac).
plant(viburnum).
plant(prunus).
plant(phlox).
plant(cotoneaster).
plant(buxus).
plant(rhododendron).
plant(yew).
plant(cyclamen).

plant(johnson_grass).


% =========================================================
% ALIASES
% =========================================================

alias(lengkuas, galangal).


% =========================================================
% ECOLOGICAL TRAITS
% =========================================================

trait(lemongrass, pest_repellent).
trait(catnip, pest_repellent).
trait(rue, pest_repellent).
trait(tansy, pest_repellent).
trait(chives, pest_repellent).
trait(garlic, pest_repellent).

trait(nasturtium, pest_trap).

trait(borage, pollinator_attractor).
trait(clover, pollinator_attractor).
trait(yarrow, pollinator_attractor).

trait(comfrey, nutrient_accumulator).

trait(bean_bush, nitrogen_fixer).
trait(bean_pole, nitrogen_fixer).
trait(pea, nitrogen_fixer).
trait(peanut, nitrogen_fixer).

trait(sweet_potato, ground_cover).
trait(squash, ground_cover).

trait(ginger, pest_repellent).
trait(turmeric, pest_repellent).
trait(galangal, pest_repellent).
trait(kencur, pest_repellent).
trait(temulawak, pest_repellent).

trait(johnson_grass, invasive).