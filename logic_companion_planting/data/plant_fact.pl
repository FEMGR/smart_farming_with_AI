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
plant(melon).
plant(watermelon).
plant(squash).
plant(gourd).
plant(carrot).
plant(beet).
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
plant(mustard_green).
plant(swiss_chard).
plant(water_spinach).
plant(purslane).
plant(onion).
plant(chive).
plant(garlic).
plant(green_onion).
plant(leek).
plant(shallot).
plant(celery).
plant(asparagus).
plant(artichoke).
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
plant(grape).
plant(apple).
plant(pear).
plant(strawberry).
plant(blackberry).
plant(blueberry).
plant(raspberry).
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
plant(rye).
plant(hydrangea).


% =========================================================
% SCIENTIFIC NAME MAPPINGS
% Sources: USDA Plants Database, Kew Gardens (POWO)
% =========================================================
% =========================================================
% SCIENTIFIC NAME MAPPINGS (Lowercase)
% =========================================================

% Legumes
scientific_name(bean_bush, 'phaseolus vulgaris').
scientific_name(bean_pole, 'phaseolus vulgaris').
scientific_name(pea, 'pisum sativum').
scientific_name(pea_english, 'pisum sativum var. sativum').
scientific_name(peanut, 'arachis hypogaea').

% Fruits & Gourds
scientific_name(tomato, 'solanum lycopersicum').
scientific_name(melons, 'cucumis melo').
scientific_name(watermelon, 'citrullus lanatus').
scientific_name(squash, 'cucurbita spp.').
scientific_name(gourd, 'lagenaria siceraria').

% Roots & Tubers
scientific_name(carrot, 'daucus carota').
scientific_name(beets, 'beta vulgaris').
scientific_name(radish, 'raphanus sativus').
scientific_name(turnip, 'brassica rapa subsp. rapa').
scientific_name(sweet_potato, 'ipomoea batatas').
scientific_name(taro, 'colocasia esculenta').
scientific_name(horseradish, 'armoracia rusticana').
scientific_name(potato, 'solanum tuberosum').

% Leafy Greens & Brassicas
scientific_name(lettuce, 'lactuca sativa').
scientific_name(spinach, 'spinacia oleracea').
scientific_name(cabbage, 'brassica oleracea var. capitata').
scientific_name(kale, 'brassica oleracea var. sabellica').
scientific_name(arugula, 'eruca vesicaria').
scientific_name(bok_choy, 'brassica rapa subsp. chinensis').
scientific_name(choy_sum, 'brassica rapa subsp. parachinensis').
scientific_name(mustard_green, 'brassica juncea').
scientific_name(swiss_chard, 'beta vulgaris subsp. vulgaris').
scientific_name(water_spinach, 'ipomoea aquatica').
scientific_name(purslane, 'portulaca oleracea').

% Alliums
scientific_name(onion, 'allium cepa').
scientific_name(chive, 'allium schoenoprasum').
scientific_name(garlic, 'allium sativum').
scientific_name(green_onion, 'allium fistulosum').
scientific_name(leek, 'allium ampeloprasum').
scientific_name(shallot, 'allium cepa var. aggregatum').

% Stem & Other Vegetables
scientific_name(celery, 'apium graveolens').
scientific_name(asparagus, 'asparagus officinalis').
scientific_name(artichoke, 'cynara scolymus').
scientific_name(zucchini, 'cucurbita pepo').
scientific_name(eggplant, 'solanum melongena').
scientific_name(cucumber, 'cucumis sativus').
scientific_name(pumpkin, 'cucurbita pepo').
scientific_name(bell_pepper, 'capsicum annuum').
scientific_name(chili_pepper, 'capsicum annuum').
scientific_name(okra, 'abelmoschus esculentus').
scientific_name(sweet_corn, 'zea mays var. saccharata').

% Brassica Crops
scientific_name(broccoli, 'brassica oleracea var. italica').
scientific_name(brussels_sprout, 'brassica oleracea var. gemmifera').
scientific_name(cauliflower, 'brassica oleracea var. botrytis').
scientific_name(kohlrabi, 'brassica oleracea var. gongylodes').
scientific_name(mustard, 'sinapis alba').

% Culinary Herbs
scientific_name(basil, 'ocimum basilicum').
scientific_name(parsley, 'petroselinum crispum').
scientific_name(rosemary, 'salvia rosmarinus').
scientific_name(thyme, 'thymus vulgaris').
scientific_name(oregano, 'origanum vulgare').
scientific_name(mint, 'mentha spp.').
scientific_name(sage, 'salvia officinalis').
scientific_name(cilantro, 'coriandrum sativum').
scientific_name(dill, 'anethum graveolens').
scientific_name(fennel, 'foeniculum vulgare').
scientific_name(tarragon, 'artemisia dracunculus').
scientific_name(lavender, 'lavandula spp.').
scientific_name(lemon_balm, 'melissa officinalis').
scientific_name(chamomile, 'matricaria chamomilla').
scientific_name(comfrey, 'symphytum officinale').
scientific_name(rue, 'ruta graveolens').
scientific_name(summer_savory, 'satureja hortensis').
scientific_name(hyssop, 'hyssopus officinalis').
scientific_name(borage, 'borago officinalis').
scientific_name(caraway, 'carum carvi').
scientific_name(catnip, 'nepeta cataria').
scientific_name(lemongrass, 'cymbopogon spp.').
scientific_name(tansy, 'tanacetum vulgare').

% Grains & Grasses
scientific_name(amaranth, 'amaranthus spp.').
scientific_name(corn, 'zea mays').
scientific_name(rice, 'oryza sativa').
scientific_name(barley, 'hordeum vulgare').
scientific_name(wheat, 'triticum aestivum').
scientific_name(spelt, 'triticum spelta').
scientific_name(sorghum, 'sorghum bicolor').
scientific_name(sugarcane, 'saccharum officinarum').
scientific_name(johnson_grass, 'sorghum halepense').
scientific_name(rye, 'secale cereale').

% Zingiberales (Gingers)
scientific_name(ginger, 'zingiber officinale').
scientific_name(turmeric, 'curcuma longa').
scientific_name(galangal, 'alpinia galanga').
scientific_name(lesser_galangal, 'alpinia officinarum').
scientific_name(fingerroot, 'boesenbergia rotunda').
scientific_name(temulawak, 'curcuma zanthorrhiza').
scientific_name(temu_ireng, 'curcuma aeruginosa').
scientific_name(temu_kunci, 'boesenbergia rotunda').
scientific_name(temu_mangga, 'curcuma mangga').
scientific_name(kencur, 'kaempferia galanga').

% Flowers & Ornamentals
scientific_name(calendula, 'calendula officinalis').
scientific_name(viola, 'viola spp.').
scientific_name(rose, 'rosa spp.').
scientific_name(hibiscus, 'hibiscus rosa-sinensis').
scientific_name(jasmine, 'jasminum spp.').
scientific_name(chrysanthemum, 'chrysanthemum spp.').
scientific_name(cornflower, 'centaurea cyanus').
scientific_name(dandelion, 'taraxacum officinale').
scientific_name(elderflower, 'sambucus nigra').
scientific_name(bee_balm, 'monarda spp.').
scientific_name(yarrow, 'achillea millefolium').
scientific_name(clover, 'trifolium spp.').
scientific_name(sunflower, 'helianthus annuus').
scientific_name(gladiolus, 'gladiolus spp.').
scientific_name(nasturtium, 'tropaeolum majus').
scientific_name(pyrethrum, 'tanacetum cinerariifolium').
scientific_name(tulip, 'tulipa spp.').
scientific_name(dahlia, 'dahlia spp.').
scientific_name(hydrangea, 'hydrangea spp.').

% Fruits & Berries
scientific_name(grapes, 'vitis vinifera').
scientific_name(apple, 'malus domestica').
scientific_name(pear, 'pyrus communis').
scientific_name(strawberry, 'fragaria x ananassa').
scientific_name(blackberry, 'rubus subg. rubus').
scientific_name(blueberry, 'vaccinium corymbosum').
scientific_name(raspberry, 'rubus idaeus').

% Spices & Woody Plants
scientific_name(cinnamon, 'cinnamomum verum').
scientific_name(nutmeg, 'myristica fragrans').
scientific_name(black_pepper, 'piper nigrum').
scientific_name(white_pepper, 'piper nigrum').
scientific_name(juniper, 'juniperus communis').
scientific_name(privet, 'ligustrum spp.').
scientific_name(lilac, 'syringa spp.').
scientific_name(viburnum, 'viburnum spp.').
scientific_name(prunus, 'prunus spp.').
scientific_name(phlox, 'phlox spp.').
scientific_name(cotoneaster, 'cotoneaster spp.').
scientific_name(buxus, 'buxus spp.').
scientific_name(rhododendron, 'rhododendron spp.').
scientific_name(yew, 'taxus spp.').
scientific_name(cyclamen, 'cyclamen spp.').




% =========================================================
% ECOLOGICAL TRAITS
% =========================================================

trait(lemongrass, pest_repellent).
trait(catnip, pest_repellent).
trait(rue, pest_repellent).
trait(tansy, pest_repellent).
trait(chive, pest_repellent).
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