% FILE: logic_companion_planting/rules/environment_rules.pl
%
% PURPOSE:
% Environmental reasoning engine for:
% - weather risks
% - plant stress
% - fungal conditions
% - irrigation reasoning
% - environmental compatibility
% - soil compatibility
%
% =========================================================
% ENVIRONMENTAL COMPATIBILITY
% =========================================================

% -------------------------
% Sunlight Compatibility
% -------------------------

compatible_sunlight(X, Y) :-
    sunlight_requirement(X, Level),
    sunlight_requirement(Y, Level).


sunlight_conflict(X, Y) :-
    sunlight_requirement(X, Level1),
    sunlight_requirement(Y, Level2),

    Level1 \= Level2.

% -------------------------
% Temperature Compatibility
% -------------------------

compatible_temperature(X, Y) :-
    preferred_temperature(X, Temp),
    preferred_temperature(Y, Temp).


temperature_conflict(X, Y) :-
    preferred_temperature(X, Temp1),
    preferred_temperature(Y, Temp2),

    Temp1 \= Temp2.

% =========================================================
% WATER COMPATIBILITY
% =========================================================

compatible_water(X, Y) :-
    water_need(X, Need),
    water_need(Y, Need).


water_conflict(X, Y) :-
    water_need(X, Need1),
    water_need(Y, Need2),

    Need1 \= Need2.

% =========================================================
% SOIL COMPATIBILITY
% =========================================================

% -------------------------
% Preferred Soil Match
% -------------------------

compatible_soil(Plant, Soil) :-
    preferred_soil(Plant, Soil).

% -------------------------
% Drainage Compatibility
% -------------------------

compatible_drainage(Plant, Soil) :-
    preferred_drainage(Plant, Drainage),
    soil_drainage(Soil, Drainage).

% -------------------------
% pH Compatibility
% -------------------------

compatible_soil_ph(Plant, Soil) :-
    preferred_soil_ph(Plant, PH),
    soil_ph(Soil, PH).

% =========================================================
% SOIL-BASED RISKS
% =========================================================

% -------------------------
% Soil Conflict
% -------------------------
soil_conflict(X, Y) :-

    preferred_soil(X, Soil1),
    preferred_soil(Y, Soil2),

    Soil1 \= Soil2.

% -------------------------
% Root Rot Risk
% -------------------------

root_rot_risk(Plant, Soil) :-
    sensitive_to_overwatering(Plant),
    soil_drainage(Soil, poor).

% -------------------------
% Drought Stress Risk
% -------------------------

drought_stress_risk(Plant, Soil, Time) :-
    soil_water_retention(Soil, low),
    high_evaporation_risk(Time),
    water_need(Plant, high).

% =========================================================
% WEATHER-BASED REASONING
% =========================================================

% -------------------------
% Evaporation Risk
% -------------------------

high_evaporation_risk(Time) :-
    current_weather(Time, temperature, high),
    current_weather(Time, sunlight, high),
    current_weather(Time, wind, high).

% -------------------------
% Storm Risk
% -------------------------

storm_risk(Time) :-
    current_weather(Time, wind, extreme),
    current_weather(Time, precipitation, extreme).

% =========================================================
% DISEASE CONDITIONS
% =========================================================

% -------------------------
% Fungal Disease Conditions
% -------------------------

favorable_for_fungal_disease(Time) :-
    current_weather(Time, humidity, high),
    current_weather(Time, precipitation, high).

% =========================================================
% PLANT STRESS CONDITIONS
% =========================================================

% -------------------------
% Heat Stress
% -------------------------

plant_heat_stress(Plant, Time) :-
    sensitive_to_heat(Plant),
    current_weather(Time, temperature, high),
    current_weather(Time, humidity, low).

% -------------------------
% Low Sunlight Risk
% -------------------------

low_sunlight_risk(Plant, Time) :-
    sunlight_requirement(Plant, full_sun),
    current_weather(Time, sunlight, low).

% =========================================================
% IDEAL ENVIRONMENTAL CONDITIONS
% =========================================================

ideal_growth_conditions(Plant, Soil, Time) :-
    preferred_temperature(Plant, moderate),
    current_weather(Time, temperature, moderate),

    compatible_drainage(Plant, Soil),

    current_weather(Time, humidity, moderate).

