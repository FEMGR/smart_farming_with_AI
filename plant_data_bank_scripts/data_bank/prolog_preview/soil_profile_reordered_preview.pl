% FILE: logic_companion_planting/base/soil_profile.pl
%
% This file defines various soil types and their characteristics.
% It helps categorize soil for companion planting logic.

% =========================================
% SOIL TAXONOMY
% =========================================

% =========================================================
% SOIL PROFILE FACTS
% Auto-organized by plant_data_bank_scripts/scripts/prolog/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% CHALKY
% ---------------------------------------------------------
is_a(chalky, soil).
soil_drainage(chalky, good).
soil_water_retention(chalky, low).
soil_nutrient_level(chalky, low).
soil_ph(chalky, alkaline).
soil_texture(chalky, stony).

% ---------------------------------------------------------
% CLAY
% ---------------------------------------------------------
is_a(clay, soil).
soil_drainage(clay, poor).
soil_water_retention(clay, high).
soil_nutrient_level(clay, high).
soil_ph(clay, alkaline_to_neutral).
soil_texture(clay, sticky).

% ---------------------------------------------------------
% LOAMY
% ---------------------------------------------------------
is_a(loamy, soil).
soil_drainage(loamy, good).
soil_water_retention(loamy, moderate).
soil_nutrient_level(loamy, high).
soil_ph(loamy, neutral).
soil_texture(loamy, crumbly).

% ---------------------------------------------------------
% PEATY
% ---------------------------------------------------------
is_a(peaty, soil).
soil_drainage(peaty, good).
soil_water_retention(peaty, high).
soil_nutrient_level(peaty, high).
soil_ph(peaty, acidic).
soil_texture(peaty, spongy).

% ---------------------------------------------------------
% SANDY
% ---------------------------------------------------------
is_a(sandy, soil).
soil_drainage(sandy, good).
soil_water_retention(sandy, low).
soil_nutrient_level(sandy, low).
soil_ph(sandy, acidic_to_neutral).
soil_texture(sandy, gritty).

% ---------------------------------------------------------
% SILTY
% ---------------------------------------------------------
is_a(silty, soil).
soil_drainage(silty, moderate).
soil_water_retention(silty, moderate).
soil_nutrient_level(silty, moderate).
soil_ph(silty, neutral).
soil_texture(silty, smooth).
