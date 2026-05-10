% logic_companion_planting/rules/relationship_rules.pl

% =========================================================
% RELATIONSHIP INFERENCE ENGINE
% =========================================================

% =========================================================
% SYMMETRIC SUPPORT
% =========================================================

friendly(X, Y, Source, Confidence) :-
    beneficial_relation(X, Y, Source, Confidence).

friendly(X, Y, Source, Confidence) :-
    beneficial_relation(Y, X, Source, Confidence).


% =========================================================
% SYMMETRIC CONFLICT
% =========================================================

conflict(X, Y, Source, Confidence) :-
    harmful_relation(X, Y, Source, Confidence).

conflict(X, Y, Source, Confidence) :-
    harmful_relation(Y, X, Source, Confidence).


% =========================================================
% DIRECT SUPPORT
% =========================================================

direct_support(X, Y, Source, Confidence) :-
    friendly(X, Y, Source, Confidence).


% =========================================================
% GROUP SUPPORT EXPANSION
% =========================================================

expanded_support(X, Y, Source, Confidence) :-
    friendly(X, Group, Source, Confidence),
    group(Group),
    member_of(Y, Group).

expanded_support(X, Y, Source, Confidence) :-
    friendly(Group, Y, Source, Confidence),
    group(Group),
    member_of(X, Group).

expanded_support(X, Y, Source, Confidence) :-
    friendly(GroupA, GroupB, Source, Confidence),
    group(GroupA),
    group(GroupB),
    member_of(X, GroupA),
    member_of(Y, GroupB).

% =========================================================
% GROUP CONFLICT EXPANSION
% =========================================================

expanded_conflict(X, Y, Source, Confidence) :-
    conflict(X, Group, Source, Confidence),
    group(Group),
    member_of(Y, Group).

expanded_conflict(X, Y, Source, Confidence) :-
    conflict(Group, Y, Source, Confidence),
    group(Group),
    member_of(X, Group).

expanded_conflict(X, Y, Source, Confidence) :-
    conflict(GroupA, GroupB, Source, Confidence),
    group(GroupA),
    group(GroupB),
    member_of(X, GroupA),
    member_of(Y, GroupB).

% =========================================================
% SAFE ECOLOGICAL RELATIONSHIPS
% =========================================================

safe_companion(X, Y, Source, Confidence) :-

    normalize(X, NX),
    normalize(Y, NY),

    (
        direct_support(
            NX,
            NY,
            Source,
            Confidence
        )

        ;

        expanded_support(
            NX,
            NY,
            Source,
            Confidence
        )
    ),

    NX \= NY,

    \+ direct_conflict(NX, NY),

    \+ expanded_conflict(
        NX,
        NY,
        _,
        _
    ).


% =========================================================
% DIRECT CONFLICT CHECK
% =========================================================

direct_conflict(X, Y) :-
    harmful_relation(X, Y, _, _).

direct_conflict(X, Y) :-
    harmful_relation(Y, X, _, _).


% =========================================================
% FINAL NEIGHBOR EVALUATION
% =========================================================

good_neighbor(X, Y) :-
    safe_companion(X, Y, _, _).

should_plant_with(X, Y) :-

    good_neighbor(X, Y).

bba(X, Y) :-
    expanded_conflict(X, Y, _, _).

should_avoid(X, Y) :-

    direct_conflict(X, Y).

should_avoid(X, Y) :-

    expanded_conflict(X, Y, _, _).

