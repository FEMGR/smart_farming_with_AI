
#logic_companion_planting/data/insect_fact.pl

% -----------------------------
% DISEASE KNOWLEDGE BASE
% -----------------------------

% =========================
% POWDERY MILDEW
% =========================
disease(powdery_mildew, multiple_plants, fungal).
symptom(powdery_mildew, white_powder).
symptom(powdery_mildew, leaf_distortion).
treatment(powdery_mildew, improve_air_circulation, high).
treatment(powdery_mildew, reduce_humidity, high).
treatment(powdery_mildew, remove_infected_leaves, high).
treatment(powdery_mildew, fungicide, medium).

% =========================
% DOWNY MILDEW
% =========================
disease(downy_mildew, multiple_plants, fungal).
symptom(downy_mildew, yellow_patches).
symptom(downy_mildew, grey_underside_growth).
treatment(downy_mildew, improve_airflow, high).
treatment(downy_mildew, avoid_overwatering, high).
treatment(downy_mildew, fungicide, medium).

% =========================
% ROOT ROT
% =========================
disease(root_rot, multiple_plants, fungal).
symptom(root_rot, wilting).
symptom(root_rot, brown_roots).
treatment(root_rot, improve_drainage, high).
treatment(root_rot, reduce_watering, high).
treatment(root_rot, remove_rotten_roots, medium).

% =========================
% RUST_DISEASES
% =========================
disease(rust_diseases, multiple_plants, fungal).
symptom(rust_diseases, yellow_leaves).
symptom(rust_diseases, brown_spots).
symptom(rust_diseases, leaf_spots).
treatment(rust_diseases, adjust_watering, medium).
treatment(rust_diseases, remove_infected_parts, medium).
treatment(rust_diseases, sanitize_tools, medium).

% =========================
% LAUREL_LEAF_DISEASES
% =========================
disease(laurel_leaf_diseases, laurel, fungal).
symptom(laurel_leaf_diseases, white_powder).
symptom(laurel_leaf_diseases, leaf_spots).
symptom(laurel_leaf_diseases, brown_spots).
symptom(laurel_leaf_diseases, rot).
symptom(laurel_leaf_diseases, yellow_leaves).
treatment(laurel_leaf_diseases, adjust_watering, medium).
treatment(laurel_leaf_diseases, remove_infected_parts, medium).
treatment(laurel_leaf_diseases, sanitize_tools, medium).

% =========================
% RHODODENDRON_DISEASES
% =========================
disease(rhododendron_diseases, rhododendron, fungal).
symptom(rhododendron_diseases, leaf_spots).
symptom(rhododendron_diseases, white_powder).
symptom(rhododendron_diseases, dieback).
symptom(rhododendron_diseases, rot).
symptom(rhododendron_diseases, wilting).
symptom(rhododendron_diseases, yellow_leaves).
treatment(rhododendron_diseases, adjust_watering, medium).
treatment(rhododendron_diseases, remove_infected_parts, medium).
treatment(rhododendron_diseases, sanitize_tools, medium).


% =========================
% IRIS_DISEASES
% =========================
disease(iris_diseases, iris, fungal).
symptom(iris_diseases, rot).
symptom(iris_diseases, leaf_spots).
symptom(iris_diseases, stunted_growth).
symptom(iris_diseases, yellow_leaves).
treatment(iris_diseases, adjust_watering, medium).
treatment(iris_diseases, remove_infected_parts, medium).
treatment(iris_diseases, sanitize_tools, medium).

% =========================
% LAWN_RUST_DISEASE
% =========================
disease(lawn_rust_disease, lawn, fungal).
symptom(lawn_rust_disease, fungal_growth).
symptom(lawn_rust_disease, yellow_leaves).
treatment(lawn_rust_disease, adjust_watering, medium).
treatment(lawn_rust_disease, improve_air_circulation, medium).


% =========================
% DUTCH_ELM_DISEASE
% =========================
disease(dutch_elm_disease, dutch_elm, fungal).
symptom(dutch_elm_disease, rot).
symptom(dutch_elm_disease, wilting).
symptom(dutch_elm_disease, yellow_leaves).
symptom(dutch_elm_disease, dieback).
treatment(dutch_elm_disease, adjust_watering, medium).
treatment(dutch_elm_disease, remove_infected_parts, medium).
treatment(dutch_elm_disease, sanitize_tools, medium).



% =========================
% SCLEROTINIA_DISEASE
% =========================
disease(sclerotinia_disease, sclerotinia, fungal).
symptom(sclerotinia_disease, rot).
symptom(sclerotinia_disease, fungal_growth).
symptom(sclerotinia_disease, yellow_leaves).
symptom(sclerotinia_disease, leaf_spots).
symptom(sclerotinia_disease, wilting).
treatment(sclerotinia_disease, adjust_watering, medium).
treatment(sclerotinia_disease, remove_infected_parts, medium).
treatment(sclerotinia_disease, sanitize_tools, medium).

% =========================
% ROBINIA_PSEUDOACACIA_FRISIA_PROBLEMS
% =========================
disease(robinia_pseudoacacia_frisia_problems, robinia_pseudoacacia_frisia_problems, fungal).
symptom(robinia_pseudoacacia_frisia_problems, brown_spots).
symptom(robinia_pseudoacacia_frisia_problems, dieback).
symptom(robinia_pseudoacacia_frisia_problems, rot).
symptom(robinia_pseudoacacia_frisia_problems, wilting).
symptom(robinia_pseudoacacia_frisia_problems, yellow_leaves).
treatment(robinia_pseudoacacia_frisia_problems, adjust_watering, medium).
treatment(robinia_pseudoacacia_frisia_problems, remove_infected_parts, medium).
treatment(robinia_pseudoacacia_frisia_problems, sanitize_tools, medium).

% =========================
% LILY_DISEASES
% =========================
disease(lily_diseases, lily, fungal).
symptom(lily_diseases, rot).
symptom(lily_diseases, brown_spots).
symptom(lily_diseases, fungal_growth).
symptom(lily_diseases, stunted_growth).
symptom(lily_diseases, yellow_leaves).
treatment(lily_diseases, adjust_watering, medium).
treatment(lily_diseases, remove_infected_parts, medium).

% =========================
% CONIFERS_PESTALOTIOPSIS_DISEASE
% =========================
disease(conifers_pestalotiopsis_disease, conifers_pestalotiopsis, fungal).
symptom(conifers_pestalotiopsis_disease, leaf_spots).
symptom(conifers_pestalotiopsis_disease, dieback).
symptom(conifers_pestalotiopsis_disease, rot).
symptom(conifers_pestalotiopsis_disease, yellow_leaves).
treatment(conifers_pestalotiopsis_disease, adjust_watering, medium).
treatment(conifers_pestalotiopsis_disease, remove_infected_parts, medium).
treatment(conifers_pestalotiopsis_disease, sanitize_tools, medium).

% =========================
% SHRUBBY_VERONICA_HEBE_LEAF_DISEASES
% =========================
disease(shrubby_veronica_hebe_leaf_diseases, shrubby_veronica_hebe, fungal).
symptom(shrubby_veronica_hebe_leaf_diseases, fungal_growth).
symptom(shrubby_veronica_hebe_leaf_diseases, white_powder).
symptom(shrubby_veronica_hebe_leaf_diseases, leaf_spots).
symptom(shrubby_veronica_hebe_leaf_diseases, wilting).
symptom(shrubby_veronica_hebe_leaf_diseases, dieback).
symptom(shrubby_veronica_hebe_leaf_diseases, yellow_leaves).
treatment(shrubby_veronica_hebe_leaf_diseases, adjust_watering, medium).
treatment(shrubby_veronica_hebe_leaf_diseases, improve_air_circulation, medium).
treatment(shrubby_veronica_hebe_leaf_diseases, remove_infected_parts, medium).
treatment(shrubby_veronica_hebe_leaf_diseases, sanitize_tools, medium).

% =========================
% GRAPEVINE_DISEASES
% =========================
disease(grapevine_diseases, grapevine, fungal).
symptom(grapevine_diseases, rot).
symptom(grapevine_diseases, white_powder).
symptom(grapevine_diseases, wilting).
symptom(grapevine_diseases, fungal_growth).
symptom(grapevine_diseases, stunted_growth).
symptom(grapevine_diseases, yellow_leaves).
treatment(grapevine_diseases, adjust_watering, medium).
treatment(grapevine_diseases, improve_air_circulation, medium).
treatment(grapevine_diseases, remove_infected_parts, medium).
treatment(grapevine_diseases, sanitize_tools, medium).


% =========================
% TREES_AND_SHRUBS_SCAB_DISEASES
% =========================
disease(trees_and_shrubs_scab_diseases, trees_and_shrubs, fungal).
symptom(trees_and_shrubs_scab_diseases, dieback).
symptom(trees_and_shrubs_scab_diseases, leaf_spots).
symptom(trees_and_shrubs_scab_diseases, yellow_leaves).
treatment(trees_and_shrubs_scab_diseases, adjust_watering, medium).
treatment(trees_and_shrubs_scab_diseases, improve_air_circulation, medium).
treatment(trees_and_shrubs_scab_diseases, remove_infected_parts, medium).
treatment(trees_and_shrubs_scab_diseases, sanitize_tools, medium).


% =========================
% BLIGHT
% =========================
disease(blight, tomato, fungal).
symptom(blight, brown_spots).
symptom(blight, rapid_leaf_decay).
treatment(blight, remove_infected_plants, high).
treatment(blight, crop_rotation, high).



% =========================
% APHIDS
% =========================
disease(aphids, general, pest).
symptom(aphids, sticky_residue).
symptom(aphids, curled_leaves).
treatment(aphids, spray_water, medium).
treatment(aphids, introduce_ladybugs, high).
treatment(aphids, insecticidal_soap, high).



% =========================================================
% RHS DISEASE TREATMENT
% Source: RHS
% Confidence: high
% =========================================================

% Plant Disease and Management Rules
% Format: disease_host_treatment(Disease, Host_Plant_or_Family, Treatment).

% Fungal Diseases
disease_host_treatment(honey_fungus, privet, remove_infected_plants_and_stumps).
disease_host_treatment(honey_fungus, lilac, remove_infected_plants_and_stumps).
disease_host_treatment(honey_fungus, viburnum, replace_soil_or_use_physical_barriers).
disease_host_treatment(honey_fungus, apple, remove_stumps_and_woody_debris).
disease_host_treatment(rose_black_spot, rose, clear_up_and_dispose_of_fallen_leaves).
disease_host_treatment(rose_black_spot, rose, apply_thick_winter_mulch).
disease_host_treatment(powdery_mildew, prunus, improve_air_ventilation_and_spacing).
disease_host_treatment(powdery_mildew, phlox, avoid_drought_stress_by_watering).
disease_host_treatment(apple_scab, apple, prune_out_infected_shoots_in_winter).
disease_host_treatment(apple_scab, cotoneaster, remove_and_dispose_of_fallen_leaves).
disease_host_treatment(pear_scab, pear, prune_out_infected_shoots_in_winter).
disease_host_treatment(pear_rust, pear, remove_affected_leaves_in_summer).
disease_host_treatment(pear_rust, juniper, remove_alternate_host_nearby_if_possible).
disease_host_treatment(box_blight, buxus, prune_only_in_dry_weather_and_clean_tools).

% Root and Soil-borne Diseases
disease_host_treatment(phytophthora_root_rot, rhododendron, improve_soil_drainage_and_aeration).
disease_host_treatment(phytophthora_root_rot, yew, avoid_overwatering_and_piling_mulch_on_stems).
disease_host_treatment(tulip_fire, tulip, dispose_of_infected_bulbs_and_foliage).

% Viral and Pests
disease_host_treatment(plant_virus, dahlia, dispose_of_heavily_infected_plants).
disease_host_treatment(box_tree_caterpillar, buxus, apply_biological_control_bacillus_thuringiensis).
disease_host_treatment(vine_weevil, cyclamen, apply_parasitic_nematodes_to_soil).
