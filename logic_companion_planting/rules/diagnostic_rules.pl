% FILE: logic_companion_planting/rules/diagnostic_rules.pl
%
% PURPOSE:
% This file contains rules for diagnosing potential problems in a garden layout,
% particularly in the context of companion planting. It identifies conflicts
% related to plant interactions, environmental factors, water needs, and pest risks.
%
% PREDICATES:
% - bad_neighbor_layout(Plant1, Plant2): Identifies if two plants placed near each other
%   have an expanded conflict (e.g., antagonistic relationship).
% - environment_problem(Plant1, Plant2): Checks for environmental conflicts between
%   two nearby plants.
% - water_problem(Plant1, Plant2): Detects conflicts in water requirements between
%   two nearby plants.
% - pest_risk(Plant, Pest): Determines if a specific plant is at risk from a pest,
%   considering if there are protective measures in place.
% - at_risk_layout(Plant): A general predicate to indicate if a plant in the layout
%   is at risk due to any pest.
%
% RELATED MODULES:
% - `interaction_support.pl`: Provides predicates like `expanded_conflict/4` which
%   are used here to determine conflicts.
% - `environment_rules.pl`: Defines `environment_conflict/2`.
% - `normalization_rules.pl`: Defines `water_conflict/2`.
% - `insect_fact.pl`: Defines `attacks/2`.
% - `recommendation_rules.pl`: Might use these diagnostic rules to inform recommendations.
%
% USAGE:
% These rules are typically queried to assess the health and compatibility of a
% garden design, highlighting areas where companion planting principles might be violated.

% =========================================================
% GARDEN DIAGNOSTIC ENGINE
% =========================================================

% :- dynamic near/2.


% =========================================================
% CONFLICT DIAGNOSTICS
% =========================================================

bad_neighbor_layout(X, Y) :-

    near(X, Y),

    expanded_conflict(X, Y, _, _).


% =========================================================
% ENVIRONMENT DIAGNOSTICS
% =========================================================

environment_problem(X, Y) :-

    near(X, Y),

    (
        sunlight_conflict(X, Y)
        ;
        temperature_conflict(X, Y)
        ;
        water_conflict(X, Y)
        ;
        soil_conflict(X, Y)
    ).

% =========================================================
% WATER DIAGNOSTICS
% =========================================================

water_problem(X, Y) :-

    near(X, Y),

    water_conflict(X, Y).


% =========================================================
% PEST RISK DIAGNOSTICS
% =========================================================

pest_risk(Plant, Pest) :-

    attacks(Pest, Plant),

    \+ protects(_, Plant, Pest).


% =========================================================
% GENERAL RISK STATUS
% =========================================================

at_risk_layout(Plant) :-

    pest_risk(Plant, _).
