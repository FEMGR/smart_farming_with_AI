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
        setof(X-Y,
            (
                member(X, CleanList),
                member(Y, CleanList),
                X @< Y,
                should_plant_with(X, Y)
            ),
            GoodPairs
        )
    -> true ; GoodPairs = []
    ),

    % -------------------------------------
    % BAD PAIRS
    % -------------------------------------

    (
        setof(X-Y,
            (
                member(X, CleanList),
                member(Y, CleanList),
                X @< Y,
                should_avoid(X, Y)
            ),
            BadPairs
        )
    -> true ; BadPairs = []
    ),

    % -------------------------------------
    % OUTPUT
    % -------------------------------------

    write('GOOD:'), write_list(GoodPairs), nl,

    write('BAD:'), write_list(BadPairs), nl.


% -------------------------------------
% SUGGEST COMPANIONS
% -------------------------------------

suggest_companions(InputList) :-
    load_all,
    maplist(normalize, InputList, NormalizedInput),
    exclude(is_unknown, NormalizedInput, CleanInput),

    % Get all known plants from the knowledge base
    (setof(P, plant(P), AllKnownPlants) -> true ; AllKnownPlants = []),

    % Find good companions for each plant in CleanInput
    (setof(ExistingPlant-GoodCompanion,
        (Source, Confidence)^( % Quantify Source and Confidence
            member(ExistingPlant, CleanInput),
            member(GoodCompanion, AllKnownPlants),
            \+ member(GoodCompanion, CleanInput), % Ensure it's not already in the input list
            should_plant_with(ExistingPlant, GoodCompanion)
        ),
        GoodSuggestions
    ) -> true ; GoodSuggestions = []),

    % Find bad companions for each plant in CleanInput
    (setof(ExistingPlant-BadCompanion,
        (Source, Confidence)^( % Quantify Source and Confidence
            member(ExistingPlant, CleanInput),
            member(BadCompanion, AllKnownPlants),
            \+ member(BadCompanion, CleanInput), % Ensure it's not already in the input list
            should_avoid(ExistingPlant, BadCompanion)
        ),
        BadSuggestions
    ) -> true ; BadSuggestions = []),

    write('SUGGEST_GOOD:'), write_list(GoodSuggestions), nl,
    write('SUGGEST_BAD:'), write_list(BadSuggestions), nl.
