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
