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

% =========================================================
% PLANT FACTS BY PLANT
% Auto-organized by plant_data_bank_scripts/scripts/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% AMARANTH
% ---------------------------------------------------------

% =========================================================
% PLANT FACTS BY PLANT
% Auto-organized by plant_data_bank_scripts/scripts/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% AMARANTH
% ---------------------------------------------------------
plant(amaranth).
scientific_name(amaranth, 'amaranthus spp.').

% ---------------------------------------------------------
% APPLE
% ---------------------------------------------------------
plant(apple).
scientific_name(apple, 'malus domestica').

% ---------------------------------------------------------
% ARTICHOKE
% ---------------------------------------------------------
plant(artichoke).
scientific_name(artichoke, 'cynara scolymus').

% ---------------------------------------------------------
% ARUGULA
% ---------------------------------------------------------
plant(arugula).
scientific_name(arugula, 'eruca vesicaria').

% ---------------------------------------------------------
% ASPARAGUS
% ---------------------------------------------------------
plant(asparagus).
scientific_name(asparagus, 'asparagus officinalis').

% ---------------------------------------------------------
% BARLEY
% ---------------------------------------------------------
plant(barley).
scientific_name(barley, 'hordeum vulgare').

% ---------------------------------------------------------
% BASIL
% ---------------------------------------------------------
plant(basil).
scientific_name(basil, 'ocimum basilicum').

% ---------------------------------------------------------
% BEAN BUSH
% ---------------------------------------------------------
plant(bean_bush).
scientific_name(bean_bush, 'phaseolus vulgaris').
trait(bean_bush, nitrogen_fixer).

% ---------------------------------------------------------
% BEAN POLE
% ---------------------------------------------------------
plant(bean_pole).
scientific_name(bean_pole, 'phaseolus vulgaris').
trait(bean_pole, nitrogen_fixer).

% ---------------------------------------------------------
% BEE BALM
% ---------------------------------------------------------
plant(bee_balm).
scientific_name(bee_balm, 'monarda spp.').

% ---------------------------------------------------------
% BEET
% ---------------------------------------------------------
plant(beet).

% ---------------------------------------------------------
% BEETS
% ---------------------------------------------------------
scientific_name(beets, 'beta vulgaris').

% ---------------------------------------------------------
% BELL PEPPER
% ---------------------------------------------------------
plant(bell_pepper).
scientific_name(bell_pepper, 'capsicum annuum').

% ---------------------------------------------------------
% BLACK PEPPER
% ---------------------------------------------------------
plant(black_pepper).
scientific_name(black_pepper, 'piper nigrum').

% ---------------------------------------------------------
% BLACKBERRY
% ---------------------------------------------------------
plant(blackberry).
scientific_name(blackberry, 'rubus subg. rubus').

% ---------------------------------------------------------
% BLUEBERRY
% ---------------------------------------------------------
plant(blueberry).
scientific_name(blueberry, 'vaccinium corymbosum').

% ---------------------------------------------------------
% BOK CHOY
% ---------------------------------------------------------
plant(bok_choy).
scientific_name(bok_choy, 'brassica rapa subsp. chinensis').

% ---------------------------------------------------------
% BORAGE
% ---------------------------------------------------------
plant(borage).
scientific_name(borage, 'borago officinalis').
trait(borage, pollinator_attractor).

% ---------------------------------------------------------
% BROCCOLI
% ---------------------------------------------------------
plant(broccoli).
scientific_name(broccoli, 'brassica oleracea var. italica').

% ---------------------------------------------------------
% BRUSSELS SPROUT
% ---------------------------------------------------------
plant(brussels_sprout).
scientific_name(brussels_sprout, 'brassica oleracea var. gemmifera').

% ---------------------------------------------------------
% BUXUS
% ---------------------------------------------------------
plant(buxus).
scientific_name(buxus, 'buxus spp.').

% ---------------------------------------------------------
% CABBAGE
% ---------------------------------------------------------
plant(cabbage).
scientific_name(cabbage, 'brassica oleracea var. capitata').

% ---------------------------------------------------------
% CALENDULA
% ---------------------------------------------------------
plant(calendula).
scientific_name(calendula, 'calendula officinalis').

% ---------------------------------------------------------
% CARAWAY
% ---------------------------------------------------------
plant(caraway).
scientific_name(caraway, 'carum carvi').

% ---------------------------------------------------------
% CARROT
% ---------------------------------------------------------
plant(carrot).
scientific_name(carrot, 'daucus carota').

% ---------------------------------------------------------
% CATNIP
% ---------------------------------------------------------
plant(catnip).
scientific_name(catnip, 'nepeta cataria').
trait(catnip, pest_repellent).

% ---------------------------------------------------------
% CAULIFLOWER
% ---------------------------------------------------------
plant(cauliflower).
scientific_name(cauliflower, 'brassica oleracea var. botrytis').

% ---------------------------------------------------------
% CELERY
% ---------------------------------------------------------
plant(celery).
scientific_name(celery, 'apium graveolens').

% ---------------------------------------------------------
% CHAMOMILE
% ---------------------------------------------------------
plant(chamomile).
scientific_name(chamomile, 'matricaria chamomilla').

% ---------------------------------------------------------
% CHILI PEPPER
% ---------------------------------------------------------
plant(chili_pepper).
scientific_name(chili_pepper, 'capsicum annuum').

% ---------------------------------------------------------
% CHIVE
% ---------------------------------------------------------
plant(chive).
scientific_name(chive, 'allium schoenoprasum').
trait(chive, pest_repellent).

% ---------------------------------------------------------
% CHOY SUM
% ---------------------------------------------------------
plant(choy_sum).
scientific_name(choy_sum, 'brassica rapa subsp. parachinensis').

% ---------------------------------------------------------
% CHRYSANTHEMUM
% ---------------------------------------------------------
plant(chrysanthemum).
scientific_name(chrysanthemum, 'chrysanthemum spp.').

% ---------------------------------------------------------
% CILANTRO
% ---------------------------------------------------------
plant(cilantro).
scientific_name(cilantro, 'coriandrum sativum').

% ---------------------------------------------------------
% CINNAMON
% ---------------------------------------------------------
plant(cinnamon).
scientific_name(cinnamon, 'cinnamomum verum').

% ---------------------------------------------------------
% CLOVER
% ---------------------------------------------------------
plant(clover).
scientific_name(clover, 'trifolium spp.').
trait(clover, pollinator_attractor).

% ---------------------------------------------------------
% COMFREY
% ---------------------------------------------------------
plant(comfrey).
scientific_name(comfrey, 'symphytum officinale').
trait(comfrey, nutrient_accumulator).

% ---------------------------------------------------------
% CORN
% ---------------------------------------------------------
plant(corn).
scientific_name(corn, 'zea mays').

% ---------------------------------------------------------
% CORNFLOWER
% ---------------------------------------------------------
plant(cornflower).
scientific_name(cornflower, 'centaurea cyanus').

% ---------------------------------------------------------
% COTONEASTER
% ---------------------------------------------------------
plant(cotoneaster).
scientific_name(cotoneaster, 'cotoneaster spp.').

% ---------------------------------------------------------
% CUCUMBER
% ---------------------------------------------------------
plant(cucumber).
scientific_name(cucumber, 'cucumis sativus').

% ---------------------------------------------------------
% CYCLAMEN
% ---------------------------------------------------------
plant(cyclamen).
scientific_name(cyclamen, 'cyclamen spp.').

% ---------------------------------------------------------
% DAHLIA
% ---------------------------------------------------------
plant(dahlia).
scientific_name(dahlia, 'dahlia spp.').

% ---------------------------------------------------------
% DANDELION
% ---------------------------------------------------------
plant(dandelion).
scientific_name(dandelion, 'taraxacum officinale').

% ---------------------------------------------------------
% DILL
% ---------------------------------------------------------
plant(dill).
scientific_name(dill, 'anethum graveolens').

% ---------------------------------------------------------
% EGGPLANT
% ---------------------------------------------------------
plant(eggplant).
scientific_name(eggplant, 'solanum melongena').

% ---------------------------------------------------------
% ELDERFLOWER
% ---------------------------------------------------------
plant(elderflower).
scientific_name(elderflower, 'sambucus nigra').

% ---------------------------------------------------------
% FENNEL
% ---------------------------------------------------------
plant(fennel).
scientific_name(fennel, 'foeniculum vulgare').

% ---------------------------------------------------------
% FINGERROOT
% ---------------------------------------------------------
plant(fingerroot).
scientific_name(fingerroot, 'boesenbergia rotunda').

% ---------------------------------------------------------
% GALANGAL
% ---------------------------------------------------------
plant(galangal).
scientific_name(galangal, 'alpinia galanga').
trait(galangal, pest_repellent).

% ---------------------------------------------------------
% GARLIC
% ---------------------------------------------------------
plant(garlic).
scientific_name(garlic, 'allium sativum').
trait(garlic, pest_repellent).

% ---------------------------------------------------------
% GINGER
% ---------------------------------------------------------
plant(ginger).
scientific_name(ginger, 'zingiber officinale').
trait(ginger, pest_repellent).

% ---------------------------------------------------------
% GLADIOLUS
% ---------------------------------------------------------
plant(gladiolus).
scientific_name(gladiolus, 'gladiolus spp.').

% ---------------------------------------------------------
% GOTU KOLA
% ---------------------------------------------------------
plant(gotu_kola).
scientific_name(gotu_kola, 'centella asiatica').
edible(gotu_kola, true).
edible_part(gotu_kola, leaf).
use_category(gotu_kola, medicinal_plant).
trait(gotu_kola, medicinal).
trait(gotu_kola, pollinator_attractor).

% ---------------------------------------------------------
% GOURD
% ---------------------------------------------------------
plant(gourd).
scientific_name(gourd, 'lagenaria siceraria').

% ---------------------------------------------------------
% GRAPE
% ---------------------------------------------------------
plant(grape).

% ---------------------------------------------------------
% GRAPES
% ---------------------------------------------------------
scientific_name(grapes, 'vitis vinifera').

% ---------------------------------------------------------
% GREEN ONION
% ---------------------------------------------------------
plant(green_onion).
scientific_name(green_onion, 'allium fistulosum').

% ---------------------------------------------------------
% HIBISCUS
% ---------------------------------------------------------
plant(hibiscus).
scientific_name(hibiscus, 'hibiscus rosa-sinensis').

% ---------------------------------------------------------
% HORSERADISH
% ---------------------------------------------------------
plant(horseradish).
scientific_name(horseradish, 'armoracia rusticana').

% ---------------------------------------------------------
% HYDRANGEA
% ---------------------------------------------------------
plant(hydrangea).
scientific_name(hydrangea, 'hydrangea spp.').

% ---------------------------------------------------------
% HYSSOP
% ---------------------------------------------------------
plant(hyssop).
scientific_name(hyssop, 'hyssopus officinalis').

% ---------------------------------------------------------
% JASMINE
% ---------------------------------------------------------
plant(jasmine).
scientific_name(jasmine, 'jasminum spp.').

% ---------------------------------------------------------
% JOHNSON GRASS
% ---------------------------------------------------------
plant(johnson_grass).
scientific_name(johnson_grass, 'sorghum halepense').
trait(johnson_grass, invasive).

% ---------------------------------------------------------
% JUNIPER
% ---------------------------------------------------------
plant(juniper).
scientific_name(juniper, 'juniperus communis').

% ---------------------------------------------------------
% KALE
% ---------------------------------------------------------
plant(kale).
scientific_name(kale, 'brassica oleracea var. sabellica').

% ---------------------------------------------------------
% KENCUR
% ---------------------------------------------------------
plant(kencur).
scientific_name(kencur, 'kaempferia galanga').
trait(kencur, pest_repellent).

% ---------------------------------------------------------
% KOHLRABI
% ---------------------------------------------------------
plant(kohlrabi).
scientific_name(kohlrabi, 'brassica oleracea var. gongylodes').

% ---------------------------------------------------------
% LAVENDER
% ---------------------------------------------------------
plant(lavender).
scientific_name(lavender, 'lavandula spp.').

% ---------------------------------------------------------
% LEEK
% ---------------------------------------------------------
plant(leek).
scientific_name(leek, 'allium ampeloprasum').

% ---------------------------------------------------------
% LEMON BALM
% ---------------------------------------------------------
plant(lemon_balm).
scientific_name(lemon_balm, 'melissa officinalis').

% ---------------------------------------------------------
% LEMONGRASS
% ---------------------------------------------------------
plant(lemongrass).
scientific_name(lemongrass, 'cymbopogon spp.').
trait(lemongrass, pest_repellent).

% ---------------------------------------------------------
% LESSER GALANGAL
% ---------------------------------------------------------
plant(lesser_galangal).
scientific_name(lesser_galangal, 'alpinia officinarum').

% ---------------------------------------------------------
% LETTUCE
% ---------------------------------------------------------
plant(lettuce).
scientific_name(lettuce, 'lactuca sativa').

% ---------------------------------------------------------
% LILAC
% ---------------------------------------------------------
plant(lilac).
scientific_name(lilac, 'syringa spp.').

% ---------------------------------------------------------
% MELON
% ---------------------------------------------------------
plant(melon).

% ---------------------------------------------------------
% MELONS
% ---------------------------------------------------------
scientific_name(melons, 'cucumis melo').

% ---------------------------------------------------------
% MINT
% ---------------------------------------------------------
plant(mint).
scientific_name(mint, 'mentha spp.').

% ---------------------------------------------------------
% MUSTARD
% ---------------------------------------------------------
plant(mustard).
scientific_name(mustard, 'sinapis alba').

% ---------------------------------------------------------
% MUSTARD GREEN
% ---------------------------------------------------------
plant(mustard_green).
scientific_name(mustard_green, 'brassica juncea').

% ---------------------------------------------------------
% NASTURTIUM
% ---------------------------------------------------------
plant(nasturtium).
scientific_name(nasturtium, 'tropaeolum majus').
trait(nasturtium, pest_trap).

% ---------------------------------------------------------
% NUTMEG
% ---------------------------------------------------------
plant(nutmeg).
scientific_name(nutmeg, 'myristica fragrans').

% ---------------------------------------------------------
% OKRA
% ---------------------------------------------------------
plant(okra).
scientific_name(okra, 'abelmoschus esculentus').

% ---------------------------------------------------------
% ONION
% ---------------------------------------------------------
plant(onion).
scientific_name(onion, 'allium cepa').

% ---------------------------------------------------------
% OREGANO
% ---------------------------------------------------------
plant(oregano).
scientific_name(oregano, 'origanum vulgare').

% ---------------------------------------------------------
% PARSLEY
% ---------------------------------------------------------
plant(parsley).
scientific_name(parsley, 'petroselinum crispum').

% ---------------------------------------------------------
% PEA
% ---------------------------------------------------------
plant(pea).
scientific_name(pea, 'pisum sativum').
trait(pea, nitrogen_fixer).

% ---------------------------------------------------------
% PEA ENGLISH
% ---------------------------------------------------------
plant(pea_english).
scientific_name(pea_english, 'pisum sativum var. sativum').

% ---------------------------------------------------------
% PEANUT
% ---------------------------------------------------------
plant(peanut).
scientific_name(peanut, 'arachis hypogaea').
trait(peanut, nitrogen_fixer).

% ---------------------------------------------------------
% PEAR
% ---------------------------------------------------------
plant(pear).
scientific_name(pear, 'pyrus communis').

% ---------------------------------------------------------
% PHLOX
% ---------------------------------------------------------
plant(phlox).
scientific_name(phlox, 'phlox spp.').

% ---------------------------------------------------------
% POTATO
% ---------------------------------------------------------
plant(potato).
scientific_name(potato, 'solanum tuberosum').

% ---------------------------------------------------------
% PRIVET
% ---------------------------------------------------------
plant(privet).
scientific_name(privet, 'ligustrum spp.').

% ---------------------------------------------------------
% PRUNUS
% ---------------------------------------------------------
plant(prunus).
scientific_name(prunus, 'prunus spp.').

% ---------------------------------------------------------
% PUMPKIN
% ---------------------------------------------------------
plant(pumpkin).
scientific_name(pumpkin, 'cucurbita pepo').

% ---------------------------------------------------------
% PURSLANE
% ---------------------------------------------------------
plant(purslane).
scientific_name(purslane, 'portulaca oleracea').

% ---------------------------------------------------------
% PYRETHRUM
% ---------------------------------------------------------
plant(pyrethrum).
scientific_name(pyrethrum, 'tanacetum cinerariifolium').

% ---------------------------------------------------------
% RADISH
% ---------------------------------------------------------
plant(radish).
scientific_name(radish, 'raphanus sativus').

% ---------------------------------------------------------
% RASPBERRY
% ---------------------------------------------------------
plant(raspberry).
scientific_name(raspberry, 'rubus idaeus').

% ---------------------------------------------------------
% RHODODENDRON
% ---------------------------------------------------------
plant(rhododendron).
scientific_name(rhododendron, 'rhododendron spp.').

% ---------------------------------------------------------
% RICE
% ---------------------------------------------------------
plant(rice).
scientific_name(rice, 'oryza sativa').

% ---------------------------------------------------------
% ROSE
% ---------------------------------------------------------
plant(rose).
scientific_name(rose, 'rosa spp.').

% ---------------------------------------------------------
% ROSEMARY
% ---------------------------------------------------------
plant(rosemary).
scientific_name(rosemary, 'salvia rosmarinus').

% ---------------------------------------------------------
% RUE
% ---------------------------------------------------------
plant(rue).
scientific_name(rue, 'ruta graveolens').
trait(rue, pest_repellent).

% ---------------------------------------------------------
% RYE
% ---------------------------------------------------------
plant(rye).
scientific_name(rye, 'secale cereale').

% ---------------------------------------------------------
% SAGE
% ---------------------------------------------------------
plant(sage).
scientific_name(sage, 'salvia officinalis').

% ---------------------------------------------------------
% SHALLOT
% ---------------------------------------------------------
plant(shallot).
scientific_name(shallot, 'allium cepa var. aggregatum').

% ---------------------------------------------------------
% SORGHUM
% ---------------------------------------------------------
plant(sorghum).
scientific_name(sorghum, 'sorghum bicolor').

% ---------------------------------------------------------
% SPELT
% ---------------------------------------------------------
plant(spelt).
scientific_name(spelt, 'triticum spelta').

% ---------------------------------------------------------
% SPINACH
% ---------------------------------------------------------
plant(spinach).
scientific_name(spinach, 'spinacia oleracea').

% ---------------------------------------------------------
% SQUASH
% ---------------------------------------------------------
plant(squash).
scientific_name(squash, 'cucurbita spp.').
trait(squash, ground_cover).

% ---------------------------------------------------------
% STRAWBERRY
% ---------------------------------------------------------
plant(strawberry).
scientific_name(strawberry, 'fragaria ananassa').

% ---------------------------------------------------------
% SUGARCANE
% ---------------------------------------------------------
plant(sugarcane).
scientific_name(sugarcane, 'saccharum officinarum').

% ---------------------------------------------------------
% SUMMER SAVORY
% ---------------------------------------------------------
plant(summer_savory).
scientific_name(summer_savory, 'satureja hortensis').

% ---------------------------------------------------------
% SUNFLOWER
% ---------------------------------------------------------
plant(sunflower).
scientific_name(sunflower, 'helianthus annuus').

% ---------------------------------------------------------
% SWEET CORN
% ---------------------------------------------------------
plant(sweet_corn).
scientific_name(sweet_corn, 'zea mays var. saccharata').

% ---------------------------------------------------------
% SWEET POTATO
% ---------------------------------------------------------
plant(sweet_potato).
scientific_name(sweet_potato, 'ipomoea batatas').
trait(sweet_potato, ground_cover).

% ---------------------------------------------------------
% SWISS CHARD
% ---------------------------------------------------------
plant(swiss_chard).
scientific_name(swiss_chard, 'beta vulgaris subsp. vulgaris').

% ---------------------------------------------------------
% TANSY
% ---------------------------------------------------------
plant(tansy).
scientific_name(tansy, 'tanacetum vulgare').
trait(tansy, pest_repellent).

% ---------------------------------------------------------
% TARO
% ---------------------------------------------------------
plant(taro).
scientific_name(taro, 'colocasia esculenta').

% ---------------------------------------------------------
% TARRAGON
% ---------------------------------------------------------
plant(tarragon).
scientific_name(tarragon, 'artemisia dracunculus').

% ---------------------------------------------------------
% TEMU IRENG
% ---------------------------------------------------------
plant(temu_ireng).
scientific_name(temu_ireng, 'curcuma aeruginosa').

% ---------------------------------------------------------
% TEMU KUNCI
% ---------------------------------------------------------
plant(temu_kunci).
scientific_name(temu_kunci, 'boesenbergia rotunda').

% ---------------------------------------------------------
% TEMU MANGGA
% ---------------------------------------------------------
plant(temu_mangga).
scientific_name(temu_mangga, 'curcuma mangga').

% ---------------------------------------------------------
% TEMULAWAK
% ---------------------------------------------------------
plant(temulawak).
scientific_name(temulawak, 'curcuma zanthorrhiza').
trait(temulawak, pest_repellent).

% ---------------------------------------------------------
% THYME
% ---------------------------------------------------------
plant(thyme).
scientific_name(thyme, 'thymus vulgaris').

% ---------------------------------------------------------
% TOMATO
% ---------------------------------------------------------
plant(tomato).
scientific_name(tomato, 'lycopersicon esculentum').
scientific_name(tomato, 'solanum lycopersicum').

% ---------------------------------------------------------
% TULIP
% ---------------------------------------------------------
plant(tulip).
scientific_name(tulip, 'tulipa spp.').

% ---------------------------------------------------------
% TURMERIC
% ---------------------------------------------------------
plant(turmeric).
scientific_name(turmeric, 'curcuma longa').
trait(turmeric, pest_repellent).

% ---------------------------------------------------------
% TURNIP
% ---------------------------------------------------------
plant(turnip).
scientific_name(turnip, 'brassica rapa subsp. rapa').

% ---------------------------------------------------------
% VIBURNUM
% ---------------------------------------------------------
plant(viburnum).
scientific_name(viburnum, 'viburnum spp.').

% ---------------------------------------------------------
% VIOLA
% ---------------------------------------------------------
plant(viola).
scientific_name(viola, 'viola spp.').

% ---------------------------------------------------------
% WATER SPINACH
% ---------------------------------------------------------
plant(water_spinach).
scientific_name(water_spinach, 'ipomoea aquatica').

% ---------------------------------------------------------
% WATERMELON
% ---------------------------------------------------------
plant(watermelon).
scientific_name(watermelon, 'citrullus lanatus').

% ---------------------------------------------------------
% WHEAT
% ---------------------------------------------------------
plant(wheat).
scientific_name(wheat, 'triticum aestivum').

% ---------------------------------------------------------
% WHITE PEPPER
% ---------------------------------------------------------
plant(white_pepper).
scientific_name(white_pepper, 'piper nigrum').

% ---------------------------------------------------------
% YARROW
% ---------------------------------------------------------
plant(yarrow).
scientific_name(yarrow, 'achillea millefolium').
trait(yarrow, pollinator_attractor).

% ---------------------------------------------------------
% YEW
% ---------------------------------------------------------
plant(yew).
scientific_name(yew, 'taxus spp.').

% ---------------------------------------------------------
% ZUCCHINI
% ---------------------------------------------------------
plant(zucchini).
scientific_name(zucchini, 'cucurbita pepo').


% =========================================================
% AUTO-GENERATED FROM NORMALIZED PLANT PROFILES: plant_fact
% Review before editing manually.
% =========================================================

plant(aloe_vera).
scientific_name(aloe_vera, 'aloe vera').
edible(aloe_vera, true).
edible_part(aloe_vera, leaf).
edible_part(aloe_vera, seed).
use_category(aloe_vera, medicinal_plant).
trait(aloe_vera, medicinal).
trait(aloe_vera, pollinator_attractor).
trait(aloe_vera, pest_confuser).
edible(apple, true).
edible_part(apple, fruit).
edible_part(apple, oil).
use_category(apple, fruit_crop).
use_category(apple, medicinal_plant).
trait(apple, medicinal).
use_category(apple, oil_crop).
trait(apple, pollinator_attractor).
trait(apple, pest_confuser).
scientific_name(artichoke, 'cynara cardunculus').
edible(artichoke, true).
edible_part(artichoke, flower).
edible_part(artichoke, leaf).
edible_part(artichoke, root).
edible_part(artichoke, stem).
use_category(artichoke, medicinal_plant).
trait(artichoke, medicinal).
use_category(artichoke, root_tuber_crop).
trait(artichoke, pollinator_attractor).
trait(artichoke, pest_confuser).
edible(arugula, true).
edible_part(arugula, flower).
edible_part(arugula, leaf).
edible_part(arugula, seed).
use_category(arugula, medicinal_plant).
trait(arugula, medicinal).
trait(arugula, pollinator_attractor).
edible(basil, true).
edible_part(basil, leaf).
edible_part(basil, seed).
use_category(basil, beverage_plant).
use_category(basil, companion_plant).
trait(basil, companion_plant).
use_category(basil, culinary_herb).
trait(basil, culinary_herb).
use_category(basil, medicinal_plant).
trait(basil, medicinal).
use_category(basil, repellent_plant).
trait(basil, pest_repellent).
trait(basil, pollinator_attractor).
trait(basil, pest_confuser).
plant(bean_common).
scientific_name(bean_common, 'phaseolus vulgaris').
edible(bean_common, true).
edible_part(bean_common, leaf).
edible_part(bean_common, seed).
use_category(bean_common, culinary_herb).
trait(bean_common, culinary_herb).
use_category(bean_common, medicinal_plant).
trait(bean_common, medicinal).
trait(bean_common, pollinator_attractor).
plant(bitter_melon).
scientific_name(bitter_melon, 'momordica charantia').
scientific_name(blackberry, 'rubus fruticosus').
edible(blackberry, true).
edible_part(blackberry, fruit).
edible_part(blackberry, leaf).
edible_part(blackberry, root).
edible_part(blackberry, stem).
use_category(blackberry, beverage_plant).
use_category(blackberry, fruit_crop).
use_category(blackberry, medicinal_plant).
trait(blackberry, medicinal).
use_category(blackberry, root_tuber_crop).
trait(blackberry, pollinator_attractor).
trait(blackberry, pest_confuser).
scientific_name(cabbage, 'brassica oleracea').
edible(cabbage, true).
edible_part(cabbage, leaf).
use_category(cabbage, medicinal_plant).
trait(cabbage, medicinal).
trait(cabbage, pollinator_attractor).
edible(carrot, true).
edible_part(carrot, flower).
edible_part(carrot, root).
use_category(carrot, culinary_herb).
trait(carrot, culinary_herb).
use_category(carrot, medicinal_plant).
trait(carrot, medicinal).
use_category(carrot, root_tuber_crop).
edible(celery, true).
edible_part(celery, leaf).
edible_part(celery, root).
edible_part(celery, seed).
use_category(celery, companion_plant).
trait(celery, companion_plant).
use_category(celery, culinary_herb).
trait(celery, culinary_herb).
use_category(celery, medicinal_plant).
trait(celery, medicinal).
use_category(celery, repellent_plant).
trait(celery, pest_repellent).
use_category(celery, root_tuber_crop).
plant(chickpea).
scientific_name(chickpea, 'cicer arietinum').
plant(chicory).
scientific_name(chicory, 'cichorium intybus').
plant(coriander).
scientific_name(coriander, 'coriandrum sativum').
edible(cucumber, true).
edible_part(cucumber, fruit).
edible_part(cucumber, leaf).
edible_part(cucumber, oil).
edible_part(cucumber, seed).
use_category(cucumber, fruit_crop).
use_category(cucumber, medicinal_plant).
trait(cucumber, medicinal).
use_category(cucumber, oil_crop).
use_category(cucumber, repellent_plant).
trait(cucumber, pest_repellent).
trait(cucumber, pollinator_attractor).
edible(dandelion, true).
edible_part(dandelion, flower).
edible_part(dandelion, leaf).
edible_part(dandelion, root).
use_category(dandelion, beverage_plant).
use_category(dandelion, medicinal_plant).
trait(dandelion, medicinal).
use_category(dandelion, root_tuber_crop).
trait(dandelion, pollinator_attractor).
trait(dandelion, pest_confuser).
edible(eggplant, true).
edible_part(eggplant, fruit).
edible_part(eggplant, leaf).
use_category(eggplant, fruit_crop).
use_category(eggplant, medicinal_plant).
trait(eggplant, medicinal).
trait(eggplant, pollinator_attractor).
edible(fennel, true).
edible_part(fennel, flower).
edible_part(fennel, leaf).
edible_part(fennel, oil).
edible_part(fennel, root).
edible_part(fennel, seed).
edible_part(fennel, stem).
use_category(fennel, beverage_plant).
use_category(fennel, companion_plant).
trait(fennel, companion_plant).
use_category(fennel, culinary_herb).
trait(fennel, culinary_herb).
use_category(fennel, medicinal_plant).
trait(fennel, medicinal).
use_category(fennel, oil_crop).
use_category(fennel, repellent_plant).
trait(fennel, pest_repellent).
use_category(fennel, root_tuber_crop).
trait(fennel, pollinator_attractor).
plant(fig).
scientific_name(fig, 'ficus carica').
edible(fig, true).
edible_part(fig, fruit).
use_category(fig, fruit_crop).
use_category(fig, medicinal_plant).
trait(fig, medicinal).
trait(fig, pest_confuser).
edible(ginger, true).
edible_part(ginger, flower).
edible_part(ginger, leaf).
edible_part(ginger, oil).
edible_part(ginger, root).
edible_part(ginger, stem).
use_category(ginger, beverage_plant).
use_category(ginger, culinary_herb).
trait(ginger, culinary_herb).
use_category(ginger, medicinal_plant).
trait(ginger, medicinal).
use_category(ginger, oil_crop).
use_category(ginger, root_tuber_crop).
scientific_name(grape, 'vitis vinifera').
edible(grape, true).
edible_part(grape, flower).
edible_part(grape, fruit).
edible_part(grape, leaf).
edible_part(grape, oil).
edible_part(grape, stem).
use_category(grape, fruit_crop).
use_category(grape, medicinal_plant).
trait(grape, medicinal).
use_category(grape, oil_crop).
trait(grape, pollinator_attractor).
trait(grape, pest_confuser).
scientific_name(kale, 'brassica oleracea var. acephala').
scientific_name(lavender, 'lavandula angustifolia').
edible(lavender, true).
edible_part(lavender, flower).
edible_part(lavender, leaf).
use_category(lavender, beverage_plant).
use_category(lavender, companion_plant).
trait(lavender, companion_plant).
use_category(lavender, culinary_herb).
trait(lavender, culinary_herb).
use_category(lavender, medicinal_plant).
trait(lavender, medicinal).
use_category(lavender, repellent_plant).
trait(lavender, pest_repellent).
trait(lavender, pollinator_attractor).
trait(lavender, pest_confuser).
edible(lemon_balm, true).
edible_part(lemon_balm, leaf).
use_category(lemon_balm, beverage_plant).
use_category(lemon_balm, companion_plant).
trait(lemon_balm, companion_plant).
use_category(lemon_balm, culinary_herb).
trait(lemon_balm, culinary_herb).
use_category(lemon_balm, medicinal_plant).
trait(lemon_balm, medicinal).
use_category(lemon_balm, repellent_plant).
trait(lemon_balm, pest_repellent).
trait(lemon_balm, pollinator_attractor).
trait(lemon_balm, pest_confuser).
plant(lentil).
scientific_name(lentil, 'lens culinaris').
edible(lentil, true).
edible_part(lentil, seed).
use_category(lentil, medicinal_plant).
trait(lentil, medicinal).
edible(lettuce, true).
edible_part(lettuce, leaf).
edible_part(lettuce, oil).
edible_part(lettuce, seed).
use_category(lettuce, medicinal_plant).
trait(lettuce, medicinal).
use_category(lettuce, oil_crop).
scientific_name(melon, 'cucumis melo').
edible(melon, true).
edible_part(melon, fruit).
edible_part(melon, oil).
edible_part(melon, seed).
use_category(melon, fruit_crop).
use_category(melon, medicinal_plant).
trait(melon, medicinal).
use_category(melon, oil_crop).
trait(melon, pollinator_attractor).
plant(moringa).
scientific_name(moringa, 'moringa oleifera').
edible(moringa, true).
edible_part(moringa, flower).
edible_part(moringa, leaf).
edible_part(moringa, oil).
edible_part(moringa, root).
edible_part(moringa, seed).
edible_part(moringa, stem).
use_category(moringa, beverage_plant).
use_category(moringa, culinary_herb).
trait(moringa, culinary_herb).
use_category(moringa, medicinal_plant).
trait(moringa, medicinal).
use_category(moringa, oil_crop).
use_category(moringa, root_tuber_crop).
trait(moringa, pollinator_attractor).
trait(moringa, pest_confuser).
edible(onion, true).
edible_part(onion, flower).
edible_part(onion, leaf).
edible_part(onion, root).
edible_part(onion, seed).
use_category(onion, medicinal_plant).
trait(onion, medicinal).
use_category(onion, repellent_plant).
trait(onion, pest_repellent).
use_category(onion, root_tuber_crop).
trait(onion, pollinator_attractor).
trait(onion, pest_confuser).
edible(oregano, true).
edible_part(oregano, flower).
edible_part(oregano, leaf).
edible_part(oregano, stem).
use_category(oregano, beverage_plant).
use_category(oregano, companion_plant).
trait(oregano, companion_plant).
use_category(oregano, culinary_herb).
trait(oregano, culinary_herb).
use_category(oregano, medicinal_plant).
trait(oregano, medicinal).
use_category(oregano, repellent_plant).
trait(oregano, pest_repellent).
trait(oregano, pollinator_attractor).
trait(oregano, pest_confuser).
edible(parsley, true).
edible_part(parsley, leaf).
use_category(parsley, beverage_plant).
use_category(parsley, companion_plant).
trait(parsley, companion_plant).
use_category(parsley, culinary_herb).
trait(parsley, culinary_herb).
use_category(parsley, medicinal_plant).
trait(parsley, medicinal).
use_category(parsley, repellent_plant).
trait(parsley, pest_repellent).
trait(parsley, pollinator_attractor).
edible(pea, true).
edible_part(pea, leaf).
edible_part(pea, seed).
edible_part(pea, stem).
use_category(pea, companion_plant).
trait(pea, companion_plant).
use_category(pea, medicinal_plant).
trait(pea, medicinal).
trait(pea, pollinator_attractor).
edible(peanut, true).
edible_part(peanut, leaf).
edible_part(peanut, oil).
edible_part(peanut, seed).
use_category(peanut, medicinal_plant).
trait(peanut, medicinal).
use_category(peanut, oil_crop).
trait(peanut, pollinator_attractor).
edible(pear, true).
edible_part(pear, fruit).
use_category(pear, fruit_crop).
use_category(pear, medicinal_plant).
trait(pear, medicinal).
use_category(pear, repellent_plant).
trait(pear, pest_repellent).
trait(pear, pollinator_attractor).
trait(pear, pest_confuser).
plant(peppermint).
scientific_name(peppermint, 'mentha x piperita').
edible(peppermint, true).
edible_part(peppermint, leaf).
use_category(peppermint, culinary_herb).
trait(peppermint, culinary_herb).
use_category(peppermint, medicinal_plant).
trait(peppermint, medicinal).
trait(peppermint, pollinator_attractor).
edible(potato, true).
edible_part(potato, root).
use_category(potato, medicinal_plant).
trait(potato, medicinal).
use_category(potato, root_tuber_crop).
trait(potato, pollinator_attractor).
edible(pumpkin, true).
edible_part(pumpkin, flower).
edible_part(pumpkin, fruit).
edible_part(pumpkin, leaf).
edible_part(pumpkin, oil).
edible_part(pumpkin, root).
edible_part(pumpkin, seed).
use_category(pumpkin, fruit_crop).
use_category(pumpkin, medicinal_plant).
trait(pumpkin, medicinal).
use_category(pumpkin, oil_crop).
use_category(pumpkin, root_tuber_crop).
trait(pumpkin, pollinator_attractor).
edible(radish, true).
edible_part(radish, flower).
edible_part(radish, leaf).
edible_part(radish, oil).
edible_part(radish, root).
edible_part(radish, seed).
use_category(radish, medicinal_plant).
trait(radish, medicinal).
use_category(radish, oil_crop).
use_category(radish, repellent_plant).
trait(radish, pest_repellent).
use_category(radish, root_tuber_crop).
trait(radish, pollinator_attractor).
edible(raspberry, true).
edible_part(raspberry, fruit).
edible_part(raspberry, root).
edible_part(raspberry, stem).
use_category(raspberry, beverage_plant).
use_category(raspberry, fruit_crop).
use_category(raspberry, medicinal_plant).
trait(raspberry, medicinal).
use_category(raspberry, root_tuber_crop).
trait(raspberry, pollinator_attractor).
edible(sage, true).
edible_part(sage, flower).
edible_part(sage, leaf).
use_category(sage, beverage_plant).
use_category(sage, companion_plant).
trait(sage, companion_plant).
use_category(sage, culinary_herb).
trait(sage, culinary_herb).
use_category(sage, medicinal_plant).
trait(sage, medicinal).
use_category(sage, repellent_plant).
trait(sage, pest_repellent).
trait(sage, pollinator_attractor).
trait(sage, pest_confuser).
plant(soybean).
scientific_name(soybean, 'glycine max').
edible(soybean, true).
edible_part(soybean, leaf).
edible_part(soybean, oil).
edible_part(soybean, seed).
use_category(soybean, medicinal_plant).
trait(soybean, medicinal).
use_category(soybean, oil_crop).
use_category(soybean, repellent_plant).
trait(soybean, pest_repellent).
trait(soybean, pollinator_attractor).
plant(spearmint).
scientific_name(spearmint, 'mentha spicata').
edible(spearmint, true).
edible_part(spearmint, leaf).
use_category(spearmint, beverage_plant).
use_category(spearmint, companion_plant).
trait(spearmint, companion_plant).
use_category(spearmint, culinary_herb).
trait(spearmint, culinary_herb).
use_category(spearmint, medicinal_plant).
trait(spearmint, medicinal).
use_category(spearmint, repellent_plant).
trait(spearmint, pest_repellent).
trait(spearmint, pollinator_attractor).
trait(spearmint, pest_confuser).
scientific_name(strawberry, 'fragaria x ananassa').
edible(strawberry, true).
edible_part(strawberry, fruit).
edible_part(strawberry, leaf).
use_category(strawberry, fruit_crop).
use_category(strawberry, medicinal_plant).
trait(strawberry, medicinal).
trait(strawberry, pollinator_attractor).
trait(strawberry, pest_confuser).
edible(sunflower, true).
edible_part(sunflower, flower).
edible_part(sunflower, oil).
edible_part(sunflower, seed).
edible_part(sunflower, stem).
use_category(sunflower, medicinal_plant).
trait(sunflower, medicinal).
use_category(sunflower, oil_crop).
trait(sunflower, pollinator_attractor).
edible(sweet_potato, true).
edible_part(sweet_potato, leaf).
edible_part(sweet_potato, root).
edible_part(sweet_potato, stem).
use_category(sweet_potato, medicinal_plant).
trait(sweet_potato, medicinal).
use_category(sweet_potato, root_tuber_crop).
trait(sweet_potato, pollinator_attractor).
trait(sweet_potato, pest_confuser).
edible(thyme, true).
edible_part(thyme, flower).
edible_part(thyme, leaf).
edible_part(thyme, stem).
use_category(thyme, beverage_plant).
use_category(thyme, companion_plant).
trait(thyme, companion_plant).
use_category(thyme, culinary_herb).
trait(thyme, culinary_herb).
use_category(thyme, medicinal_plant).
trait(thyme, medicinal).
use_category(thyme, repellent_plant).
trait(thyme, pest_repellent).
trait(thyme, pollinator_attractor).
trait(thyme, pest_confuser).
edible(tomato, true).
edible_part(tomato, fruit).
edible_part(tomato, oil).
edible_part(tomato, seed).
use_category(tomato, beverage_plant).
use_category(tomato, companion_plant).
trait(tomato, companion_plant).
use_category(tomato, fruit_crop).
use_category(tomato, medicinal_plant).
trait(tomato, medicinal).
use_category(tomato, oil_crop).
use_category(tomato, repellent_plant).
trait(tomato, pest_repellent).
trait(tomato, pollinator_attractor).
edible(watermelon, true).
edible_part(watermelon, fruit).
edible_part(watermelon, leaf).
edible_part(watermelon, oil).
edible_part(watermelon, seed).
use_category(watermelon, fruit_crop).
use_category(watermelon, medicinal_plant).
trait(watermelon, medicinal).
use_category(watermelon, oil_crop).
trait(watermelon, pollinator_attractor).
edible(zucchini, true).
edible_part(zucchini, flower).
edible_part(zucchini, fruit).
edible_part(zucchini, leaf).
edible_part(zucchini, oil).
edible_part(zucchini, root).
edible_part(zucchini, seed).
use_category(zucchini, fruit_crop).
use_category(zucchini, medicinal_plant).
trait(zucchini, medicinal).
use_category(zucchini, oil_crop).
use_category(zucchini, root_tuber_crop).
trait(zucchini, pollinator_attractor).
