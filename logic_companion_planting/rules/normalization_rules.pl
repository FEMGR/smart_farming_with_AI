% logic_companion_planting/rules/normalization_rules.pl

% =========================================================
% NORMALIZATION RULES
% =========================================================

normalize(X, Canonical) :-

    alias(X, Canonical).


normalize(X, X) :-

    plant(X).


normalize(X, X) :-

    group(X).

normalize(X, X) :-

    nonvar(X),

    \+ alias(X, _).
