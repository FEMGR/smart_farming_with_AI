% logic_companion_planting/main.pl

:- ['load.pl'].


write_list([]).
write_list([X]) :-
    write(X).
write_list([X | Rest]) :-
    write(X),
    write(','),
    write_list(Rest).

% New predicate for writing lists of atoms (single plants)
write_atom_list([]).
write_atom_list([X]) :-
    write(X).
write_atom_list([X | Rest]) :-
    write(X),
    write(','),
    write_atom_list(Rest).

% -------------------------------------
% UNKNOWN FILTER HELPER
% -------------------------------------

is_unknown(unknown(_)).


recommend_all(InputList) :-
    load_all,

    % -------------------------------------
    % NORMALIZE INPUT
    % -------------------------------------

    maplist(normalize, InputList, Normalized),
    exclude(is_unknown, Normalized, CleanList),

    % -------------------------------------
    % GOOD PAIRS
    % -------------------------------------

    (
        setof(
            (X, Y, Reason),
            (
                member(X, CleanList),
                member(Y, CleanList),
                X @< Y,
                recommended_companion(X, Y, Reason)
            ),
            GoodPairs
        )
    -> true ; GoodPairs = []
    ),

    % -------------------------------------
    % BAD PAIRS
    % -------------------------------------

    (
        setof(
            (X, Y, Source, Confidence),
            (
                member(X, CleanList),
                member(Y, CleanList),
                X @< Y,
                expanded_conflict(X, Y, Source, Confidence)
            ),
            BadPairs
        )
    -> true ; BadPairs = []
    ),

    % -------------------------------------
    % OUTPUT
    % -------------------------------------

    write('GOOD:'),
    write_recommendation_list(GoodPairs),
    nl,

    write('BAD:'),
    write_bad_recommendation_list(BadPairs),
    nl.
% -------------------------------------
% SUGGEST COMPANIONS
% -------------------------------------

suggest_companions(InputList) :-
    load_all,
    maplist(normalize, InputList, NormalizedInput),
    exclude(is_unknown, NormalizedInput, CleanInput),

    % Get all known plants from the knowledge base
    (setof(P, plant(P), AllKnownPlants) -> true ; AllKnownPlants = []),

    % Find good companion suggestions with reasons
    (
        setof(
            (ExistingPlant, GoodCompanion, Reason),
            (
                member(ExistingPlant, CleanInput),
                member(GoodCompanion, AllKnownPlants),
                \+ member(GoodCompanion, CleanInput),
                recommended_companion(ExistingPlant, GoodCompanion, Reason)
            ),
            GoodSuggestions
        )
    -> true ; GoodSuggestions = []
    ),

    % Find bad companion suggestions with source/confidence
    (
        setof(
            (ExistingPlant, BadCompanion, Source, Confidence),
            (
                member(ExistingPlant, CleanInput),
                member(BadCompanion, AllKnownPlants),
                \+ member(BadCompanion, CleanInput),
                expanded_conflict(ExistingPlant, BadCompanion, Source, Confidence)
            ),
            BadSuggestions
        )
    -> true ; BadSuggestions = []
    ),

    write('SUGGEST_GOOD:'),
    write_recommendation_list(GoodSuggestions),
    nl,

    write('SUGGEST_BAD:'),
    write_bad_recommendation_list(BadSuggestions),
    nl.

% -------------------------------------
% FORMAT GOOD RECOMMENDATION
% -------------------------------------

write_recommendation((X, Y, reason(companion, Source, Confidence))) :-
    write(X-Y),
    write('|companion'),
    write('|Ecological companion support'),
    write('|'),
    write(Confidence),
    write('|'),
    write(Source).

write_recommendation((X, Y, reason(protection, Pest, Source, Confidence))) :-
    write(X-Y),
    write('|protection'),
    write('|Protects against '),
    write(Pest),
    write('|'),
    write(Confidence),
    write('|'),
    write(Source).

write_recommendation((X, Y, reason(attracts_beneficial, Beneficial, Source, Confidence))) :-
    write(X-Y),
    write('|beneficial_insect'),
    write('|Attracts beneficial insect '),
    write(Beneficial),
    write('|'),
    write(Confidence),
    write('|'),
    write(Source).

write_recommendation((X, Y, reason(trait, Trait))) :-
    write(X-Y),
    write('|trait'),
    write('|Shared ecological trait '),
    write(Trait),
    write('|0.6|ecology').


% -------------------------------------
% WRITE GOOD RECOMMENDATION LIST
% -------------------------------------

write_recommendation_list([]).

write_recommendation_list([X]) :-
    write_recommendation(X).

write_recommendation_list([X | Rest]) :-
    write_recommendation(X),
    write(','),
    write_recommendation_list(Rest).


% -------------------------------------
% FORMAT BAD RECOMMENDATION
% -------------------------------------

write_bad_recommendation((X, Y, Source, Confidence)) :-
    write(X-Y),
    write('|conflict'),
    write('|Conflict detected'),
    write('|'),
    write(Confidence),
    write('|'),
    write(Source).


% -------------------------------------
% WRITE BAD RECOMMENDATION LIST
% -------------------------------------

write_bad_recommendation_list([]).

write_bad_recommendation_list([X]) :-
    write_bad_recommendation(X).

write_bad_recommendation_list([X | Rest]) :-
    write_bad_recommendation(X),
    write(','),
    write_bad_recommendation_list(Rest).