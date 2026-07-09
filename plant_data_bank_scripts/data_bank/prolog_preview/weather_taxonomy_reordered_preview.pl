% FILE: logic_companion_planting/base/weather_taxonomy.pl
%
% PURPOSE:
% This file defines various weather conditions and their associated characteristics.
% It helps categorize weather for companion planting logic, allowing rules to consider
% environmental factors in recommendations.
%
% PREDICATES:
% - weather_condition(ConditionName): Declares a specific weather condition (e.g., sunny, rainy).
% - weather_characteristic(Condition, Factor, Level): Associates a characteristic
%   (e.g., high_temperature, precipitation, strong_winds, high_humidity, high_sunlight)
%   with a particular weather condition.
% - weather_category(Condition, Category)
%
% RELATED MODULES:
% - `environment_rules.pl`: uses these weather facts to define environmental rules
%   and conditions for plant growth or irrigation.
%
% USAGE:
% This file is queried by rules that need to evaluate environmental conditions.
% For example, a rule might check `weather_characteristic(Condition, Factor, Level)`
% to determine if certain plants are under stress.
% =========================================================
% WEATHER CONDITIONS
% =========================================================

% =========================================================
% WEATHER TAXONOMY FACTS
% Auto-organized by plant_data_bank_scripts/scripts/prolog/reorder_prolog_facts_by_plant.py
% =========================================================

% ---------------------------------------------------------
% CLOUDY
% ---------------------------------------------------------
weather_condition(cloudy).
weather_characteristic(cloudy, sunlight, low).

% ---------------------------------------------------------
% COLD
% ---------------------------------------------------------
weather_condition(cold).
weather_characteristic(cold, temperature, low).
weather_category(cold, extreme_weather).

% ---------------------------------------------------------
% DRY
% ---------------------------------------------------------
weather_condition(dry).
weather_characteristic(dry, humidity, low).
weather_category(dry, dry_weather).

% ---------------------------------------------------------
% HOT
% ---------------------------------------------------------
weather_condition(hot).
weather_characteristic(hot, temperature, high).
weather_category(hot, extreme_weather).

% ---------------------------------------------------------
% HUMID
% ---------------------------------------------------------
weather_condition(humid).
weather_characteristic(humid, humidity, high).
weather_category(humid, humid_weather).

% ---------------------------------------------------------
% MILD
% ---------------------------------------------------------
weather_condition(mild).
weather_characteristic(mild, temperature, moderate).

% ---------------------------------------------------------
% PARTLY CLOUDY
% ---------------------------------------------------------
weather_condition(partly_cloudy).
weather_characteristic(partly_cloudy, sunlight, moderate).
weather_category(partly_cloudy, clear_weather).

% ---------------------------------------------------------
% RAINY
% ---------------------------------------------------------
weather_condition(rainy).
weather_characteristic(rainy, precipitation, moderate).
weather_category(rainy, wet_weather).

% ---------------------------------------------------------
% STORMY
% ---------------------------------------------------------
weather_condition(stormy).
weather_characteristic(stormy, precipitation, extreme).
weather_characteristic(stormy, wind, extreme).
weather_category(stormy, extreme_weather).
weather_category(stormy, wet_weather).

% ---------------------------------------------------------
% SUNNY
% ---------------------------------------------------------
weather_condition(sunny).
weather_characteristic(sunny, sunlight, high).
weather_category(sunny, clear_weather).

% ---------------------------------------------------------
% WINDY
% ---------------------------------------------------------
weather_condition(windy).
weather_characteristic(windy, wind, high).
weather_category(windy, extreme_weather).
