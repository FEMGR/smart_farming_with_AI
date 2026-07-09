% FILE: logic_companion_planting/data/insect_fact.pl
%
% PURPOSE:
% This file defines facts related to insect interactions within the Smart Farming System's
% companion planting logic. It categorizes insects as pests or beneficial organisms
% and details their relationships with plants, including pest attacks, beneficial predation,
% parasitic control, and pollination activities.
%
% PREDICATES DEFINED:
% - attacks(Pest, Plant): Indicates that a specific pest attacks a particular plant.
% - eats(BeneficialInsect, Pest): Describes a beneficial insect preying on a pest.
% - parasitizes(Parasite, Host): Details a parasitic relationship between an insect and a host.
% - pollinates(Pollinator, Plant): Identifies insects that pollinate specific plants.
%
% RELATED MODULES:
% - `plant_fact.pl`: Provides the canonical list of plant names referenced in this file.
% - `companion_fact.pl`: May use these insect interactions to infer companion planting relationships.
% - `rules/companion_rules.pl`: Utilizes these facts for inference regarding pest control and pollination.
%
% USAGE:
% This file is consulted by the reasoning engine to understand the ecological roles of various
% insects and their direct impact on plants, informing companion planting recommendations.
%
% =========================================================
% INSECT FACTS
% Auto-organized by plant_data_bank_scripts/scripts/prolog/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% APHID
% ---------------------------------------------------------
pest(aphid).
pest_type(aphid, insect).
pest_scientific_name(aphid, aphis_gossypii).
pest_scientific_name(aphid, macrosiphum_euphorbiae).
pest_scientific_name(aphid, myzus_persicae).
pest_included_species(aphid, green_peach_aphid, myzus_persicae).
pest_included_species(aphid, melon_aphid, aphis_gossypii).
pest_included_species(aphid, potato_aphid, macrosiphum_euphorbiae).
attacks(aphid, artichoke).
attacks(aphid, asparagus).
attacks(aphid, bean).
attacks(aphid, beet).
attacks(aphid, bell_pepper).
attacks(aphid, broccoli).
attacks(aphid, brussels_sprout).
attacks(aphid, cabbage).
attacks(aphid, cantaloupe).
attacks(aphid, carrot).
attacks(aphid, cauliflower).
attacks(aphid, celery).
attacks(aphid, chili_pepper).
attacks(aphid, collard).
attacks(aphid, corn).
attacks(aphid, cucumber).
attacks(aphid, dill).
attacks(aphid, eggplant).
attacks(aphid, endive).
attacks(aphid, escarole).
attacks(aphid, horseradish).
attacks(aphid, kale).
attacks(aphid, kohlrabi).
attacks(aphid, lentil).
attacks(aphid, lettuce).
attacks(aphid, lima_bean).
attacks(aphid, melon).
attacks(aphid, muskmelon).
attacks(aphid, mustard_green).
attacks(aphid, parsley).
attacks(aphid, parsnip).
attacks(aphid, pea).
attacks(aphid, pepper).
attacks(aphid, pumpkin).
attacks(aphid, radish).
attacks(aphid, rutabaga).
attacks(aphid, salsify).
attacks(aphid, spinach).
attacks(aphid, squash).
attacks(aphid, sweet_corn).
attacks(aphid, sweet_potato).
attacks(aphid, swiss_chard).
attacks(aphid, tomato).
attacks(aphid, turnip).
attacks(aphid, watercress).
attacks(aphid, watermelon).
damage_symptom(aphid, disease_vector).
damage_symptom(aphid, distortion).
damage_symptom(aphid, fruit_damage).
damage_symptom(aphid, honeydew).
damage_symptom(aphid, leaf_curling).
damage_symptom(aphid, leaf_damage).
damage_symptom(aphid, necrosis).
damage_symptom(aphid, pod_damage).
damage_symptom(aphid, sooty_mold).
damage_symptom(aphid, stem_damage).
damage_symptom(aphid, stunting).
damage_symptom(aphid, virus_vector).
damage_symptom(aphid, wilting).
damage_symptom(aphid, yellowing).
pest_source(aphid, pnw_insect_management_handbook).
pest_source_url(aphid, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-aphid').

% ---------------------------------------------------------
% ARMYWORM
% ---------------------------------------------------------
pest(armyworm).
pest_type(armyworm, insect).
pest_scientific_name(armyworm, mamestra_configurata).
pest_scientific_name(armyworm, spodoptera_exigua).
pest_scientific_name(armyworm, spodoptera_praefica).
pest_included_species(armyworm, beet_armyworm, spodoptera_exigua).
pest_included_species(armyworm, bertha_armyworm, mamestra_configurata).
pest_included_species(armyworm, western_yellowstriped_armyworm, spodoptera_praefica).
attacks(armyworm, asparagus).
attacks(armyworm, bean).
attacks(armyworm, beet).
attacks(armyworm, bell_pepper).
attacks(armyworm, broccoli).
attacks(armyworm, brussels_sprout).
attacks(armyworm, cabbage).
attacks(armyworm, cantaloupe).
attacks(armyworm, carrot).
attacks(armyworm, cauliflower).
attacks(armyworm, chili_pepper).
attacks(armyworm, collard).
attacks(armyworm, corn).
attacks(armyworm, garlic).
attacks(armyworm, kale).
attacks(armyworm, kohlrabi).
attacks(armyworm, lettuce).
attacks(armyworm, melon).
attacks(armyworm, muskmelon).
attacks(armyworm, mustard_green).
attacks(armyworm, onion).
attacks(armyworm, parsley).
attacks(armyworm, parsnip).
attacks(armyworm, pea).
attacks(armyworm, pepper).
attacks(armyworm, radish).
attacks(armyworm, rhubarb).
attacks(armyworm, salsify).
attacks(armyworm, spinach).
attacks(armyworm, sweet_corn).
attacks(armyworm, swiss_chard).
attacks(armyworm, tomato).
attacks(armyworm, watermelon).
damage_symptom(armyworm, feeding_damage).
damage_symptom(armyworm, feeding_holes).
damage_symptom(armyworm, leaf_damage).
damage_symptom(armyworm, leaf_mining).
damage_symptom(armyworm, seedling_damage).
damage_symptom(armyworm, yellowing).
pest_source(armyworm, pnw_insect_management_handbook).
pest_source_url(armyworm, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-armyworm').

% ---------------------------------------------------------
% ARTICHOKE PLUME MOTH
% ---------------------------------------------------------
pest(artichoke_plume_moth).
pest_type(artichoke_plume_moth, insect).
attacks(artichoke_plume_moth, artichoke).
damage_symptom(artichoke_plume_moth, yellowing).
pest_source(artichoke_plume_moth, pnw_insect_management_handbook).

% ---------------------------------------------------------
% ASPARAGUS BEETLE
% ---------------------------------------------------------
pest(asparagus_beetle).
pest_type(asparagus_beetle, insect).
attacks(asparagus_beetle, asparagus).
damage_symptom(asparagus_beetle, feeding_damage).
damage_symptom(asparagus_beetle, leaf_damage).
damage_symptom(asparagus_beetle, stem_damage).
damage_symptom(asparagus_beetle, yellowing).
pest_source(asparagus_beetle, pnw_insect_management_handbook).

% ---------------------------------------------------------
% BEET ARMYWORM
% ---------------------------------------------------------
pest(beet_armyworm).
pest_type(beet_armyworm, insect).
attacks(beet_armyworm, endive).
attacks(beet_armyworm, escarole).
damage_symptom(beet_armyworm, leaf_damage).
pest_source(beet_armyworm, pnw_insect_management_handbook).

% ---------------------------------------------------------
% BLISTER BEETLE
% ---------------------------------------------------------
pest(blister_beetle).
pest_type(blister_beetle, insect).
attacks(blister_beetle, beet).
attacks(blister_beetle, swiss_chard).
damage_symptom(blister_beetle, defoliation).
damage_symptom(blister_beetle, feeding_damage).
damage_symptom(blister_beetle, yellowing).
pest_source(blister_beetle, pnw_insect_management_handbook).

% ---------------------------------------------------------
% BROWN WHEAT MITE
% ---------------------------------------------------------
pest(brown_wheat_mite).
pest_type(brown_wheat_mite, mite).
attacks(brown_wheat_mite, onion).
damage_symptom(brown_wheat_mite, feeding_damage).
damage_symptom(brown_wheat_mite, leaf_damage).
damage_symptom(brown_wheat_mite, silvering).
pest_source(brown_wheat_mite, pnw_insect_management_handbook).

% ---------------------------------------------------------
% BULB MITE
% ---------------------------------------------------------
pest(bulb_mite).
pest_type(bulb_mite, mite).
attacks(bulb_mite, garlic).
attacks(bulb_mite, onion).
damage_symptom(bulb_mite, root_damage).
pest_source(bulb_mite, pnw_insect_management_handbook).

% ---------------------------------------------------------
% BUMBLEBEE
% ---------------------------------------------------------
pollinates(bumblebee, pepper).
pollinates(bumblebee, tomato).

% ---------------------------------------------------------
% CABBAGE FLEA BEETLE
% ---------------------------------------------------------
pest(cabbage_flea_beetle).
pest_type(cabbage_flea_beetle, insect).
attacks(cabbage_flea_beetle, horseradish).
pest_source(cabbage_flea_beetle, pnw_insect_management_handbook).

% ---------------------------------------------------------
% CABBAGE MAGGOT
% ---------------------------------------------------------
pest(cabbage_maggot).
pest_type(cabbage_maggot, insect).
attacks(cabbage_maggot, broccoli).
attacks(cabbage_maggot, brussels_sprout).
attacks(cabbage_maggot, cabbage).
attacks(cabbage_maggot, cauliflower).
attacks(cabbage_maggot, collard).
attacks(cabbage_maggot, kale).
attacks(cabbage_maggot, kohlrabi).
attacks(cabbage_maggot, mustard_green).
attacks(cabbage_maggot, radish).
attacks(cabbage_maggot, rutabaga).
attacks(cabbage_maggot, turnip).
damage_symptom(cabbage_maggot, feeding_damage).
damage_symptom(cabbage_maggot, root_damage).
damage_symptom(cabbage_maggot, stem_damage).
pest_source(cabbage_maggot, pnw_insect_management_handbook).
pest_source_url(cabbage_maggot, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-cabbage-maggot').

% ---------------------------------------------------------
% CABBAGE WORM
% ---------------------------------------------------------
attacks(cabbage_worm, broccoli).
attacks(cabbage_worm, cabbage).

% ---------------------------------------------------------
% CARROT RUST FLY
% ---------------------------------------------------------
pest(carrot_rust_fly).
pest_type(carrot_rust_fly, insect).
attacks(carrot_rust_fly, carrot).
attacks(carrot_rust_fly, celery).
attacks(carrot_rust_fly, parsnip).
damage_symptom(carrot_rust_fly, leaf_damage).
damage_symptom(carrot_rust_fly, root_damage).
damage_symptom(carrot_rust_fly, stunting).
damage_symptom(carrot_rust_fly, wilting).
damage_symptom(carrot_rust_fly, yellowing).
pest_source(carrot_rust_fly, pnw_insect_management_handbook).
pest_source_url(carrot_rust_fly, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-carrot-rust-fly').

% ---------------------------------------------------------
% COLLEMBOLA
% ---------------------------------------------------------
pest(collembola).
pest_type(collembola, springtail).
attacks(collembola, spinach).
damage_symptom(collembola, root_damage).
pest_source(collembola, pnw_insect_management_handbook).

% ---------------------------------------------------------
% COLORADO POTATO BEETLE
% ---------------------------------------------------------
pest(colorado_potato_beetle).
pest_type(colorado_potato_beetle, insect).
attacks(colorado_potato_beetle, eggplant).
attacks(colorado_potato_beetle, tomato).
damage_symptom(colorado_potato_beetle, yellowing).
pest_source(colorado_potato_beetle, pnw_insect_management_handbook).
pest_source_url(colorado_potato_beetle, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-colorado-potato-beetle').

% ---------------------------------------------------------
% CORN EARWORM
% ---------------------------------------------------------
pest(corn_earworm).
pest_type(corn_earworm, insect).
attacks(corn_earworm, bean).
attacks(corn_earworm, corn).
attacks(corn_earworm, lima_bean).
attacks(corn_earworm, sweet_corn).
attacks(corn_earworm, tomato).
damage_symptom(corn_earworm, feeding_damage).
damage_symptom(corn_earworm, fruit_damage).
damage_symptom(corn_earworm, leaf_damage).
damage_symptom(corn_earworm, yellowing).
pest_source(corn_earworm, pnw_insect_management_handbook).
pest_source_url(corn_earworm, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-corn-earworm').

% ---------------------------------------------------------
% CORN ROOTWORM
% ---------------------------------------------------------
pest(corn_rootworm).
pest_type(corn_rootworm, insect).
attacks(corn_rootworm, corn).
attacks(corn_rootworm, sweet_corn).
damage_symptom(corn_rootworm, feeding_holes).
damage_symptom(corn_rootworm, leaf_damage).
damage_symptom(corn_rootworm, root_damage).
damage_symptom(corn_rootworm, seedling_damage).
damage_symptom(corn_rootworm, stem_damage).
damage_symptom(corn_rootworm, yellowing).
pest_source(corn_rootworm, pnw_insect_management_handbook).

% ---------------------------------------------------------
% CUCUMBER BEETLE
% ---------------------------------------------------------
pest(cucumber_beetle).
pest_type(cucumber_beetle, insect).
pest_scientific_name(cucumber_beetle, acalymma_trivittatum).
pest_scientific_name(cucumber_beetle, diabrotica_undecimpunctata).
attacks(cucumber_beetle, bean).
attacks(cucumber_beetle, beet).
attacks(cucumber_beetle, cantaloupe).
attacks(cucumber_beetle, cucumber).
attacks(cucumber_beetle, kohlrabi).
attacks(cucumber_beetle, lettuce).
attacks(cucumber_beetle, melon).
attacks(cucumber_beetle, muskmelon).
attacks(cucumber_beetle, mustard_green).
attacks(cucumber_beetle, pumpkin).
attacks(cucumber_beetle, spinach).
attacks(cucumber_beetle, squash).
attacks(cucumber_beetle, swiss_chard).
attacks(cucumber_beetle, watermelon).
damage_symptom(cucumber_beetle, feeding_holes).
damage_symptom(cucumber_beetle, leaf_damage).
damage_symptom(cucumber_beetle, root_damage).
damage_symptom(cucumber_beetle, stem_damage).
damage_symptom(cucumber_beetle, yellowing).
pest_source(cucumber_beetle, pnw_insect_management_handbook).
pest_source_url(cucumber_beetle, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-cucumber-beetle').

% ---------------------------------------------------------
% CUTWORM
% ---------------------------------------------------------
pest(cutworm).
pest_type(cutworm, insect).
pest_scientific_name(cutworm, agotis_ipsilon).
pest_scientific_name(cutworm, peridroma_saucia).
pest_included_species(cutworm, unknown, agotis_ipsilon).
pest_included_species(cutworm, unknown, peridroma_saucia).
attacks(cutworm, artichoke).
attacks(cutworm, asparagus).
attacks(cutworm, bean).
attacks(cutworm, beet).
attacks(cutworm, bell_pepper).
attacks(cutworm, broccoli).
attacks(cutworm, brussels_sprout).
attacks(cutworm, cabbage).
attacks(cutworm, cantaloupe).
attacks(cutworm, carrot).
attacks(cutworm, cauliflower).
attacks(cutworm, chili_pepper).
attacks(cutworm, collard).
attacks(cutworm, corn).
attacks(cutworm, cucumber).
attacks(cutworm, garlic).
attacks(cutworm, horseradish).
attacks(cutworm, kale).
attacks(cutworm, kohlrabi).
attacks(cutworm, lettuce).
attacks(cutworm, melon).
attacks(cutworm, muskmelon).
attacks(cutworm, mustard_green).
attacks(cutworm, onion).
attacks(cutworm, parsley).
attacks(cutworm, parsnip).
attacks(cutworm, pea).
attacks(cutworm, pepper).
attacks(cutworm, radish).
attacks(cutworm, rhubarb).
attacks(cutworm, spinach).
attacks(cutworm, sweet_corn).
attacks(cutworm, swiss_chard).
attacks(cutworm, tomato).
attacks(cutworm, watermelon).
damage_symptom(cutworm, feeding_damage).
damage_symptom(cutworm, feeding_holes).
damage_symptom(cutworm, leaf_damage).
damage_symptom(cutworm, seedling_damage).
pest_source(cutworm, pnw_insect_management_handbook).
pest_source_url(cutworm, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-cutworm').

% ---------------------------------------------------------
% DELPHASTUS BEETLE
% ---------------------------------------------------------
eats(delphastus_beetle, whitefly).

% ---------------------------------------------------------
% DIAMONDBACK MOTH
% ---------------------------------------------------------
pest(diamondback_moth).
pest_type(diamondback_moth, insect).
attacks(diamondback_moth, broccoli).
attacks(diamondback_moth, brussels_sprout).
attacks(diamondback_moth, cabbage).
attacks(diamondback_moth, cauliflower).
attacks(diamondback_moth, collard).
attacks(diamondback_moth, horseradish).
attacks(diamondback_moth, kale).
attacks(diamondback_moth, kohlrabi).
attacks(diamondback_moth, mustard_green).
attacks(diamondback_moth, radish).
attacks(diamondback_moth, rutabaga).
attacks(diamondback_moth, turnip).
damage_symptom(diamondback_moth, feeding_damage).
damage_symptom(diamondback_moth, feeding_holes).
damage_symptom(diamondback_moth, leaf_damage).
damage_symptom(diamondback_moth, stem_damage).
pest_source(diamondback_moth, pnw_insect_management_handbook).
pest_source_url(diamondback_moth, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-diamondback-moth').

% ---------------------------------------------------------
% ENCARSIA FORMOSA
% ---------------------------------------------------------
parasitizes(encarsia_formosa, whitefly).

% ---------------------------------------------------------
% EUROPEAN CRANEFLY
% ---------------------------------------------------------
pest(european_cranefly).
pest_type(european_cranefly, insect).
attacks(european_cranefly, spinach).
damage_symptom(european_cranefly, seedling_damage).
pest_source(european_cranefly, pnw_insect_management_handbook).

% ---------------------------------------------------------
% EUROPEAN EARWIG
% ---------------------------------------------------------
pest(european_earwig).
pest_type(european_earwig, insect).
attacks(european_earwig, celery).
attacks(european_earwig, lettuce).
damage_symptom(european_earwig, feeding_holes).
damage_symptom(european_earwig, leaf_damage).
pest_source(european_earwig, pnw_insect_management_handbook).
pest_source_url(european_earwig, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-european-earwig').

% ---------------------------------------------------------
% FLEA BEETLE
% ---------------------------------------------------------
pest(flea_beetle).
pest_type(flea_beetle, insect).
pest_scientific_name(flea_beetle, epitrix).
pest_scientific_name(flea_beetle, phyllotreta_cruciferae).
pest_included_species(flea_beetle, unknown, epitrix).
pest_included_species(flea_beetle, unknown, phyllotreta_cruciferae).
attacks(flea_beetle, beet).
attacks(flea_beetle, bell_pepper).
attacks(flea_beetle, broccoli).
attacks(flea_beetle, brussels_sprout).
attacks(flea_beetle, cabbage).
attacks(flea_beetle, cauliflower).
attacks(flea_beetle, chili_pepper).
attacks(flea_beetle, collard).
attacks(flea_beetle, eggplant).
attacks(flea_beetle, kale).
attacks(flea_beetle, kohlrabi).
attacks(flea_beetle, mustard_green).
attacks(flea_beetle, parsnip).
attacks(flea_beetle, pepper).
attacks(flea_beetle, radish).
attacks(flea_beetle, rutabaga).
attacks(flea_beetle, swiss_chard).
attacks(flea_beetle, tomato).
attacks(flea_beetle, turnip).
attacks(flea_beetle, watercress).
damage_symptom(flea_beetle, disease_vector).
damage_symptom(flea_beetle, feeding_damage).
damage_symptom(flea_beetle, feeding_holes).
damage_symptom(flea_beetle, leaf_damage).
damage_symptom(flea_beetle, seedling_damage).
pest_source(flea_beetle, pnw_insect_management_handbook).
pest_source_url(flea_beetle, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-flea-beetle').

% ---------------------------------------------------------
% GARDEN SYMPHYLAN
% ---------------------------------------------------------
pest(garden_symphylan).
pest_type(garden_symphylan, symphylan).
attacks(garden_symphylan, asparagus).
attacks(garden_symphylan, bean).
attacks(garden_symphylan, beet).
attacks(garden_symphylan, bell_pepper).
attacks(garden_symphylan, broccoli).
attacks(garden_symphylan, brussels_sprout).
attacks(garden_symphylan, cabbage).
attacks(garden_symphylan, carrot).
attacks(garden_symphylan, cauliflower).
attacks(garden_symphylan, chili_pepper).
attacks(garden_symphylan, corn).
attacks(garden_symphylan, cucumber).
attacks(garden_symphylan, garlic).
attacks(garden_symphylan, pepper).
attacks(garden_symphylan, rhubarb).
attacks(garden_symphylan, spinach).
attacks(garden_symphylan, sweet_corn).
damage_symptom(garden_symphylan, feeding_damage).
damage_symptom(garden_symphylan, leaf_mining).
damage_symptom(garden_symphylan, root_damage).
damage_symptom(garden_symphylan, stunting).
pest_source(garden_symphylan, pnw_insect_management_handbook).
pest_source_url(garden_symphylan, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-garden-symphylan').

% ---------------------------------------------------------
% GRASSHOPPER
% ---------------------------------------------------------
pest(grasshopper).
pest_type(grasshopper, insect).
attacks(grasshopper, bean).
attacks(grasshopper, broccoli).
attacks(grasshopper, brussels_sprout).
attacks(grasshopper, cabbage).
attacks(grasshopper, cantaloupe).
attacks(grasshopper, cauliflower).
attacks(grasshopper, corn).
attacks(grasshopper, cucumber).
attacks(grasshopper, lima_bean).
attacks(grasshopper, melon).
attacks(grasshopper, muskmelon).
attacks(grasshopper, pea).
attacks(grasshopper, sweet_corn).
attacks(grasshopper, watermelon).
damage_symptom(grasshopper, feeding_holes).
damage_symptom(grasshopper, leaf_damage).
pest_source(grasshopper, pnw_insect_management_handbook).
pest_source_url(grasshopper, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-grasshopper').

% ---------------------------------------------------------
% GROUND BEETLE
% ---------------------------------------------------------
eats(ground_beetle, cutworm).

% ---------------------------------------------------------
% HONEYBEE
% ---------------------------------------------------------
pollinates(honeybee, cucumber).
pollinates(honeybee, squash).

% ---------------------------------------------------------
% HOVERFLY
% ---------------------------------------------------------
eats(hoverfly, aphid).
eats(hoverfly, whitefly).
pollinates(hoverfly, strawberry).

% ---------------------------------------------------------
% IMPORTED CABBAGEWORM
% ---------------------------------------------------------
pest(imported_cabbageworm).
pest_type(imported_cabbageworm, insect).
attacks(imported_cabbageworm, broccoli).
attacks(imported_cabbageworm, brussels_sprout).
attacks(imported_cabbageworm, cabbage).
attacks(imported_cabbageworm, cauliflower).
attacks(imported_cabbageworm, collard).
attacks(imported_cabbageworm, horseradish).
attacks(imported_cabbageworm, kale).
attacks(imported_cabbageworm, kohlrabi).
attacks(imported_cabbageworm, mustard_green).
damage_symptom(imported_cabbageworm, feeding_holes).
damage_symptom(imported_cabbageworm, leaf_damage).
damage_symptom(imported_cabbageworm, stem_damage).
damage_symptom(imported_cabbageworm, yellowing).
pest_source(imported_cabbageworm, pnw_insect_management_handbook).
pest_source_url(imported_cabbageworm, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-imported-cabbageworm').

% ---------------------------------------------------------
% LACEWING
% ---------------------------------------------------------
eats(lacewing, aphid).
eats(lacewing, whitefly).

% ---------------------------------------------------------
% LADYBUG
% ---------------------------------------------------------
eats(ladybug, aphid).
eats(ladybug, whitefly).

% ---------------------------------------------------------
% LEAFHOPPER
% ---------------------------------------------------------
pest(leafhopper).
pest_type(leafhopper, insect).
attacks(leafhopper, lima_bean).
attacks(leafhopper, parsnip).
damage_symptom(leafhopper, disease_vector).
damage_symptom(leafhopper, feeding_damage).
damage_symptom(leafhopper, leaf_damage).
damage_symptom(leafhopper, virus_vector).
damage_symptom(leafhopper, yellowing).
pest_source(leafhopper, pnw_insect_management_handbook).
pest_source_url(leafhopper, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-leafhopper').

% ---------------------------------------------------------
% LEAFMINER
% ---------------------------------------------------------
pest(leafminer).
pest_type(leafminer, insect).
attacks(leafminer, beet).
attacks(leafminer, collard).
attacks(leafminer, kale).
attacks(leafminer, onion).
attacks(leafminer, pea).
attacks(leafminer, spinach).
attacks(leafminer, swiss_chard).
damage_symptom(leafminer, feeding_damage).
damage_symptom(leafminer, leaf_damage).
damage_symptom(leafminer, leaf_mining).
damage_symptom(leafminer, seedling_damage).
damage_symptom(leafminer, yellowing).
pest_source(leafminer, pnw_insect_management_handbook).

% ---------------------------------------------------------
% LEPIDOPTERA LARVAE
% ---------------------------------------------------------
pest(lepidoptera_larvae).
pest_type(lepidoptera_larvae, insect).
attacks(lepidoptera_larvae, celery).
attacks(lepidoptera_larvae, watercress).
pest_source(lepidoptera_larvae, pnw_insect_management_handbook).

% ---------------------------------------------------------
% LETTUCE ROOT APHID
% ---------------------------------------------------------
pest(lettuce_root_aphid).
pest_type(lettuce_root_aphid, insect).
attacks(lettuce_root_aphid, lettuce).
damage_symptom(lettuce_root_aphid, root_damage).
pest_source(lettuce_root_aphid, pnw_insect_management_handbook).

% ---------------------------------------------------------
% LIMA BEAN POD BORER
% ---------------------------------------------------------
pest(lima_bean_pod_borer).
pest_type(lima_bean_pod_borer, insect).
attacks(lima_bean_pod_borer, lima_bean).
damage_symptom(lima_bean_pod_borer, pod_damage).
pest_source(lima_bean_pod_borer, pnw_insect_management_handbook).

% ---------------------------------------------------------
% LOOPER
% ---------------------------------------------------------
pest(looper).
pest_type(looper, insect).
pest_scientific_name(looper, autographa_californica).
pest_scientific_name(looper, trichoplusia_ni).
pest_included_species(looper, unknown, autographa_californica).
pest_included_species(looper, unknown, trichoplusia_ni).
attacks(looper, bell_pepper).
attacks(looper, broccoli).
attacks(looper, brussels_sprout).
attacks(looper, cabbage).
attacks(looper, cantaloupe).
attacks(looper, cauliflower).
attacks(looper, chili_pepper).
attacks(looper, collard).
attacks(looper, cucumber).
attacks(looper, endive).
attacks(looper, escarole).
attacks(looper, kale).
attacks(looper, kohlrabi).
attacks(looper, lettuce).
attacks(looper, melon).
attacks(looper, muskmelon).
attacks(looper, mustard_green).
attacks(looper, parsley).
attacks(looper, pea).
attacks(looper, pepper).
attacks(looper, radish).
attacks(looper, rhubarb).
attacks(looper, spinach).
attacks(looper, swiss_chard).
attacks(looper, watermelon).
damage_symptom(looper, defoliation).
damage_symptom(looper, feeding_damage).
damage_symptom(looper, feeding_holes).
damage_symptom(looper, leaf_damage).
damage_symptom(looper, seedling_damage).
damage_symptom(looper, silvering).
pest_source(looper, pnw_insect_management_handbook).
pest_source_url(looper, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-looper').

% ---------------------------------------------------------
% LYGUS BUG
% ---------------------------------------------------------
pest(lygus_bug).
pest_type(lygus_bug, insect).
attacks(lygus_bug, bean).
attacks(lygus_bug, lentil).
attacks(lygus_bug, lima_bean).
attacks(lygus_bug, spinach).
damage_symptom(lygus_bug, leaf_mining).
damage_symptom(lygus_bug, yellowing).
pest_source(lygus_bug, pnw_insect_management_handbook).
pest_source_url(lygus_bug, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-lygus-bug').

% ---------------------------------------------------------
% MEXICAN BEAN BEETLE
% ---------------------------------------------------------
pest(mexican_bean_beetle).
pest_type(mexican_bean_beetle, insect).
attacks(mexican_bean_beetle, bean).
damage_symptom(mexican_bean_beetle, leaf_damage).
damage_symptom(mexican_bean_beetle, pod_damage).
damage_symptom(mexican_bean_beetle, seedling_damage).
damage_symptom(mexican_bean_beetle, stem_damage).
damage_symptom(mexican_bean_beetle, yellowing).
pest_source(mexican_bean_beetle, pnw_insect_management_handbook).

% ---------------------------------------------------------
% NITIDULID BEETLE
% ---------------------------------------------------------
pest(nitidulid_beetle).
pest_type(nitidulid_beetle, insect).
attacks(nitidulid_beetle, bean).
attacks(nitidulid_beetle, pumpkin).
attacks(nitidulid_beetle, squash).
pest_source(nitidulid_beetle, pnw_insect_management_handbook).

% ---------------------------------------------------------
% ONION MAGGOT
% ---------------------------------------------------------
pest(onion_maggot).
pest_type(onion_maggot, insect).
attacks(onion_maggot, onion).
damage_symptom(onion_maggot, feeding_damage).
damage_symptom(onion_maggot, leaf_damage).
damage_symptom(onion_maggot, root_damage).
damage_symptom(onion_maggot, seedling_damage).
damage_symptom(onion_maggot, stem_damage).
damage_symptom(onion_maggot, yellowing).
pest_source(onion_maggot, pnw_insect_management_handbook).

% ---------------------------------------------------------
% PAINTED LADY BUTTERFLY
% ---------------------------------------------------------
pest(painted_lady_butterfly).
pest_type(painted_lady_butterfly, insect).
attacks(painted_lady_butterfly, artichoke).
damage_symptom(painted_lady_butterfly, yellowing).
pest_source(painted_lady_butterfly, pnw_insect_management_handbook).

% ---------------------------------------------------------
% PARASITIC WASP
% ---------------------------------------------------------
parasitizes(parasitic_wasp, caterpillar).

% ---------------------------------------------------------
% PEA LEAF WEEVIL
% ---------------------------------------------------------
pest(pea_leaf_weevil).
pest_type(pea_leaf_weevil, insect).
attacks(pea_leaf_weevil, bean).
attacks(pea_leaf_weevil, pea).
damage_symptom(pea_leaf_weevil, feeding_damage).
damage_symptom(pea_leaf_weevil, leaf_damage).
damage_symptom(pea_leaf_weevil, root_damage).
damage_symptom(pea_leaf_weevil, seedling_damage).
pest_source(pea_leaf_weevil, pnw_insect_management_handbook).

% ---------------------------------------------------------
% PEA MOTH
% ---------------------------------------------------------
pest(pea_moth).
pest_type(pea_moth, insect).
attacks(pea_moth, pea).
damage_symptom(pea_moth, feeding_damage).
damage_symptom(pea_moth, pod_damage).
damage_symptom(pea_moth, yellowing).
pest_source(pea_moth, pnw_insect_management_handbook).

% ---------------------------------------------------------
% PEA WEEVIL
% ---------------------------------------------------------
pest(pea_weevil).
pest_type(pea_weevil, insect).
attacks(pea_weevil, pea).
damage_symptom(pea_weevil, pod_damage).
pest_source(pea_weevil, pnw_insect_management_handbook).

% ---------------------------------------------------------
% PLANT BUG
% ---------------------------------------------------------
pest(plant_bug).
pest_type(plant_bug, insect).
attacks(plant_bug, bean).
damage_symptom(plant_bug, leaf_damage).
damage_symptom(plant_bug, yellowing).
pest_source(plant_bug, pnw_insect_management_handbook).

% ---------------------------------------------------------
% PRAYING MANTIS
% ---------------------------------------------------------
eats(praying_mantis, grasshopper).

% ---------------------------------------------------------
% SEEDCORN MAGGOT
% ---------------------------------------------------------
pest(seedcorn_maggot).
pest_type(seedcorn_maggot, insect).
attacks(seedcorn_maggot, bean).
attacks(seedcorn_maggot, corn).
attacks(seedcorn_maggot, cucumber).
attacks(seedcorn_maggot, lentil).
attacks(seedcorn_maggot, lima_bean).
attacks(seedcorn_maggot, onion).
attacks(seedcorn_maggot, pea).
attacks(seedcorn_maggot, pumpkin).
attacks(seedcorn_maggot, squash).
attacks(seedcorn_maggot, sweet_corn).
damage_symptom(seedcorn_maggot, feeding_damage).
damage_symptom(seedcorn_maggot, fruit_damage).
damage_symptom(seedcorn_maggot, leaf_damage).
damage_symptom(seedcorn_maggot, root_damage).
damage_symptom(seedcorn_maggot, seedling_damage).
damage_symptom(seedcorn_maggot, stem_damage).
damage_symptom(seedcorn_maggot, yellowing).
pest_source(seedcorn_maggot, pnw_insect_management_handbook).
pest_source_url(seedcorn_maggot, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-seedcorn-maggot').

% ---------------------------------------------------------
% SIXSPOTTED LEAFHOPPER
% ---------------------------------------------------------
pest(sixspotted_leafhopper).
pest_type(sixspotted_leafhopper, insect).
attacks(sixspotted_leafhopper, carrot).
damage_symptom(sixspotted_leafhopper, feeding_damage).
damage_symptom(sixspotted_leafhopper, leaf_damage).
damage_symptom(sixspotted_leafhopper, root_damage).
damage_symptom(sixspotted_leafhopper, yellowing).
pest_source(sixspotted_leafhopper, pnw_insect_management_handbook).

% ---------------------------------------------------------
% SLUG
% ---------------------------------------------------------
pest(slug).
pest_type(slug, mollusk).
pest_scientific_name(slug, arion).
pest_scientific_name(slug, derocerus_laeve).
pest_scientific_name(slug, derocerus_reticulatum).
pest_scientific_name(slug, limax_maximus).
pest_scientific_name(slug, milax_gagates).
pest_scientific_name(slug, prophysaon_andersoni).
pest_included_species(slug, unknown, arion).
pest_included_species(slug, unknown, derocerus_laeve).
pest_included_species(slug, unknown, derocerus_reticulatum).
pest_included_species(slug, unknown, limax_maximus).
pest_included_species(slug, unknown, milax_gagates).
pest_included_species(slug, unknown, prophysaon_andersoni).
attacks(slug, artichoke).
attacks(slug, bean).
attacks(slug, beet).
attacks(slug, broccoli).
attacks(slug, brussels_sprout).
attacks(slug, cabbage).
attacks(slug, carrot).
attacks(slug, cauliflower).
attacks(slug, celery).
attacks(slug, corn).
attacks(slug, cucumber).
attacks(slug, lettuce).
attacks(slug, lima_bean).
attacks(slug, pumpkin).
attacks(slug, rhubarb).
attacks(slug, squash).
attacks(slug, sweet_corn).
damage_symptom(slug, leaf_damage).
damage_symptom(slug, root_damage).
pest_source(slug, pnw_insect_management_handbook).
pest_source_url(slug, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-slug').

% ---------------------------------------------------------
% SPIDER MITE
% ---------------------------------------------------------
pest(spider_mite).
pest_type(spider_mite, mite).
pest_scientific_name(spider_mite, tetranychus_pacificus).
pest_scientific_name(spider_mite, tetranychus_turkestani).
pest_scientific_name(spider_mite, tetranychus_urticae).
pest_included_species(spider_mite, unknown, tetranychus_pacificus).
pest_included_species(spider_mite, unknown, tetranychus_turkestani).
pest_included_species(spider_mite, unknown, tetranychus_urticae).
attacks(spider_mite, bean).
attacks(spider_mite, beet).
attacks(spider_mite, bell_pepper).
attacks(spider_mite, cantaloupe).
attacks(spider_mite, chili_pepper).
attacks(spider_mite, corn).
attacks(spider_mite, cucumber).
attacks(spider_mite, eggplant).
attacks(spider_mite, lima_bean).
attacks(spider_mite, melon).
attacks(spider_mite, muskmelon).
attacks(spider_mite, pepper).
attacks(spider_mite, pumpkin).
attacks(spider_mite, squash).
attacks(spider_mite, sweet_corn).
attacks(spider_mite, sweet_potato).
attacks(spider_mite, tomato).
attacks(spider_mite, watermelon).
damage_symptom(spider_mite, leaf_damage).
damage_symptom(spider_mite, webbing).
damage_symptom(spider_mite, wilting).
pest_source(spider_mite, pnw_insect_management_handbook).
pest_source_url(spider_mite, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-spider-mite').

% ---------------------------------------------------------
% SPOTTED ASPARAGUS BEETLE
% ---------------------------------------------------------
pest(spotted_asparagus_beetle).
pest_type(spotted_asparagus_beetle, insect).
attacks(spotted_asparagus_beetle, asparagus).
damage_symptom(spotted_asparagus_beetle, yellowing).
pest_source(spotted_asparagus_beetle, pnw_insect_management_handbook).

% ---------------------------------------------------------
% SPRINGTAIL
% ---------------------------------------------------------
pest(springtail).
pest_type(springtail, springtail).
attacks(springtail, spinach).
damage_symptom(springtail, root_damage).
pest_source(springtail, pnw_insect_management_handbook).

% ---------------------------------------------------------
% SQUASH BUG
% ---------------------------------------------------------
pest(squash_bug).
pest_type(squash_bug, insect).
attacks(squash_bug, cantaloupe).
attacks(squash_bug, cucumber).
attacks(squash_bug, melon).
attacks(squash_bug, muskmelon).
attacks(squash_bug, pumpkin).
attacks(squash_bug, squash).
attacks(squash_bug, watermelon).
damage_symptom(squash_bug, fruit_damage).
damage_symptom(squash_bug, leaf_damage).
damage_symptom(squash_bug, stem_damage).
damage_symptom(squash_bug, wilting).
damage_symptom(squash_bug, yellowing).
pest_source(squash_bug, pnw_insect_management_handbook).
pest_source_url(squash_bug, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-squash-bug').

% ---------------------------------------------------------
% STINK BUG
% ---------------------------------------------------------
pest(stink_bug).
pest_type(stink_bug, insect).
attacks(stink_bug, bean).
damage_symptom(stink_bug, leaf_damage).
damage_symptom(stink_bug, yellowing).
pest_source(stink_bug, pnw_insect_management_handbook).

% ---------------------------------------------------------
% THISTLE BUTTERFLY
% ---------------------------------------------------------
pest(thistle_butterfly).
pest_type(thistle_butterfly, insect).
attacks(thistle_butterfly, artichoke).
damage_symptom(thistle_butterfly, yellowing).
pest_source(thistle_butterfly, pnw_insect_management_handbook).

% ---------------------------------------------------------
% THRIPS
% ---------------------------------------------------------
pest(thrips).
pest_type(thrips, insect).
pest_scientific_name(thrips, frankliniella_williamsi).
pest_included_species(thrips, unknown, frankliniella_williamsi).
attacks(thrips, bean).
attacks(thrips, broccoli).
attacks(thrips, brussels_sprout).
attacks(thrips, cabbage).
attacks(thrips, cauliflower).
attacks(thrips, corn).
attacks(thrips, cucumber).
attacks(thrips, garlic).
attacks(thrips, leek).
attacks(thrips, onion).
attacks(thrips, pea).
attacks(thrips, pepper).
attacks(thrips, shallot).
attacks(thrips, sweet_corn).
damage_symptom(thrips, feeding_damage).
damage_symptom(thrips, leaf_damage).
damage_symptom(thrips, stunting).
damage_symptom(thrips, virus_vector).
damage_symptom(thrips, wilting).
damage_symptom(thrips, yellowing).
pest_source(thrips, pnw_insect_management_handbook).
pest_source_url(thrips, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-thrips').

% ---------------------------------------------------------
% TOMATO FRUITWORM
% ---------------------------------------------------------
pest(tomato_fruitworm).
pest_type(tomato_fruitworm, insect).
attacks(tomato_fruitworm, tomato).
damage_symptom(tomato_fruitworm, fruit_damage).
damage_symptom(tomato_fruitworm, leaf_damage).
damage_symptom(tomato_fruitworm, yellowing).
pest_source(tomato_fruitworm, pnw_insect_management_handbook).

% ---------------------------------------------------------
% TOMATO HORNWORM
% ---------------------------------------------------------
pest(tomato_hornworm).
pest_type(tomato_hornworm, insect).
attacks(tomato_hornworm, tomato).
damage_symptom(tomato_hornworm, fruit_damage).
damage_symptom(tomato_hornworm, leaf_damage).
damage_symptom(tomato_hornworm, yellowing).
pest_source(tomato_hornworm, pnw_insect_management_handbook).

% ---------------------------------------------------------
% WESTERN BEAN CUTWORM
% ---------------------------------------------------------
pest(western_bean_cutworm).
pest_type(western_bean_cutworm, insect).
attacks(western_bean_cutworm, bean).
attacks(western_bean_cutworm, corn).
attacks(western_bean_cutworm, sweet_corn).
pest_source(western_bean_cutworm, pnw_insect_management_handbook).
pest_source_url(western_bean_cutworm, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-western-bean-cutworm').

% ---------------------------------------------------------
% WESTERN YELLOWSTRIPED ARMYWORM
% ---------------------------------------------------------
pest(western_yellowstriped_armyworm).
pest_type(western_yellowstriped_armyworm, insect).
attacks(western_yellowstriped_armyworm, lentil).
pest_source(western_yellowstriped_armyworm, pnw_insect_management_handbook).

% ---------------------------------------------------------
% WHITEFLY
% ---------------------------------------------------------
pest(whitefly).
pest_type(whitefly, insect).
attacks(whitefly, bell_pepper).
attacks(whitefly, chili_pepper).
attacks(whitefly, cucumber).
attacks(whitefly, eggplant).
attacks(whitefly, pepper).
attacks(whitefly, tomato).
damage_symptom(whitefly, honeydew).
damage_symptom(whitefly, leaf_damage).
damage_symptom(whitefly, sooty_mold).
damage_symptom(whitefly, stunting).
damage_symptom(whitefly, wilting).
damage_symptom(whitefly, yellowing).
pest_source(whitefly, pnw_insect_management_handbook).
pest_source_url(whitefly, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-whitefly').

% ---------------------------------------------------------
% WIREWORM
% ---------------------------------------------------------
pest(wireworm).
pest_type(wireworm, insect).
attacks(wireworm, asparagus).
attacks(wireworm, bean).
attacks(wireworm, beet).
attacks(wireworm, bell_pepper).
attacks(wireworm, broccoli).
attacks(wireworm, brussels_sprout).
attacks(wireworm, cabbage).
attacks(wireworm, cantaloupe).
attacks(wireworm, carrot).
attacks(wireworm, cauliflower).
attacks(wireworm, chili_pepper).
attacks(wireworm, collard).
attacks(wireworm, corn).
attacks(wireworm, cucumber).
attacks(wireworm, eggplant).
attacks(wireworm, endive).
attacks(wireworm, escarole).
attacks(wireworm, garlic).
attacks(wireworm, horseradish).
attacks(wireworm, kale).
attacks(wireworm, kohlrabi).
attacks(wireworm, lettuce).
attacks(wireworm, lima_bean).
attacks(wireworm, melon).
attacks(wireworm, muskmelon).
attacks(wireworm, mustard_green).
attacks(wireworm, onion).
attacks(wireworm, pea).
attacks(wireworm, pepper).
attacks(wireworm, pumpkin).
attacks(wireworm, radish).
attacks(wireworm, rutabaga).
attacks(wireworm, salsify).
attacks(wireworm, spinach).
attacks(wireworm, squash).
attacks(wireworm, sweet_corn).
attacks(wireworm, sweet_potato).
attacks(wireworm, swiss_chard).
attacks(wireworm, tomato).
attacks(wireworm, turnip).
attacks(wireworm, watermelon).
damage_symptom(wireworm, feeding_damage).
damage_symptom(wireworm, root_damage).
damage_symptom(wireworm, seedling_damage).
damage_symptom(wireworm, stem_damage).
damage_symptom(wireworm, wilting).
damage_symptom(wireworm, yellowing).
pest_source(wireworm, pnw_insect_management_handbook).
pest_source_url(wireworm, 'https://pnwhandbooks.org/insect/vegetable/vegetable-pests/common-vegetable/vegetable-crop-wireworm').
