% logic_companion_planting/rules/ecology_rules.pl

% =========================================================
% ECOLOGICAL INTELLIGENCE ENGINE
% =========================================================

% =========================================================
% TRAIT-BASED ECOLOGICAL MATCHING
% =========================================================

trait_companion(X, Y, Trait) :-

    plant(X),
    plant(Y),

    trait(X, Trait),
    trait(Y, Trait),

    X \= Y.


% =========================================================
% ECOLOGICAL PEST PROTECTION
% =========================================================

protects(Protector, Plant, Pest) :-

    attacks(Pest, Plant),

    deters(
        Protector,
        Pest,
        _Source,
        _Confidence
    ).


% =========================================================
% BENEFICIAL INSECT SUPPORT
% =========================================================

attracts_defender(Plant, Beneficial) :-

    attracts_beneficial(
        Plant,
        Beneficial,
        _Source,
        _Confidence
    ).


% =========================================================
% POLLINATION SUPPORT
% =========================================================

supports_pollination(Plant, Pollinator) :-

    pollinates(
        Pollinator,
        Plant
    ).


% =========================================================
% PROTECTION CHECK
% =========================================================

protected_from(Plant, Pest) :-

    near(Protector, Plant),

    deters(
        Protector,
        Pest,
        _,
        _
    ).


% =========================================================
% ECOLOGICAL RISK ANALYSIS
% =========================================================

at_risk(Plant) :-

    attacks(Pest, Plant),

    \+ protected_from(
        Plant,
        Pest
    ).


% =========================================================
% RISK EXPLANATION
% =========================================================

why_at_risk(
    Plant,
    explanation(attacked_by(Pest))
) :-

    attacks(Pest, Plant),

    \+ protected_from(
        Plant,
        Pest
    ).


% =========================================================
% UNIQUE RISK COLLECTION
% =========================================================

all_risks(Risks) :-

    setof(
        Plant,
        at_risk(Plant),
        Risks
    ).


% =========================================================
% ECOLOGICAL SAFETY CHECK
% =========================================================

ecologically_safe(Plant) :-

    \+ at_risk(Plant).


% =========================================================
% GARDEN BIODIVERSITY SCORE
% =========================================================

biodiversity_score(Score) :-

    findall(
        Beneficial,
        member_of(Beneficial, beneficial_insect),
        List
    ),

    sort(List, Unique),

    length(Unique, Score).


% =========================================================
% ECOLOGICAL CONFLICT DETECTION
% =========================================================

ecological_conflict(X, Y) :-

    conflict(X, Y, _, _).


% =========================================================
% ECOLOGICAL SUPPORT DETECTION
% =========================================================

ecological_support(X, Y) :-

    friendly(X, Y, _, _).


% =========================================================
% END OF FILE
% =========================================================