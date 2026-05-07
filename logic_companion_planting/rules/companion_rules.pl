
#logic_companion_planting/rules/companion_rules.pl
% =========================================
% SMART FARMING - COMPANION LOGIC ENGINE
% =========================================



% -----------------------------
% 2. ENVIRONMENT REQUIREMENTS
% -----------------------------

requires(tomato, full_sun).
requires(basil, full_sun).
requires(cabbage, partial_shade).
requires(marigold, full_sun).
requires(garlic, full_sun).
requires(borage, full_sun).

water_need(tomato, medium).
water_need(basil, medium).
water_need(cabbage, high).
water_need(marigold, low).
water_need(garlic, low).
water_need(borage, medium).

% -----------------------------
% 3. COMPANION RELATIONSHIPS
% -----------------------------

good_pair(tomato, basil).
good_pair(tomato, marigold).
good_pair(tomato, garlic).
good_pair(cabbage, garlic).

bad_pair(tomato, cabbage).
bad_pair(cabbage, tomato).  % optional redundancy for clarity


% -----------------------------
% 5. PLANT EFFECTS
% -----------------------------

repels(garlic, aphid).
repels(marigold, nematode).

attracts(basil, pollinators).
attracts(borage, bees).

% -----------------------------
% 6. GARDEN LAYOUT (DYNAMIC)
% -----------------------------
% These will usually come from your backend

:- dynamic near/2.

% Example layout (can be removed in production)
near(tomato, basil).
near(tomato, cabbage).

% -----------------------------
% 7. CORE RULES
% -----------------------------

% Symmetric companion
companion(X, Y) :- good_pair(X, Y).
companion(X, Y) :- good_pair(Y, X).

% Symmetric conflict
conflict(X, Y) :- bad_pair(X, Y).
conflict(X, Y) :- bad_pair(Y, X).

% -----------------------------
% 8. ECOLOGICAL INTELLIGENCE
% -----------------------------

% A plant protects another if it repels a pest attacking it
protects(Helper, Plant) :-
    repels(Helper, Pest),
    attacks(Pest, Plant).

% Plant is at risk if pests attack it and no protection nearby
at_risk(Plant) :-
    attacks(Pest, Plant),
    \+ (near(Helper, Plant), repels(Helper, Pest)).

% -----------------------------
% 9. ENVIRONMENT COMPATIBILITY
% -----------------------------

compatible_environment(X, Y) :-
    requires(X, Cond),
    requires(Y, Cond).

environment_conflict(X, Y) :-
    requires(X, Cond1),
    requires(Y, Cond2),
    Cond1 \= Cond2.

% -----------------------------
% 10. GARDEN LOGIC
% -----------------------------

% Detect bad neighbors
bad_neighbor(X, Y) :-
    near(X, Y),
    conflict(X, Y).

% Detect general problems
problem(X, Y) :-
    near(X, Y),
    (
        conflict(X, Y);
        environment_conflict(X, Y)
    ).

% -----------------------------
% 11. RECOMMENDATION ENGINE
% -----------------------------

% Good companion overall
good_companion(X, Y) :-
    companion(X, Y),
    compatible_environment(X, Y),
    \+ conflict(X, Y).

% Suggest what to plant near a plant
should_plant_with(Plant, Helper) :-
    protects(Helper, Plant).

% Suggest what to avoid
should_avoid(Plant, Neighbor) :-
    conflict(Plant, Neighbor).

% -----------------------------
% 12. ADVANCED INSIGHT
% -----------------------------

% Fully safe pairing
safe_pair(X, Y) :-
    good_companion(X, Y),
    \+ environment_conflict(X, Y).

% Dangerous pairing
dangerous_pair(X, Y) :-
    conflict(X, Y).

% Find all helpers for a plant
helper_for(Plant, Helper) :-
    protects(Helper, Plant).

% -----------------------------
% END OF MODEL
% -----------------------------
