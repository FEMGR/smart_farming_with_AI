% logic_companion_planting/rules/recommendation_rules.pl

% =========================================================
% SCORING SYSTEM
% =========================================================

score_reason(reason(companion, _, Confidence), Confidence).
score_reason(reason(trait, _), 0.6).
score_reason(reason(protection, _, _, Confidence), Confidence).
score_reason(reason(attracts_beneficial, _), 0.7).

% =========================================================
% PEST PROTECTION INFERENCE (CORE FIX)
% =========================================================

% Direct pest → plant → protector chain
protects(Protector, Plant, Pest, Source, Confidence) :-
    attacks(Pest, Plant),
    deters(Protector, Pest, Source, Confidence).

% (Optional but powerful) group-level pest expansion
protects(Protector, Plant, Pest, Source, Confidence) :-
    attacks(Pest, Group),
    group(Group),
    member_of(Plant, Group),
    deters(Protector, Pest, Source, Confidence).

% =========================================================
% HIGH-LEVEL RECOMMENDATION ENGINE
% =========================================================

% -----------------------------------------
% Companion-based
% -----------------------------------------

recommended_companion(
    Plant,
    Candidate,
    reason(companion, Source, Confidence)
) :-
    normalize(Plant, NP),
    normalize(Candidate, NC),
    safe_companion(NP, NC, Source, Confidence).

% -----------------------------------------
% Trait-based
% -----------------------------------------

recommended_companion(
    Plant,
    Candidate,
    reason(trait, Trait)
) :-
    normalize(Plant, NP),
    trait_companion(NP, Candidate, Trait).

% -----------------------------------------
% Pest protection (FIXED + EXTENDED)
% -----------------------------------------

recommended_companion(
    Plant,
    Protector,
    reason(protection, Pest, Source, Confidence)
) :-
    normalize(Plant, NP),
    protects(Protector, NP, Pest, Source, Confidence).

% -----------------------------------------
% Beneficial insect support
% -----------------------------------------

recommended_companion(
    Plant,
    Companion,
    reason(attracts_beneficial, Beneficial, Source, Confidence)
) :-
    normalize(Plant, NP),
    safe_companion(NP, Companion, _, _),
    attracts_beneficial(Companion, Beneficial, Source, Confidence).

% =========================================================
% UNIQUE RECOMMENDATION WRAPPER
% =========================================================

unique_recommendations(Plant, Results) :-
    findall(
        (Candidate, Reason),
        recommended_companion(Plant, Candidate, Reason),
        Raw
    ),
    sort(Raw, Results).

% =========================================================
% EXPLANATION ENGINE (ALIGNED WITH INFERENCE)
% =========================================================

why_recommend(
    Protector,
    Plant,
    explanation(protects_against(Pest, Source, Confidence))
) :-
    normalize(Plant, NP),
    protects(Protector, NP, Pest, Source, Confidence).

why_recommend(
    Companion,
    Plant,
    explanation(ecological_support(Source, Confidence))
) :-
    normalize(Plant, NP),
    safe_companion(NP, Companion, Source, Confidence).

why_recommend(
    Companion,
    Plant,
    explanation(attracts(Beneficial))
) :-
    normalize(Plant, NP),
    safe_companion(NP, Companion, _, _),
    attracts_beneficial(Companion, Beneficial, _, _).

% =========================================================
% QUERY HELPERS
% =========================================================

find_companions(Plant, Results) :-
    unique_recommendations(Plant, Results).

find_conflicts(X, Y) :-
    expanded_conflict(X, Y, _, _).

% =========================================================
% SCORING WRAPPER
% =========================================================

recommend_with_score(Plant, Candidate, Score, Reason) :-
    recommended_companion(Plant, Candidate, Reason),
    score_reason(Reason, Score).

% =========================================================
% RANKED RECOMMENDATIONS
% =========================================================

ranked_recommendations(Plant, Sorted) :-
    findall(
        Score-Candidate-Reason,
        recommend_with_score(Plant, Candidate, Score, Reason),
        Raw
    ),
    sort(0, @>=, Raw, Sorted).