% FILE: logic_companion_planting/data/disease_fact.pl
%
% PURPOSE:
% This file contains facts related to plant diseases within the Smart Farming System's
% companion planting logic. It defines various diseases, their host plants, symptoms,
% and recommended treatments. This knowledge base helps in identifying plant health issues
% and suggesting appropriate interventions, potentially influencing companion planting advice.
%
% PREDICATES DEFINED:
% - disease(DiseaseName, HostPlantOrFamily, Type): Declares a disease, its primary host, and type (e.g., fungal, pest).
% - symptom(DiseaseName, Symptom): Associates a specific symptom with a disease.
% - treatment(DiseaseName, TreatmentAction, Confidence): Recommends a treatment for a disease with a confidence level.
% - disease_host_treatment(DiseaseName, HostPlantOrFamily, TreatmentAction): A specific format for RHS-sourced data.
%
% RELATED MODULES:
% - `plant_fact.pl`: Provides the canonical list of plant names that can be hosts.
% - `rules/companion_rules.pl`: Utilizes these facts for inference regarding disease prevention and management.
%
% USAGE:
% This file is consulted by the reasoning engine to diagnose plant diseases, understand
% their characteristics, and propose solutions, which can then be integrated into
% companion planting strategies (e.g., recommending plants that deter certain diseases).
%

% =========================================================
% DISEASE FACTS
% Auto-organized by plant_data_bank_scripts/scripts/prolog/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% APHIDS
% ---------------------------------------------------------
disease(aphids, general, pest).
symptom(aphids, curled_leaves).
symptom(aphids, sticky_residue).
treatment(aphids, insecticidal_soap, high).
treatment(aphids, introduce_ladybugs, high).
treatment(aphids, spray_water, medium).

% ---------------------------------------------------------
% APPLE SCAB
% ---------------------------------------------------------
disease_host_treatment(apple_scab, apple, prune_out_infected_shoots_in_winter).
disease_host_treatment(apple_scab, cotoneaster, remove_and_dispose_of_fallen_leaves).

% ---------------------------------------------------------
% BLIGHT
% ---------------------------------------------------------
disease(blight, tomato, fungal).
symptom(blight, brown_spots).
symptom(blight, rapid_leaf_decay).
treatment(blight, crop_rotation, high).
treatment(blight, remove_infected_plants, high).

% ---------------------------------------------------------
% BOX BLIGHT
% ---------------------------------------------------------
disease_host_treatment(box_blight, buxus, prune_only_in_dry_weather_and_clean_tools).

% ---------------------------------------------------------
% BOX TREE CATERPILLAR
% ---------------------------------------------------------
disease_host_treatment(box_tree_caterpillar, buxus, apply_biological_control_bacillus_thuringiensis).

% ---------------------------------------------------------
% CONIFERS PESTALOTIOPSIS DISEASE
% ---------------------------------------------------------
disease(conifers_pestalotiopsis_disease, conifers_pestalotiopsis, fungal).
symptom(conifers_pestalotiopsis_disease, dieback).
symptom(conifers_pestalotiopsis_disease, leaf_spots).
symptom(conifers_pestalotiopsis_disease, rot).
symptom(conifers_pestalotiopsis_disease, yellow_leaves).
treatment(conifers_pestalotiopsis_disease, adjust_watering, medium).
treatment(conifers_pestalotiopsis_disease, remove_infected_parts, medium).
treatment(conifers_pestalotiopsis_disease, sanitize_tools, medium).

% ---------------------------------------------------------
% DOWNY MILDEW
% ---------------------------------------------------------
disease(downy_mildew, multiple_plants, fungal).
symptom(downy_mildew, grey_underside_growth).
symptom(downy_mildew, yellow_patches).
treatment(downy_mildew, avoid_overwatering, high).
treatment(downy_mildew, fungicide, medium).
treatment(downy_mildew, improve_airflow, high).

% ---------------------------------------------------------
% DUTCH ELM DISEASE
% ---------------------------------------------------------
disease(dutch_elm_disease, dutch_elm, fungal).
symptom(dutch_elm_disease, dieback).
symptom(dutch_elm_disease, rot).
symptom(dutch_elm_disease, wilting).
symptom(dutch_elm_disease, yellow_leaves).
treatment(dutch_elm_disease, adjust_watering, medium).
treatment(dutch_elm_disease, remove_infected_parts, medium).
treatment(dutch_elm_disease, sanitize_tools, medium).

% ---------------------------------------------------------
% GRAPEVINE DISEASES
% ---------------------------------------------------------
disease(grapevine_diseases, grapevine, fungal).
symptom(grapevine_diseases, fungal_growth).
symptom(grapevine_diseases, rot).
symptom(grapevine_diseases, stunted_growth).
symptom(grapevine_diseases, white_powder).
symptom(grapevine_diseases, wilting).
symptom(grapevine_diseases, yellow_leaves).
treatment(grapevine_diseases, adjust_watering, medium).
treatment(grapevine_diseases, improve_air_circulation, medium).
treatment(grapevine_diseases, remove_infected_parts, medium).
treatment(grapevine_diseases, sanitize_tools, medium).

% ---------------------------------------------------------
% HONEY FUNGUS
% ---------------------------------------------------------
disease_host_treatment(honey_fungus, apple, remove_stumps_and_woody_debris).
disease_host_treatment(honey_fungus, lilac, remove_infected_plants_and_stumps).
disease_host_treatment(honey_fungus, privet, remove_infected_plants_and_stumps).
disease_host_treatment(honey_fungus, viburnum, replace_soil_or_use_physical_barriers).

% ---------------------------------------------------------
% IRIS DISEASES
% ---------------------------------------------------------
disease(iris_diseases, iris, fungal).
symptom(iris_diseases, leaf_spots).
symptom(iris_diseases, rot).
symptom(iris_diseases, stunted_growth).
symptom(iris_diseases, yellow_leaves).
treatment(iris_diseases, adjust_watering, medium).
treatment(iris_diseases, remove_infected_parts, medium).
treatment(iris_diseases, sanitize_tools, medium).

% ---------------------------------------------------------
% LAUREL LEAF DISEASES
% ---------------------------------------------------------
disease(laurel_leaf_diseases, laurel, fungal).
symptom(laurel_leaf_diseases, brown_spots).
symptom(laurel_leaf_diseases, leaf_spots).
symptom(laurel_leaf_diseases, rot).
symptom(laurel_leaf_diseases, white_powder).
symptom(laurel_leaf_diseases, yellow_leaves).
treatment(laurel_leaf_diseases, adjust_watering, medium).
treatment(laurel_leaf_diseases, remove_infected_parts, medium).
treatment(laurel_leaf_diseases, sanitize_tools, medium).

% ---------------------------------------------------------
% LAWN RUST DISEASE
% ---------------------------------------------------------
disease(lawn_rust_disease, lawn, fungal).
symptom(lawn_rust_disease, fungal_growth).
symptom(lawn_rust_disease, yellow_leaves).
treatment(lawn_rust_disease, adjust_watering, medium).
treatment(lawn_rust_disease, improve_air_circulation, medium).

% ---------------------------------------------------------
% LILY DISEASES
% ---------------------------------------------------------
disease(lily_diseases, lily, fungal).
symptom(lily_diseases, brown_spots).
symptom(lily_diseases, fungal_growth).
symptom(lily_diseases, rot).
symptom(lily_diseases, stunted_growth).
symptom(lily_diseases, yellow_leaves).
treatment(lily_diseases, adjust_watering, medium).
treatment(lily_diseases, remove_infected_parts, medium).

% ---------------------------------------------------------
% PEAR RUST
% ---------------------------------------------------------
disease_host_treatment(pear_rust, juniper, remove_alternate_host_nearby_if_possible).
disease_host_treatment(pear_rust, pear, remove_affected_leaves_in_summer).

% ---------------------------------------------------------
% PEAR SCAB
% ---------------------------------------------------------
disease_host_treatment(pear_scab, pear, prune_out_infected_shoots_in_winter).

% ---------------------------------------------------------
% PHYTOPHTHORA ROOT ROT
% ---------------------------------------------------------
disease_host_treatment(phytophthora_root_rot, rhododendron, improve_soil_drainage_and_aeration).
disease_host_treatment(phytophthora_root_rot, yew, avoid_overwatering_and_piling_mulch_on_stems).

% ---------------------------------------------------------
% PLANT VIRUS
% ---------------------------------------------------------
disease_host_treatment(plant_virus, dahlia, dispose_of_heavily_infected_plants).

% ---------------------------------------------------------
% POWDERY MILDEW
% ---------------------------------------------------------
disease(powdery_mildew, multiple_plants, fungal).
symptom(powdery_mildew, leaf_distortion).
symptom(powdery_mildew, white_powder).
treatment(powdery_mildew, fungicide, medium).
treatment(powdery_mildew, improve_air_circulation, high).
treatment(powdery_mildew, reduce_humidity, high).
treatment(powdery_mildew, remove_infected_leaves, high).
disease_host_treatment(powdery_mildew, phlox, avoid_drought_stress_by_watering).
disease_host_treatment(powdery_mildew, prunus, improve_air_ventilation_and_spacing).

% ---------------------------------------------------------
% RHODODENDRON DISEASES
% ---------------------------------------------------------
disease(rhododendron_diseases, rhododendron, fungal).
symptom(rhododendron_diseases, dieback).
symptom(rhododendron_diseases, leaf_spots).
symptom(rhododendron_diseases, rot).
symptom(rhododendron_diseases, white_powder).
symptom(rhododendron_diseases, wilting).
symptom(rhododendron_diseases, yellow_leaves).
treatment(rhododendron_diseases, adjust_watering, medium).
treatment(rhododendron_diseases, remove_infected_parts, medium).
treatment(rhododendron_diseases, sanitize_tools, medium).

% ---------------------------------------------------------
% ROBINIA PSEUDOACACIA FRISIA PROBLEMS
% ---------------------------------------------------------
disease(robinia_pseudoacacia_frisia_problems, robinia_pseudoacacia_frisia_problems, fungal).
symptom(robinia_pseudoacacia_frisia_problems, brown_spots).
symptom(robinia_pseudoacacia_frisia_problems, dieback).
symptom(robinia_pseudoacacia_frisia_problems, rot).
symptom(robinia_pseudoacacia_frisia_problems, wilting).
symptom(robinia_pseudoacacia_frisia_problems, yellow_leaves).
treatment(robinia_pseudoacacia_frisia_problems, adjust_watering, medium).
treatment(robinia_pseudoacacia_frisia_problems, remove_infected_parts, medium).
treatment(robinia_pseudoacacia_frisia_problems, sanitize_tools, medium).

% ---------------------------------------------------------
% ROOT ROT
% ---------------------------------------------------------
disease(root_rot, multiple_plants, fungal).
symptom(root_rot, brown_roots).
symptom(root_rot, wilting).
treatment(root_rot, improve_drainage, high).
treatment(root_rot, reduce_watering, high).
treatment(root_rot, remove_rotten_roots, medium).

% ---------------------------------------------------------
% ROSE BLACK SPOT
% ---------------------------------------------------------
disease_host_treatment(rose_black_spot, rose, apply_thick_winter_mulch).
disease_host_treatment(rose_black_spot, rose, clear_up_and_dispose_of_fallen_leaves).

% ---------------------------------------------------------
% RUST DISEASES
% ---------------------------------------------------------
disease(rust_diseases, multiple_plants, fungal).
symptom(rust_diseases, brown_spots).
symptom(rust_diseases, leaf_spots).
symptom(rust_diseases, yellow_leaves).
treatment(rust_diseases, adjust_watering, medium).
treatment(rust_diseases, remove_infected_parts, medium).
treatment(rust_diseases, sanitize_tools, medium).

% ---------------------------------------------------------
% SCLEROTINIA DISEASE
% ---------------------------------------------------------
disease(sclerotinia_disease, sclerotinia, fungal).
symptom(sclerotinia_disease, fungal_growth).
symptom(sclerotinia_disease, leaf_spots).
symptom(sclerotinia_disease, rot).
symptom(sclerotinia_disease, wilting).
symptom(sclerotinia_disease, yellow_leaves).
treatment(sclerotinia_disease, adjust_watering, medium).
treatment(sclerotinia_disease, remove_infected_parts, medium).
treatment(sclerotinia_disease, sanitize_tools, medium).

% ---------------------------------------------------------
% SHRUBBY VERONICA HEBE LEAF DISEASES
% ---------------------------------------------------------
disease(shrubby_veronica_hebe_leaf_diseases, shrubby_veronica_hebe, fungal).
symptom(shrubby_veronica_hebe_leaf_diseases, dieback).
symptom(shrubby_veronica_hebe_leaf_diseases, fungal_growth).
symptom(shrubby_veronica_hebe_leaf_diseases, leaf_spots).
symptom(shrubby_veronica_hebe_leaf_diseases, white_powder).
symptom(shrubby_veronica_hebe_leaf_diseases, wilting).
symptom(shrubby_veronica_hebe_leaf_diseases, yellow_leaves).
treatment(shrubby_veronica_hebe_leaf_diseases, adjust_watering, medium).
treatment(shrubby_veronica_hebe_leaf_diseases, improve_air_circulation, medium).
treatment(shrubby_veronica_hebe_leaf_diseases, remove_infected_parts, medium).
treatment(shrubby_veronica_hebe_leaf_diseases, sanitize_tools, medium).

% ---------------------------------------------------------
% TREES AND SHRUBS SCAB DISEASES
% ---------------------------------------------------------
disease(trees_and_shrubs_scab_diseases, trees_and_shrubs, fungal).
symptom(trees_and_shrubs_scab_diseases, dieback).
symptom(trees_and_shrubs_scab_diseases, leaf_spots).
symptom(trees_and_shrubs_scab_diseases, yellow_leaves).
treatment(trees_and_shrubs_scab_diseases, adjust_watering, medium).
treatment(trees_and_shrubs_scab_diseases, improve_air_circulation, medium).
treatment(trees_and_shrubs_scab_diseases, remove_infected_parts, medium).
treatment(trees_and_shrubs_scab_diseases, sanitize_tools, medium).

% ---------------------------------------------------------
% TULIP FIRE
% ---------------------------------------------------------
disease_host_treatment(tulip_fire, tulip, dispose_of_infected_bulbs_and_foliage).

% ---------------------------------------------------------
% VINE WEEVIL
% ---------------------------------------------------------
disease_host_treatment(vine_weevil, cyclamen, apply_parasitic_nematodes_to_soil).


% =========================================================
% UNGROUPED / NON-PLANT FACTS
% =========================================================

:- discontiguous disease/3.
:- discontiguous symptom/2.
:- discontiguous treatment/3.
