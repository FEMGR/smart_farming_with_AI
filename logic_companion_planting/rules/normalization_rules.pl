% logic_companion_planting/rules/normalization_rules.pl


% -----------------------------------------
% MAIN NORMALIZATION ENTRY
% -----------------------------------------

normalize(X, NX) :-
    nonvar(X),
    atom(X),
    downcase_atom(X, Lower),
    normalize_lower(Lower, NX).

% -----------------------------------------
% INTERNAL NORMALIZATION
% -----------------------------------------

normalize_lower(X, NX) :-
    alias(X, NX), !.

normalize_lower(X, X) :-
    plant(X), !.

normalize_lower(X, X) :-
    group(X), !.

% -----------------------------------------
% UNKNOWN HANDLING
% -----------------------------------------

normalize_lower(X, unknown(X)).


% =========================================================
% SAFE NORMALIZATION FOR LISTS
% =========================================================

normalize_list(Input, Output) :-
    maplist(normalize, Input, Temp),
    exclude(is_unknown, Temp, Output).