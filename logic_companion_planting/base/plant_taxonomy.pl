% FILE: logic_companion_planting/base/plant_taxonomy_fact.pl
%
% Taxonomy enrichment for plant_group.pl.
% Purpose:
% - Bridge common plant atoms to scientific names and genera.
% - Support RHS/Perenual/genus-level matching for growth timeline facts.
% - Keep taxonomy separate from functional grouping rules.
%
% Sources used for verification/cross-checking:
% - Plants of the World Online (Royal Botanic Gardens, Kew)
% - USDA NRCS PLANTS Database
% - IPNI for nomenclatural spelling where needed
%
% Confidence:
% - high   = common crop/herb identity is standard and specific
% - medium = common name may refer to several species/cultivar groups
% - low    = likely typo/alias or ambiguous entry

% =========================================
% TAXONOMIC PREDICATES
% =========================================

% accepted_scientific_name(PlantAtom, ScientificName).
% alternate_scientific_name(PlantAtom, ScientificName).
% genus(PlantAtom, GenusAtom).
% family(PlantAtom, FamilyAtom).
% taxonomy_confidence(PlantAtom, Confidence).
% taxonomy_source(PlantAtom, SourceName).
% taxonomy_note(PlantAtom, Note).

:- discontiguous accepted_scientific_name/2.
:- discontiguous alternate_scientific_name/2.
:- discontiguous genus/2.
:- discontiguous family/2.
:- discontiguous taxonomy_confidence/2.
:- discontiguous taxonomy_source/2.
:- discontiguous taxonomy_note/2.

:- multifile accepted_scientific_name/2.
:- multifile genus/2.
:- multifile family/2.

% =========================================
% ALIASES / CLEANUP
% =========================================

accepted_scientific_name(amaranth, 'Amaranthus spp.').
genus(amaranth, amaranthus).
family(amaranth, amaranthaceae).
taxonomy_confidence(amaranth, medium).
taxonomy_source(amaranth, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(amaranth, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(artichoke, 'Cynara cardunculus var. scolymus').
genus(artichoke, cynara).
family(artichoke, asteraceae).
taxonomy_confidence(artichoke, high).
taxonomy_source(artichoke, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(arugula, 'Eruca vesicaria').
genus(arugula, eruca).
family(arugula, brassicaceae).
taxonomy_confidence(arugula, high).
taxonomy_source(arugula, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(barley, 'Hordeum vulgare').
genus(barley, hordeum).
family(barley, poaceae).
taxonomy_confidence(barley, high).
taxonomy_source(barley, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(basil, 'Ocimum basilicum').
genus(basil, ocimum).
family(basil, lamiaceae).
taxonomy_confidence(basil, high).
taxonomy_source(basil, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(bean_bush, 'Phaseolus vulgaris').
genus(bean_bush, phaseolus).
family(bean_bush, fabaceae).
taxonomy_confidence(bean_bush, high).
taxonomy_source(bean_bush, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(bean_pole, 'Phaseolus vulgaris').
genus(bean_pole, phaseolus).
family(bean_pole, fabaceae).
taxonomy_confidence(bean_pole, high).
taxonomy_source(bean_pole, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(bee_balm, 'Monarda didyma').
genus(bee_balm, monarda).
family(bee_balm, lamiaceae).
taxonomy_confidence(bee_balm, medium).
taxonomy_source(bee_balm, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(bee_balm, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(beet, 'Beta vulgaris').
genus(beet, beta).
family(beet, amaranthaceae).
taxonomy_confidence(beet, high).
taxonomy_source(beet, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(bell_pepper, 'Capsicum annuum').
genus(bell_pepper, capsicum).
family(bell_pepper, solanaceae).
taxonomy_confidence(bell_pepper, high).
taxonomy_source(bell_pepper, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(black_pepper, 'Piper nigrum').
genus(black_pepper, piper).
family(black_pepper, piperaceae).
taxonomy_confidence(black_pepper, high).
taxonomy_source(black_pepper, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(blackberry, 'Rubus spp.').
genus(blackberry, rubus).
family(blackberry, rosaceae).
taxonomy_confidence(blackberry, medium).
taxonomy_source(blackberry, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(blackberry, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(blueberry, 'Vaccinium spp.').
genus(blueberry, vaccinium).
family(blueberry, ericaceae).
taxonomy_confidence(blueberry, medium).
taxonomy_source(blueberry, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(blueberry, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(bok_choy, 'Brassica rapa subsp. chinensis').
genus(bok_choy, brassica).
family(bok_choy, brassicaceae).
taxonomy_confidence(bok_choy, high).
taxonomy_source(bok_choy, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(borage, 'Borago officinalis').
genus(borage, borago).
family(borage, boraginaceae).
taxonomy_confidence(borage, high).
taxonomy_source(borage, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(broccoli, 'Brassica oleracea var. italica').
genus(broccoli, brassica).
family(broccoli, brassicaceae).
taxonomy_confidence(broccoli, high).
taxonomy_source(broccoli, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(brussels_sprout, 'Brassica oleracea var. gemmifera').
genus(brussels_sprout, brassica).
family(brussels_sprout, brassicaceae).
taxonomy_confidence(brussels_sprout, high).
taxonomy_source(brussels_sprout, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(cabbage, 'Brassica oleracea var. capitata').
genus(cabbage, brassica).
family(cabbage, brassicaceae).
taxonomy_confidence(cabbage, high).
taxonomy_source(cabbage, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(calendula, 'Calendula officinalis').
genus(calendula, calendula).
family(calendula, asteraceae).
taxonomy_confidence(calendula, high).
taxonomy_source(calendula, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(caraway, 'Carum carvi').
genus(caraway, carum).
family(caraway, apiaceae).
taxonomy_confidence(caraway, high).
taxonomy_source(caraway, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(carrot, 'Daucus carota subsp. sativus').
genus(carrot, daucus).
family(carrot, apiaceae).
taxonomy_confidence(carrot, high).
taxonomy_source(carrot, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(catnip, 'Nepeta cataria').
genus(catnip, nepeta).
family(catnip, lamiaceae).
taxonomy_confidence(catnip, high).
taxonomy_source(catnip, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(cauliflower, 'Brassica oleracea var. botrytis').
genus(cauliflower, brassica).
family(cauliflower, brassicaceae).
taxonomy_confidence(cauliflower, high).
taxonomy_source(cauliflower, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(chamomile, 'Matricaria chamomilla').
alternate_scientific_name(chamomile, 'Matricaria recutita').
genus(chamomile, matricaria).
family(chamomile, asteraceae).
taxonomy_confidence(chamomile, medium).
taxonomy_source(chamomile, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(chamomile, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(chili_pepper, 'Capsicum annuum').
genus(chili_pepper, capsicum).
family(chili_pepper, solanaceae).
taxonomy_confidence(chili_pepper, high).
taxonomy_source(chili_pepper, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(chive, 'Allium schoenoprasum').
genus(chive, allium).
family(chive, amaryllidaceae).
taxonomy_confidence(chive, high).
taxonomy_source(chive, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(choy_sum, 'Brassica rapa var. parachinensis').
genus(choy_sum, brassica).
family(choy_sum, brassicaceae).
taxonomy_confidence(choy_sum, high).
taxonomy_source(choy_sum, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(chrysanthemum, 'Chrysanthemum x morifolium').
genus(chrysanthemum, chrysanthemum).
family(chrysanthemum, asteraceae).
taxonomy_confidence(chrysanthemum, medium).
taxonomy_source(chrysanthemum, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(chrysanthemum, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(cilantro, 'Coriandrum sativum').
genus(cilantro, coriandrum).
family(cilantro, apiaceae).
taxonomy_confidence(cilantro, high).
taxonomy_source(cilantro, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(cinnamon, 'Cinnamomum verum').
genus(cinnamon, cinnamomum).
family(cinnamon, lauraceae).
taxonomy_confidence(cinnamon, high).
taxonomy_source(cinnamon, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(clover, 'Trifolium spp.').
genus(clover, trifolium).
family(clover, fabaceae).
taxonomy_confidence(clover, medium).
taxonomy_source(clover, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(clover, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(comfrey, 'Symphytum officinale').
genus(comfrey, symphytum).
family(comfrey, boraginaceae).
taxonomy_confidence(comfrey, high).
taxonomy_source(comfrey, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(corn, 'Zea mays').
genus(corn, zea).
family(corn, poaceae).
taxonomy_confidence(corn, high).
taxonomy_source(corn, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(cornflower, 'Centaurea cyanus').
genus(cornflower, centaurea).
family(cornflower, asteraceae).
taxonomy_confidence(cornflower, high).
taxonomy_source(cornflower, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(cucumber, 'Cucumis sativus').
genus(cucumber, cucumis).
family(cucumber, cucurbitaceae).
taxonomy_confidence(cucumber, high).
taxonomy_source(cucumber, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(dandelion, 'Taraxacum officinale agg.').
genus(dandelion, taraxacum).
family(dandelion, asteraceae).
taxonomy_confidence(dandelion, medium).
taxonomy_source(dandelion, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(dandelion, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(dill, 'Anethum graveolens').
genus(dill, anethum).
family(dill, apiaceae).
taxonomy_confidence(dill, high).
taxonomy_source(dill, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(eggplant, 'Solanum melongena').
genus(eggplant, solanum).
family(eggplant, solanaceae).
taxonomy_confidence(eggplant, high).
taxonomy_source(eggplant, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(elderflower, 'Sambucus nigra').
genus(elderflower, sambucus).
family(elderflower, adoxaceae).
taxonomy_confidence(elderflower, medium).
taxonomy_source(elderflower, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(elderflower, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(fennel, 'Foeniculum vulgare').
genus(fennel, foeniculum).
family(fennel, apiaceae).
taxonomy_confidence(fennel, high).
taxonomy_source(fennel, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(galangal, 'Alpinia galanga').
genus(galangal, alpinia).
family(galangal, zingiberaceae).
taxonomy_confidence(galangal, high).
taxonomy_source(galangal, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(garlic, 'Allium sativum').
genus(garlic, allium).
family(garlic, amaryllidaceae).
taxonomy_confidence(garlic, high).
taxonomy_source(garlic, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(ginger, 'Zingiber officinale').
genus(ginger, zingiber).
family(ginger, zingiberaceae).
taxonomy_confidence(ginger, high).
taxonomy_source(ginger, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(gladiolus, 'Gladiolus spp.').
genus(gladiolus, gladiolus).
family(gladiolus, iridaceae).
taxonomy_confidence(gladiolus, medium).
taxonomy_source(gladiolus, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(gladiolus, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(gourd, 'Lagenaria siceraria').
genus(gourd, lagenaria).
family(gourd, cucurbitaceae).
taxonomy_confidence(gourd, medium).
taxonomy_source(gourd, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(gourd, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(grape, 'Vitis vinifera').
genus(grape, vitis).
family(grape, vitaceae).
taxonomy_confidence(grape, high).
taxonomy_source(grape, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(green_onion, 'Allium fistulosum').
genus(green_onion, allium).
family(green_onion, amaryllidaceae).
taxonomy_confidence(green_onion, medium).
taxonomy_source(green_onion, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(green_onion, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(hibiscus, 'Hibiscus rosa-sinensis').
genus(hibiscus, hibiscus).
family(hibiscus, malvaceae).
taxonomy_confidence(hibiscus, medium).
taxonomy_source(hibiscus, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(hibiscus, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(hydrangea, 'Hydrangea macrophylla').
genus(hydrangea, hydrangea).
family(hydrangea, hydrangeaceae).
taxonomy_confidence(hydrangea, medium).
taxonomy_source(hydrangea, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(hydrangea, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(hyssop, 'Hyssopus officinalis').
genus(hyssop, hyssopus).
family(hyssop, lamiaceae).
taxonomy_confidence(hyssop, high).
taxonomy_source(hyssop, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(jasmine, 'Jasminum spp.').
genus(jasmine, jasminum).
family(jasmine, oleaceae).
taxonomy_confidence(jasmine, medium).
taxonomy_source(jasmine, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(jasmine, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(johnson_grass, 'Sorghum halepense').
genus(johnson_grass, sorghum).
family(johnson_grass, poaceae).
taxonomy_confidence(johnson_grass, high).
taxonomy_source(johnson_grass, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(kale, 'Brassica oleracea var. sabellica').
genus(kale, brassica).
family(kale, brassicaceae).
taxonomy_confidence(kale, medium).
taxonomy_source(kale, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(kale, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(kencur, 'Kaempferia galanga').
genus(kencur, kaempferia).
family(kencur, zingiberaceae).
taxonomy_confidence(kencur, high).
taxonomy_source(kencur, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(lavender, 'Lavandula angustifolia').
genus(lavender, lavandula).
family(lavender, lamiaceae).
taxonomy_confidence(lavender, high).
taxonomy_source(lavender, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(leek, 'Allium ampeloprasum var. porrum').
genus(leek, allium).
family(leek, amaryllidaceae).
taxonomy_confidence(leek, high).
taxonomy_source(leek, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(lemon_balm, 'Melissa officinalis').
genus(lemon_balm, melissa).
family(lemon_balm, lamiaceae).
taxonomy_confidence(lemon_balm, high).
taxonomy_source(lemon_balm, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(lemongrass, 'Cymbopogon citratus').
genus(lemongrass, cymbopogon).
family(lemongrass, poaceae).
taxonomy_confidence(lemongrass, high).
taxonomy_source(lemongrass, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(lettuce, 'Lactuca sativa').
genus(lettuce, lactuca).
family(lettuce, asteraceae).
taxonomy_confidence(lettuce, high).
taxonomy_source(lettuce, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(melon, 'Cucumis melo').
genus(melon, cucumis).
family(melon, cucurbitaceae).
taxonomy_confidence(melon, high).
taxonomy_source(melon, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(mint, 'Mentha spp.').
genus(mint, mentha).
family(mint, lamiaceae).
taxonomy_confidence(mint, medium).
taxonomy_source(mint, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(mint, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(mustard_green, 'Brassica juncea').
genus(mustard_green, brassica).
family(mustard_green, brassicaceae).
taxonomy_confidence(mustard_green, medium).
taxonomy_source(mustard_green, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(mustard_green, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(nasturtium, 'Tropaeolum majus').
genus(nasturtium, tropaeolum).
family(nasturtium, tropaeolaceae).
taxonomy_confidence(nasturtium, high).
taxonomy_source(nasturtium, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(nutmeg, 'Myristica fragrans').
genus(nutmeg, myristica).
family(nutmeg, myristicaceae).
taxonomy_confidence(nutmeg, high).
taxonomy_source(nutmeg, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(okra, 'Abelmoschus esculentus').
genus(okra, abelmoschus).
family(okra, malvaceae).
taxonomy_confidence(okra, high).
taxonomy_source(okra, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(onion, 'Allium cepa').
genus(onion, allium).
family(onion, amaryllidaceae).
taxonomy_confidence(onion, high).
taxonomy_source(onion, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(oregano, 'Origanum vulgare').
genus(oregano, origanum).
family(oregano, lamiaceae).
taxonomy_confidence(oregano, high).
taxonomy_source(oregano, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(parsley, 'Petroselinum crispum').
genus(parsley, petroselinum).
family(parsley, apiaceae).
taxonomy_confidence(parsley, high).
taxonomy_source(parsley, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(pea, 'Pisum sativum').
genus(pea, pisum).
family(pea, fabaceae).
taxonomy_confidence(pea, high).
taxonomy_source(pea, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(pea_english, 'Pisum sativum').
genus(pea_english, pisum).
family(pea_english, fabaceae).
taxonomy_confidence(pea_english, high).
taxonomy_source(pea_english, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(peanut, 'Arachis hypogaea').
genus(peanut, arachis).
family(peanut, fabaceae).
taxonomy_confidence(peanut, high).
taxonomy_source(peanut, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(pepper, 'Capsicum spp.').
genus(pepper, capsicum).
family(pepper, solanaceae).
taxonomy_confidence(pepper, medium).
taxonomy_source(pepper, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(pepper, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(potato, 'Solanum tuberosum').
genus(potato, solanum).
family(potato, solanaceae).
taxonomy_confidence(potato, high).
taxonomy_source(potato, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(pumpkin, 'Cucurbita pepo').
genus(pumpkin, cucurbita).
family(pumpkin, cucurbitaceae).
taxonomy_confidence(pumpkin, medium).
taxonomy_source(pumpkin, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(pumpkin, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(radish, 'Raphanus sativus').
genus(radish, raphanus).
family(radish, brassicaceae).
taxonomy_confidence(radish, high).
taxonomy_source(radish, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(raspberry, 'Rubus idaeus').
genus(raspberry, rubus).
family(raspberry, rosaceae).
taxonomy_confidence(raspberry, medium).
taxonomy_source(raspberry, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(raspberry, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(rice, 'Oryza sativa').
genus(rice, oryza).
family(rice, poaceae).
taxonomy_confidence(rice, high).
taxonomy_source(rice, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(rose, 'Rosa spp.').
genus(rose, rosa).
family(rose, rosaceae).
taxonomy_confidence(rose, medium).
taxonomy_source(rose, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(rose, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(rosemary, 'Salvia rosmarinus').
genus(rosemary, salvia).
family(rosemary, lamiaceae).
taxonomy_confidence(rosemary, high).
taxonomy_source(rosemary, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(rue, 'Ruta graveolens').
genus(rue, ruta).
family(rue, rutaceae).
taxonomy_confidence(rue, high).
taxonomy_source(rue, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(rye, 'Secale cereale').
genus(rye, secale).
family(rye, poaceae).
taxonomy_confidence(rye, high).
taxonomy_source(rye, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(sage, 'Salvia officinalis').
genus(sage, salvia).
family(sage, lamiaceae).
taxonomy_confidence(sage, high).
taxonomy_source(sage, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(shallot, 'Allium cepa Aggregatum Group').
genus(shallot, allium).
family(shallot, amaryllidaceae).
taxonomy_confidence(shallot, medium).
taxonomy_source(shallot, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(shallot, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(spelt, 'Triticum spelta').
genus(spelt, triticum).
family(spelt, poaceae).
taxonomy_confidence(spelt, high).
taxonomy_source(spelt, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(spinach, 'Spinacia oleracea').
genus(spinach, spinacia).
family(spinach, amaranthaceae).
taxonomy_confidence(spinach, high).
taxonomy_source(spinach, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(squash, 'Cucurbita pepo').
genus(squash, cucurbita).
family(squash, cucurbitaceae).
taxonomy_confidence(squash, medium).
taxonomy_source(squash, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(squash, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(strawberry, 'Fragaria ananassa').
genus(strawberry, fragaria).
family(strawberry, rosaceae).
taxonomy_confidence(strawberry, high).
taxonomy_source(strawberry, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(summer_savory, 'Satureja hortensis').
genus(summer_savory, satureja).
family(summer_savory, lamiaceae).
taxonomy_confidence(summer_savory, high).
taxonomy_source(summer_savory, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(sunflower, 'Helianthus annuus').
genus(sunflower, helianthus).
family(sunflower, asteraceae).
taxonomy_confidence(sunflower, high).
taxonomy_source(sunflower, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(sweet_potato, 'Ipomoea batatas').
genus(sweet_potato, ipomoea).
family(sweet_potato, convolvulaceae).
taxonomy_confidence(sweet_potato, high).
taxonomy_source(sweet_potato, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(swiss_chard, 'Beta vulgaris subsp. vulgaris').
genus(swiss_chard, beta).
family(swiss_chard, amaranthaceae).
taxonomy_confidence(swiss_chard, high).
taxonomy_source(swiss_chard, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(tansy, 'Tanacetum vulgare').
genus(tansy, tanacetum).
family(tansy, asteraceae).
taxonomy_confidence(tansy, high).
taxonomy_source(tansy, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(taro, 'Colocasia esculenta').
genus(taro, colocasia).
family(taro, araceae).
taxonomy_confidence(taro, high).
taxonomy_source(taro, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(tarragon, 'Artemisia dracunculus').
genus(tarragon, artemisia).
family(tarragon, asteraceae).
taxonomy_confidence(tarragon, high).
taxonomy_source(tarragon, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(thyme, 'Thymus vulgaris').
genus(thyme, thymus).
family(thyme, lamiaceae).
taxonomy_confidence(thyme, high).
taxonomy_source(thyme, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(tomato, 'Solanum lycopersicum').
alternate_scientific_name(tomato, 'Lycopersicon esculentum').
genus(tomato, solanum).
family(tomato, solanaceae).
taxonomy_confidence(tomato, high).
taxonomy_source(tomato, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(turmeric, 'Curcuma longa').
genus(turmeric, curcuma).
family(turmeric, zingiberaceae).
taxonomy_confidence(turmeric, high).
taxonomy_source(turmeric, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(turnip, 'Brassica rapa subsp. rapa').
genus(turnip, brassica).
family(turnip, brassicaceae).
taxonomy_confidence(turnip, high).
taxonomy_source(turnip, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(viola, 'Viola spp.').
genus(viola, viola).
family(viola, violaceae).
taxonomy_confidence(viola, medium).
taxonomy_source(viola, 'Kew POWO / USDA PLANTS cross-check').
taxonomy_note(viola, 'Common name is somewhat broad; scientific name/genus should be confirmed from Perenual scientific_name when available.').

accepted_scientific_name(water_spinach, 'Ipomoea aquatica').
genus(water_spinach, ipomoea).
family(water_spinach, convolvulaceae).
taxonomy_confidence(water_spinach, high).
taxonomy_source(water_spinach, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(watermelon, 'Citrullus lanatus').
genus(watermelon, citrullus).
family(watermelon, cucurbitaceae).
taxonomy_confidence(watermelon, high).
taxonomy_source(watermelon, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(wheat, 'Triticum aestivum').
genus(wheat, triticum).
family(wheat, poaceae).
taxonomy_confidence(wheat, high).
taxonomy_source(wheat, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(white_pepper, 'Piper nigrum').
genus(white_pepper, piper).
family(white_pepper, piperaceae).
taxonomy_confidence(white_pepper, high).
taxonomy_source(white_pepper, 'Kew POWO / USDA PLANTS cross-check').

accepted_scientific_name(yarrow, 'Achillea millefolium').
genus(yarrow, achillea).
family(yarrow, asteraceae).
taxonomy_confidence(yarrow, high).
taxonomy_source(yarrow, 'Kew POWO / USDA PLANTS cross-check').

% =========================================
% EXPANDED TAXONOMY - EDIBLE PLANTS, ROOTS, HERBS, SPICES, FLOWERS
% =========================================
% Added as broad project enrichment. Prefer Perenual scientific_name when available for user-added plants.
% Sources are recorded per entry; ambiguous common names use taxonomy_confidence(..., medium).

accepted_scientific_name(lentil, 'Lens culinaris').
genus(lentil, lens).
family(lentil, fabaceae).
taxonomy_confidence(lentil, high).
taxonomy_source(lentil, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(chickpea, 'Cicer arietinum').
genus(chickpea, cicer).
family(chickpea, fabaceae).
taxonomy_confidence(chickpea, high).
taxonomy_source(chickpea, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(soybean, 'Glycine max').
genus(soybean, glycine).
family(soybean, fabaceae).
taxonomy_confidence(soybean, high).
taxonomy_source(soybean, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(edamame, 'Glycine max').
genus(edamame, glycine).
family(edamame, fabaceae).
taxonomy_confidence(edamame, high).
taxonomy_source(edamame, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(edamame, 'Edamame is immature soybean; kept as separate crop atom for UI/search convenience.').

accepted_scientific_name(cowpea, 'Vigna unguiculata').
genus(cowpea, vigna).
family(cowpea, fabaceae).
taxonomy_confidence(cowpea, high).
taxonomy_source(cowpea, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(yardlong_bean, 'Vigna unguiculata subsp. sesquipedalis').
genus(yardlong_bean, vigna).
family(yardlong_bean, fabaceae).
taxonomy_confidence(yardlong_bean, high).
taxonomy_source(yardlong_bean, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(mung_bean, 'Vigna radiata').
genus(mung_bean, vigna).
family(mung_bean, fabaceae).
taxonomy_confidence(mung_bean, high).
taxonomy_source(mung_bean, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(fava_bean, 'Vicia faba').
genus(fava_bean, vicia).
family(fava_bean, fabaceae).
taxonomy_confidence(fava_bean, high).
taxonomy_source(fava_bean, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(lima_bean, 'Phaseolus lunatus').
genus(lima_bean, phaseolus).
family(lima_bean, fabaceae).
taxonomy_confidence(lima_bean, high).
taxonomy_source(lima_bean, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(adzuki_bean, 'Vigna angularis').
genus(adzuki_bean, vigna).
family(adzuki_bean, fabaceae).
taxonomy_confidence(adzuki_bean, high).
taxonomy_source(adzuki_bean, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(pigeon_pea, 'Cajanus cajan').
genus(pigeon_pea, cajanus).
family(pigeon_pea, fabaceae).
taxonomy_confidence(pigeon_pea, high).
taxonomy_source(pigeon_pea, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(oat, 'Avena sativa').
genus(oat, avena).
family(oat, poaceae).
taxonomy_confidence(oat, high).
taxonomy_source(oat, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(sorghum, 'Sorghum bicolor').
genus(sorghum, sorghum).
family(sorghum, poaceae).
taxonomy_confidence(sorghum, high).
taxonomy_source(sorghum, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(millet, 'Panicum miliaceum').
genus(millet, panicum).
family(millet, poaceae).
taxonomy_confidence(millet, medium).
taxonomy_source(millet, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(millet, 'Common name millet may refer to several cereal grasses; this entry uses proso millet.').

accepted_scientific_name(pearl_millet, 'Cenchrus americanus').
genus(pearl_millet, cenchrus).
family(pearl_millet, poaceae).
taxonomy_confidence(pearl_millet, high).
taxonomy_source(pearl_millet, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(quinoa, 'Chenopodium quinoa').
genus(quinoa, chenopodium).
family(quinoa, amaranthaceae).
taxonomy_confidence(quinoa, high).
taxonomy_source(quinoa, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(buckwheat, 'Fagopyrum esculentum').
genus(buckwheat, fagopyrum).
family(buckwheat, polygonaceae).
taxonomy_confidence(buckwheat, high).
taxonomy_source(buckwheat, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(sesame, 'Sesamum indicum').
genus(sesame, sesamum).
family(sesame, pedaliaceae).
taxonomy_confidence(sesame, high).
taxonomy_source(sesame, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(flax, 'Linum usitatissimum').
genus(flax, linum).
family(flax, linaceae).
taxonomy_confidence(flax, high).
taxonomy_source(flax, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(chia, 'Salvia hispanica').
genus(chia, salvia).
family(chia, lamiaceae).
taxonomy_confidence(chia, high).
taxonomy_source(chia, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(parsnip, 'Pastinaca sativa').
genus(parsnip, pastinaca).
family(parsnip, apiaceae).
taxonomy_confidence(parsnip, high).
taxonomy_source(parsnip, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(rutabaga, 'Brassica napus var. napobrassica').
genus(rutabaga, brassica).
family(rutabaga, brassicaceae).
taxonomy_confidence(rutabaga, high).
taxonomy_source(rutabaga, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(daikon, 'Raphanus sativus var. longipinnatus').
genus(daikon, raphanus).
family(daikon, brassicaceae).
taxonomy_confidence(daikon, medium).
taxonomy_source(daikon, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(daikon, 'Daikon is commonly treated as a cultivar group of radish.').

accepted_scientific_name(cassava, 'Manihot esculenta').
genus(cassava, manihot).
family(cassava, euphorbiaceae).
taxonomy_confidence(cassava, high).
taxonomy_source(cassava, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(yam, 'Dioscorea spp.').
genus(yam, dioscorea).
family(yam, dioscoreaceae).
taxonomy_confidence(yam, medium).
taxonomy_source(yam, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(yam, 'Common name yam can refer to multiple Dioscorea species.').

accepted_scientific_name(jicama, 'Pachyrhizus erosus').
genus(jicama, pachyrhizus).
family(jicama, fabaceae).
taxonomy_confidence(jicama, high).
taxonomy_source(jicama, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(lotus_root, 'Nelumbo nucifera').
genus(lotus_root, nelumbo).
family(lotus_root, nelumbonaceae).
taxonomy_confidence(lotus_root, high).
taxonomy_source(lotus_root, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(celeriac, 'Apium graveolens var. rapaceum').
genus(celeriac, apium).
family(celeriac, apiaceae).
taxonomy_confidence(celeriac, high).
taxonomy_source(celeriac, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(wasabi, 'Eutrema japonicum').
genus(wasabi, eutrema).
family(wasabi, brassicaceae).
taxonomy_confidence(wasabi, high).
taxonomy_source(wasabi, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(horseradish, 'Armoracia rusticana').
genus(horseradish, armoracia).
family(horseradish, brassicaceae).
taxonomy_confidence(horseradish, high).
taxonomy_source(horseradish, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(jerusalem_artichoke, 'Helianthus tuberosus').
genus(jerusalem_artichoke, helianthus).
family(jerusalem_artichoke, asteraceae).
taxonomy_confidence(jerusalem_artichoke, high).
taxonomy_source(jerusalem_artichoke, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(salsify, 'Tragopogon porrifolius').
genus(salsify, tragopogon).
family(salsify, asteraceae).
taxonomy_confidence(salsify, high).
taxonomy_source(salsify, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(burdock, 'Arctium lappa').
genus(burdock, arctium).
family(burdock, asteraceae).
taxonomy_confidence(burdock, high).
taxonomy_source(burdock, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(collard_green, 'Brassica oleracea var. viridis').
genus(collard_green, brassica).
family(collard_green, brassicaceae).
taxonomy_confidence(collard_green, high).
taxonomy_source(collard_green, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(napa_cabbage, 'Brassica rapa subsp. pekinensis').
genus(napa_cabbage, brassica).
family(napa_cabbage, brassicaceae).
taxonomy_confidence(napa_cabbage, high).
taxonomy_source(napa_cabbage, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(tatsoi, 'Brassica rapa subsp. narinosa').
genus(tatsoi, brassica).
family(tatsoi, brassicaceae).
taxonomy_confidence(tatsoi, high).
taxonomy_source(tatsoi, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(mizuna, 'Brassica rapa var. nipposinica').
genus(mizuna, brassica).
family(mizuna, brassicaceae).
taxonomy_confidence(mizuna, high).
taxonomy_source(mizuna, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(komatsuna, 'Brassica rapa var. perviridis').
genus(komatsuna, brassica).
family(komatsuna, brassicaceae).
taxonomy_confidence(komatsuna, high).
taxonomy_source(komatsuna, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(endive, 'Cichorium endivia').
genus(endive, cichorium).
family(endive, asteraceae).
taxonomy_confidence(endive, high).
taxonomy_source(endive, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(escarole, 'Cichorium endivia var. latifolium').
genus(escarole, cichorium).
family(escarole, asteraceae).
taxonomy_confidence(escarole, high).
taxonomy_source(escarole, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(radicchio, 'Cichorium intybus').
genus(radicchio, cichorium).
family(radicchio, asteraceae).
taxonomy_confidence(radicchio, medium).
taxonomy_source(radicchio, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(radicchio, 'Radicchio is a cultivated type of Cichorium intybus.').

accepted_scientific_name(watercress, 'Nasturtium officinale').
genus(watercress, nasturtium).
family(watercress, brassicaceae).
taxonomy_confidence(watercress, high).
taxonomy_source(watercress, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(malabar_spinach, 'Basella alba').
genus(malabar_spinach, basella).
family(malabar_spinach, basellaceae).
taxonomy_confidence(malabar_spinach, high).
taxonomy_source(malabar_spinach, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(new_zealand_spinach, 'Tetragonia tetragonioides').
genus(new_zealand_spinach, tetragonia).
family(new_zealand_spinach, aizoaceae).
taxonomy_confidence(new_zealand_spinach, high).
taxonomy_source(new_zealand_spinach, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(moringa, 'Moringa oleifera').
genus(moringa, moringa).
family(moringa, moringaceae).
taxonomy_confidence(moringa, high).
taxonomy_source(moringa, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(purslane, 'Portulaca oleracea').
genus(purslane, portulaca).
family(purslane, portulacaceae).
taxonomy_confidence(purslane, high).
taxonomy_source(purslane, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(tomatillo, 'Physalis philadelphica').
genus(tomatillo, physalis).
family(tomatillo, solanaceae).
taxonomy_confidence(tomatillo, high).
taxonomy_source(tomatillo, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(ground_cherry, 'Physalis pruinosa').
genus(ground_cherry, physalis).
family(ground_cherry, solanaceae).
taxonomy_confidence(ground_cherry, medium).
taxonomy_source(ground_cherry, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(ground_cherry, 'Ground cherry common name can refer to multiple Physalis species.').

accepted_scientific_name(bitter_melon, 'Momordica charantia').
genus(bitter_melon, momordica).
family(bitter_melon, cucurbitaceae).
taxonomy_confidence(bitter_melon, high).
taxonomy_source(bitter_melon, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(chayote, 'Sechium edule').
genus(chayote, sechium).
family(chayote, cucurbitaceae).
taxonomy_confidence(chayote, high).
taxonomy_source(chayote, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(loofah, 'Luffa aegyptiaca').
genus(loofah, luffa).
family(loofah, cucurbitaceae).
taxonomy_confidence(loofah, high).
taxonomy_source(loofah, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(snake_gourd, 'Trichosanthes cucumerina').
genus(snake_gourd, trichosanthes).
family(snake_gourd, cucurbitaceae).
taxonomy_confidence(snake_gourd, high).
taxonomy_source(snake_gourd, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(ash_gourd, 'Benincasa hispida').
genus(ash_gourd, benincasa).
family(ash_gourd, cucurbitaceae).
taxonomy_confidence(ash_gourd, high).
taxonomy_source(ash_gourd, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(winter_melon, 'Benincasa hispida').
genus(winter_melon, benincasa).
family(winter_melon, cucurbitaceae).
taxonomy_confidence(winter_melon, high).
taxonomy_source(winter_melon, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(cape_gooseberry, 'Physalis peruviana').
genus(cape_gooseberry, physalis).
family(cape_gooseberry, solanaceae).
taxonomy_confidence(cape_gooseberry, high).
taxonomy_source(cape_gooseberry, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(apple, 'Malus domestica').
genus(apple, malus).
family(apple, rosaceae).
taxonomy_confidence(apple, high).
taxonomy_source(apple, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(pear, 'Pyrus communis').
genus(pear, pyrus).
family(pear, rosaceae).
taxonomy_confidence(pear, high).
taxonomy_source(pear, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(peach, 'Prunus persica').
genus(peach, prunus).
family(peach, rosaceae).
taxonomy_confidence(peach, high).
taxonomy_source(peach, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(plum, 'Prunus domestica').
genus(plum, prunus).
family(plum, rosaceae).
taxonomy_confidence(plum, medium).
taxonomy_source(plum, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(plum, 'Common cultivated plum may also refer to other Prunus species.').

accepted_scientific_name(cherry, 'Prunus avium').
genus(cherry, prunus).
family(cherry, rosaceae).
taxonomy_confidence(cherry, medium).
taxonomy_source(cherry, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(cherry, 'Common name cherry is broad; sweet cherry used here.').

accepted_scientific_name(apricot, 'Prunus armeniaca').
genus(apricot, prunus).
family(apricot, rosaceae).
taxonomy_confidence(apricot, high).
taxonomy_source(apricot, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(fig, 'Ficus carica').
genus(fig, ficus).
family(fig, moraceae).
taxonomy_confidence(fig, high).
taxonomy_source(fig, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(pomegranate, 'Punica granatum').
genus(pomegranate, punica).
family(pomegranate, lythraceae).
taxonomy_confidence(pomegranate, high).
taxonomy_source(pomegranate, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(lemon, 'Citrus limon').
genus(lemon, citrus).
family(lemon, rutaceae).
taxonomy_confidence(lemon, high).
taxonomy_source(lemon, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(lime, 'Citrus aurantiifolia').
genus(lime, citrus).
family(lime, rutaceae).
taxonomy_confidence(lime, medium).
taxonomy_source(lime, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(lime, 'Lime common name can refer to multiple Citrus species.').

accepted_scientific_name(orange, 'Citrus sinensis').
genus(orange, citrus).
family(orange, rutaceae).
taxonomy_confidence(orange, high).
taxonomy_source(orange, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(mandarin, 'Citrus reticulata').
genus(mandarin, citrus).
family(mandarin, rutaceae).
taxonomy_confidence(mandarin, high).
taxonomy_source(mandarin, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(banana, 'Musa acuminata').
genus(banana, musa).
family(banana, musaceae).
taxonomy_confidence(banana, medium).
taxonomy_source(banana, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(banana, 'Edible bananas are often hybrids/cultivar groups; genus-level matching is safer.').

accepted_scientific_name(papaya, 'Carica papaya').
genus(papaya, carica).
family(papaya, caricaceae).
taxonomy_confidence(papaya, high).
taxonomy_source(papaya, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(pineapple, 'Ananas comosus').
genus(pineapple, ananas).
family(pineapple, bromeliaceae).
taxonomy_confidence(pineapple, high).
taxonomy_source(pineapple, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(mango, 'Mangifera indica').
genus(mango, mangifera).
family(mango, anacardiaceae).
taxonomy_confidence(mango, high).
taxonomy_source(mango, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(avocado, 'Persea americana').
genus(avocado, persea).
family(avocado, lauraceae).
taxonomy_confidence(avocado, high).
taxonomy_source(avocado, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(guava, 'Psidium guajava').
genus(guava, psidium).
family(guava, myrtaceae).
taxonomy_confidence(guava, high).
taxonomy_source(guava, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(passion_fruit, 'Passiflora edulis').
genus(passion_fruit, passiflora).
family(passion_fruit, passifloraceae).
taxonomy_confidence(passion_fruit, high).
taxonomy_source(passion_fruit, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(dragon_fruit, 'Selenicereus undatus').
genus(dragon_fruit, selenicereus).
family(dragon_fruit, cactaceae).
taxonomy_confidence(dragon_fruit, medium).
taxonomy_source(dragon_fruit, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(dragon_fruit, 'Dragon fruit may refer to several Selenicereus/Hylocereus species.').

accepted_scientific_name(kiwi, 'Actinidia deliciosa').
genus(kiwi, actinidia).
family(kiwi, actinidiaceae).
taxonomy_confidence(kiwi, medium).
taxonomy_source(kiwi, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(kiwi, 'Kiwi can refer to multiple Actinidia species; common kiwifruit used here.').

accepted_scientific_name(gooseberry, 'Ribes uva-crispa').
genus(gooseberry, ribes).
family(gooseberry, grossulariaceae).
taxonomy_confidence(gooseberry, high).
taxonomy_source(gooseberry, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(currant, 'Ribes spp.').
genus(currant, ribes).
family(currant, grossulariaceae).
taxonomy_confidence(currant, medium).
taxonomy_source(currant, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(currant, 'Currant common name is broad; genus-level matching recommended.').

accepted_scientific_name(cranberry, 'Vaccinium macrocarpon').
genus(cranberry, vaccinium).
family(cranberry, ericaceae).
taxonomy_confidence(cranberry, high).
taxonomy_source(cranberry, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(marjoram, 'Origanum majorana').
genus(marjoram, origanum).
family(marjoram, lamiaceae).
taxonomy_confidence(marjoram, high).
taxonomy_source(marjoram, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(lovage, 'Levisticum officinale').
genus(lovage, levisticum).
family(lovage, apiaceae).
taxonomy_confidence(lovage, high).
taxonomy_source(lovage, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(chervil, 'Anthriscus cerefolium').
genus(chervil, anthriscus).
family(chervil, apiaceae).
taxonomy_confidence(chervil, high).
taxonomy_source(chervil, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(sorrel, 'Rumex acetosa').
genus(sorrel, rumex).
family(sorrel, polygonaceae).
taxonomy_confidence(sorrel, medium).
taxonomy_source(sorrel, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(sorrel, 'Sorrel common name may refer to several Rumex species.').

accepted_scientific_name(stevia, 'Stevia rebaudiana').
genus(stevia, stevia).
family(stevia, asteraceae).
taxonomy_confidence(stevia, high).
taxonomy_source(stevia, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(epazote, 'Dysphania ambrosioides').
genus(epazote, dysphania).
family(epazote, amaranthaceae).
taxonomy_confidence(epazote, high).
taxonomy_source(epazote, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(shiso, 'Perilla frutescens').
genus(shiso, perilla).
family(shiso, lamiaceae).
taxonomy_confidence(shiso, high).
taxonomy_source(shiso, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(thai_basil, 'Ocimum basilicum var. thyrsiflora').
genus(thai_basil, ocimum).
family(thai_basil, lamiaceae).
taxonomy_confidence(thai_basil, medium).
taxonomy_source(thai_basil, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(thai_basil, 'Thai basil is commonly treated as a cultivar/type of Ocimum basilicum.').

accepted_scientific_name(holy_basil, 'Ocimum tenuiflorum').
genus(holy_basil, ocimum).
family(holy_basil, lamiaceae).
taxonomy_confidence(holy_basil, high).
taxonomy_source(holy_basil, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(vietnamese_coriander, 'Persicaria odorata').
genus(vietnamese_coriander, persicaria).
family(vietnamese_coriander, polygonaceae).
taxonomy_confidence(vietnamese_coriander, high).
taxonomy_source(vietnamese_coriander, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(curry_leaf, 'Murraya koenigii').
genus(curry_leaf, murraya).
family(curry_leaf, rutaceae).
taxonomy_confidence(curry_leaf, high).
taxonomy_source(curry_leaf, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(bay_laurel, 'Laurus nobilis').
genus(bay_laurel, laurus).
family(bay_laurel, lauraceae).
taxonomy_confidence(bay_laurel, high).
taxonomy_source(bay_laurel, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(pandan, 'Pandanus amaryllifolius').
genus(pandan, pandanus).
family(pandan, pandanaceae).
taxonomy_confidence(pandan, high).
taxonomy_source(pandan, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(coriander_seed, 'Coriandrum sativum').
genus(coriander_seed, coriandrum).
family(coriander_seed, apiaceae).
taxonomy_confidence(coriander_seed, high).
taxonomy_source(coriander_seed, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(coriander_seed, 'Same species as cilantro; seed/spice form kept as separate atom if needed.').

accepted_scientific_name(cumin, 'Cuminum cyminum').
genus(cumin, cuminum).
family(cumin, apiaceae).
taxonomy_confidence(cumin, high).
taxonomy_source(cumin, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(anise, 'Pimpinella anisum').
genus(anise, pimpinella).
family(anise, apiaceae).
taxonomy_confidence(anise, high).
taxonomy_source(anise, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(star_anise, 'Illicium verum').
genus(star_anise, illicium).
family(star_anise, schisandraceae).
taxonomy_confidence(star_anise, high).
taxonomy_source(star_anise, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(cardamom, 'Elettaria cardamomum').
genus(cardamom, elettaria).
family(cardamom, zingiberaceae).
taxonomy_confidence(cardamom, high).
taxonomy_source(cardamom, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(clove, 'Syzygium aromaticum').
genus(clove, syzygium).
family(clove, myrtaceae).
taxonomy_confidence(clove, high).
taxonomy_source(clove, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(vanilla, 'Vanilla planifolia').
genus(vanilla, vanilla).
family(vanilla, orchidaceae).
taxonomy_confidence(vanilla, high).
taxonomy_source(vanilla, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(saffron, 'Crocus sativus').
genus(saffron, crocus).
family(saffron, iridaceae).
taxonomy_confidence(saffron, high).
taxonomy_source(saffron, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(mustard, 'Brassica juncea').
genus(mustard, brassica).
family(mustard, brassicaceae).
taxonomy_confidence(mustard, medium).
taxonomy_source(mustard, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(mustard, 'Mustard as spice/green can refer to several Brassica/Sinapis species.').

accepted_scientific_name(fenugreek, 'Trigonella foenum-graecum').
genus(fenugreek, trigonella).
family(fenugreek, fabaceae).
taxonomy_confidence(fenugreek, high).
taxonomy_source(fenugreek, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(allspice, 'Pimenta dioica').
genus(allspice, pimenta).
family(allspice, myrtaceae).
taxonomy_confidence(allspice, high).
taxonomy_source(allspice, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(mace, 'Myristica fragrans').
genus(mace, myristica).
family(mace, myristicaceae).
taxonomy_confidence(mace, high).
taxonomy_source(mace, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(mace, 'Mace and nutmeg come from the same species.').

accepted_scientific_name(marigold, 'Tagetes spp.').
genus(marigold, tagetes).
family(marigold, asteraceae).
taxonomy_confidence(marigold, medium).
taxonomy_source(marigold, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(marigold, 'Common name marigold is broad; genus-level matching recommended.').

accepted_scientific_name(french_marigold, 'Tagetes patula').
genus(french_marigold, tagetes).
family(french_marigold, asteraceae).
taxonomy_confidence(french_marigold, high).
taxonomy_source(french_marigold, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(african_marigold, 'Tagetes erecta').
genus(african_marigold, tagetes).
family(african_marigold, asteraceae).
taxonomy_confidence(african_marigold, high).
taxonomy_source(african_marigold, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(sweet_alyssum, 'Lobularia maritima').
genus(sweet_alyssum, lobularia).
family(sweet_alyssum, brassicaceae).
taxonomy_confidence(sweet_alyssum, high).
taxonomy_source(sweet_alyssum, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(echinacea, 'Echinacea purpurea').
genus(echinacea, echinacea).
family(echinacea, asteraceae).
taxonomy_confidence(echinacea, high).
taxonomy_source(echinacea, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(pansy, 'Viola x wittrockiana').
genus(pansy, viola).
family(pansy, violaceae).
taxonomy_confidence(pansy, medium).
taxonomy_source(pansy, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(pansy, 'Cultivated pansies are hybrid/cultivar groups; genus-level matching recommended.').

accepted_scientific_name(snapdragon, 'Antirrhinum majus').
genus(snapdragon, antirrhinum).
family(snapdragon, plantaginaceae).
taxonomy_confidence(snapdragon, high).
taxonomy_source(snapdragon, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(petunia, 'Petunia x atkinsiana').
genus(petunia, petunia).
family(petunia, solanaceae).
taxonomy_confidence(petunia, medium).
taxonomy_source(petunia, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(petunia, 'Garden petunias are commonly hybrid cultivars.').

accepted_scientific_name(zinnia, 'Zinnia elegans').
genus(zinnia, zinnia).
family(zinnia, asteraceae).
taxonomy_confidence(zinnia, high).
taxonomy_source(zinnia, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(cosmos, 'Cosmos bipinnatus').
genus(cosmos, cosmos).
family(cosmos, asteraceae).
taxonomy_confidence(cosmos, high).
taxonomy_source(cosmos, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(dahlia, 'Dahlia pinnata').
genus(dahlia, dahlia).
family(dahlia, asteraceae).
taxonomy_confidence(dahlia, medium).
taxonomy_source(dahlia, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(dahlia, 'Dahlia garden forms may be hybrids; genus-level matching recommended.').

accepted_scientific_name(hollyhock, 'Alcea rosea').
genus(hollyhock, alcea).
family(hollyhock, malvaceae).
taxonomy_confidence(hollyhock, high).
taxonomy_source(hollyhock, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(foxglove, 'Digitalis purpurea').
genus(foxglove, digitalis).
family(foxglove, plantaginaceae).
taxonomy_confidence(foxglove, high).
taxonomy_source(foxglove, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(foxglove, 'Ornamental and medicinal plant; toxic if ingested.').

accepted_scientific_name(lupine, 'Lupinus spp.').
genus(lupine, lupinus).
family(lupine, fabaceae).
taxonomy_confidence(lupine, medium).
taxonomy_source(lupine, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(lupine, 'Common name lupine is broad; some species are toxic and some are crop lupins.').

accepted_scientific_name(begonia, 'Begonia spp.').
genus(begonia, begonia).
family(begonia, begoniaceae).
taxonomy_confidence(begonia, medium).
taxonomy_source(begonia, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(begonia, 'Common name refers to a large genus; species/cultivar should be confirmed.').

accepted_scientific_name(impatiens, 'Impatiens walleriana').
genus(impatiens, impatiens).
family(impatiens, balsaminaceae).
taxonomy_confidence(impatiens, medium).
taxonomy_source(impatiens, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(impatiens, 'Common bedding impatiens used here; confirm species from API when possible.').

accepted_scientific_name(coleus, 'Coleus scutellarioides').
genus(coleus, coleus).
family(coleus, lamiaceae).
taxonomy_confidence(coleus, high).
taxonomy_source(coleus, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(geranium_bedding, 'Pelargonium x hortorum').
genus(geranium_bedding, pelargonium).
family(geranium_bedding, geraniaceae).
taxonomy_confidence(geranium_bedding, medium).
taxonomy_source(geranium_bedding, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(geranium_bedding, 'Bedding geranium is usually Pelargonium, not true Geranium.').

accepted_scientific_name(true_geranium, 'Geranium spp.').
genus(true_geranium, geranium).
family(true_geranium, geraniaceae).
taxonomy_confidence(true_geranium, medium).
taxonomy_source(true_geranium, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(true_geranium, 'Use this only for true geranium/cranesbill, not bedding Pelargonium.').

accepted_scientific_name(daisy, 'Bellis perennis').
genus(daisy, bellis).
family(daisy, asteraceae).
taxonomy_confidence(daisy, medium).
taxonomy_source(daisy, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(daisy, 'Common name daisy is broad; lawn/English daisy used here.').

accepted_scientific_name(lavender_cotton, 'Santolina chamaecyparissus').
genus(lavender_cotton, santolina).
family(lavender_cotton, asteraceae).
taxonomy_confidence(lavender_cotton, high).
taxonomy_source(lavender_cotton, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(bachelor_button, 'Centaurea cyanus').
genus(bachelor_button, centaurea).
family(bachelor_button, asteraceae).
taxonomy_confidence(bachelor_button, high).
taxonomy_source(bachelor_button, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(globe_amaranth, 'Gomphrena globosa').
genus(globe_amaranth, gomphrena).
family(globe_amaranth, amaranthaceae).
taxonomy_confidence(globe_amaranth, high).
taxonomy_source(globe_amaranth, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(strawflower, 'Xerochrysum bracteatum').
genus(strawflower, xerochrysum).
family(strawflower, asteraceae).
taxonomy_confidence(strawflower, high).
taxonomy_source(strawflower, 'Kew POWO / USDA PLANTS / WFO cross-check').

accepted_scientific_name(statice, 'Limonium sinuatum').
genus(statice, limonium).
family(statice, plumbaginaceae).
taxonomy_confidence(statice, medium).
taxonomy_source(statice, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(statice, 'Annual statice commonly refers to Limonium sinuatum.').

accepted_scientific_name(flowering_tobacco, 'Nicotiana alata').
genus(flowering_tobacco, nicotiana).
family(flowering_tobacco, solanaceae).
taxonomy_confidence(flowering_tobacco, medium).
taxonomy_source(flowering_tobacco, 'Kew POWO / USDA PLANTS / WFO cross-check').
taxonomy_note(flowering_tobacco, 'Common ornamental tobacco may refer to several Nicotiana species.').

accepted_scientific_name(moss_rose, 'Portulaca grandiflora').
genus(moss_rose, portulaca).
family(moss_rose, portulacaceae).
taxonomy_confidence(moss_rose, high).
taxonomy_source(moss_rose, 'Kew POWO / USDA PLANTS / WFO cross-check').


% =========================================================
% AUTO-GENERATED FROM NORMALIZED PLANT PROFILES: plant_taxonomy
% Review before editing manually.
% =========================================================

accepted_scientific_name(gotu_kola, 'Centella asiatica').
alternate_scientific_name(gotu_kola, 'Hydrocotyle asiatica').
genus(gotu_kola, centella).
family(gotu_kola, apiaceae).
taxonomy_confidence(gotu_kola, high).
taxonomy_source(gotu_kola, 'GBIF / Plants For A Future').
