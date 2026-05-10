% logic_companion_planting/rules/recommendation_rules.pl

% =========================================================
% HIGH-LEVEL RECOMMENDATION ENGINE
% =========================================================

% =========================================================
% DIRECT COMPANION RECOMMENDATION
% =========================================================

% =========================================================
% HIGH-LEVEL RECOMMENDATION ENGINE
% =========================================================

recommended_companion(
    Plant,
    Candidate,
    reason(companion, Source, Confidence)
) :-

    safe_companion(
        Plant,
        Candidate,
        Source,
        Confidence
    ).


% =========================================================
% TRAIT-BASED RECOMMENDATION
% =========================================================

recommended_companion(
    Plant,
    Candidate,
    reason(trait, Trait)
) :-

    trait_companion(
        Plant,
        Candidate,
        Trait
    ).


% =========================================================
% PEST PROTECTION RECOMMENDATION
% =========================================================

recommended_companion(
    Plant,
    Protector,
    reason(protection, Pest)
) :-

    protects(
        Protector,
        Plant,
        Pest
    ).


% =========================================================
% BENEFICIAL INSECT SUPPORT
% =========================================================

recommended_companion(
    Plant,
    Companion,
    reason(attracts_beneficial, Beneficial)
) :-

    safe_companion(
        Plant,
        Companion,
        _,
        _
    ),

    attracts_defender(
        Companion,
        Beneficial
    ).

% =========================================================
% UNIQUE RECOMMENDATION WRAPPER
% =========================================================

unique_recommendations(Plant, Results) :-
    findall(
        (Candidate, Reason),
        recommended_companion(
            Plant,
            Candidate,
            Reason
        ),
        Raw
    ),

    sort(Raw, Results).


% =========================================================
% EXPLANATION ENGINE
% =========================================================

why_recommend(
    Protector,
    Plant,
    explanation(
        protects_against(Pest)
    )
) :-
    attacks(Pest, Plant),
    deters(
        Protector,
        Pest,
        _,
        _
    ).

why_recommend(
    Companion,
    Plant,
    explanation(
        ecological_support(Source, Confidence)
    )
) :-
    safe_companion(
        Plant,
        Companion,
        Source,
        Confidence
    ).

why_recommend(
    Plant,
    Companion,
    explanation(
        attracts(Beneficial)
    )
) :-
    safe_companion(
        Plant,
        Companion,
        _,
        _
    ),
    attracts_beneficial(
        Companion,
        Beneficial,
        _,
        _
    ).

% =========================================================
% QUERY HELPERS
% =========================================================

find_companions(Plant, Results) :-

    unique_recommendations(
        Plant,
        Results
    ).


find_conflicts(X, Y) :-
    expanded_conflict(
        X,
        Y,
        _,
        _
    ).
