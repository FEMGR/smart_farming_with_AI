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

weather_condition(sunny).
weather_condition(partly_cloudy).
weather_condition(cloudy).
weather_condition(rainy).
weather_condition(windy).
weather_condition(stormy).
weather_condition(hot).
weather_condition(cold).
weather_condition(mild).
weather_condition(humid).
weather_condition(dry).

% =========================================================
% WEATHER CHARACTERISTICS
%
% weather_characteristic(Condition, Factor, Level)
%
% Example:
% weather_characteristic(hot, temperature, high).
% =========================================================

% -------------------------
% Temperature
% -------------------------

weather_characteristic(hot, temperature, high).
weather_characteristic(cold, temperature, low).
weather_characteristic(mild, temperature, moderate).

% -------------------------
% Precipitation
% -------------------------

weather_characteristic(rainy, precipitation, moderate).
weather_characteristic(stormy, precipitation, extreme).

% -------------------------
% Wind
% -------------------------

weather_characteristic(windy, wind, high).
weather_characteristic(stormy, wind, extreme).

% -------------------------
% Humidity
% -------------------------

weather_characteristic(humid, humidity, high).
weather_characteristic(dry, humidity, low).

% -------------------------
% Sunlight
% -------------------------

weather_characteristic(sunny, sunlight, high).
weather_characteristic(partly_cloudy, sunlight, moderate).
weather_characteristic(cloudy, sunlight, low).

% =========================================================
% WEATHER CATEGORIES
%
% weather_category(Condition, Category)
% =========================================================

% -------------------------
% Clear Weather
% -------------------------

weather_category(sunny, clear_weather).
weather_category(partly_cloudy, clear_weather).

% -------------------------
% Wet Weather
% -------------------------

weather_category(rainy, wet_weather).
weather_category(stormy, wet_weather).

% -------------------------
% Extreme Weather
% -------------------------

weather_category(stormy, extreme_weather).
weather_category(hot, extreme_weather).
weather_category(cold, extreme_weather).
weather_category(windy, extreme_weather).

% -------------------------
% Humidity Categories
% -------------------------

weather_category(humid, humid_weather).
weather_category(dry, dry_weather).
