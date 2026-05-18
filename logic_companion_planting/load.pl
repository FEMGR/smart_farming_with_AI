% logic_companion_planting/load.pl

% =========================================================
% SMART FARMING KNOWLEDGE ENGINE LOADER
% =========================================================

load_all :-

    (   current_prolog_flag(argv, Argv),
        member('--quiet', Argv)
    ->  true
    ;   writeln('Loading Smart Farming Knowledge Base...')
    ),

    % =====================================================
    % BASE ONTOLOGY
    % =====================================================

    consult('base/plant_group.pl'),
    consult('base/insect_group.pl'),
    consult('base/soil_profile.pl'),
    consult('base/weather_taxonomy.pl'),

    % =====================================================
    % CORE FACTUAL DATA
    % =====================================================
    consult('data/alias_fact.pl'),
    consult('data/plant_fact.pl'),
    consult('data/insect_fact.pl'),
    consult('data/disease_fact.pl'),
    consult('data/weather_fact.pl'),
    consult('data/layout_fact.pl'),
    consult('data/environment_fact.pl'),

    % =====================================================
    % ECOLOGICAL RELATIONSHIPS
    % =====================================================

    consult('data/interaction_support.pl'),
    consult('data/pest_interactions.pl'),

    % =====================================================
    % SOURCE METADATA
    % =====================================================

    consult('data/sources_fact.pl'),

    % =====================================================
    % REASONING RULES
    % =====================================================

    consult('rules/normalization_rules.pl'),
    consult('rules/relationship_rules.pl'),
    consult('rules/ecology_rules.pl'),
    consult('rules/environment_rules.pl'),
    consult('rules/diagnostic_rules.pl'),
    consult('rules/recommendation_rules.pl'),

    (   current_prolog_flag(argv, Argv),
        member('--quiet', Argv)
    ->  true
    ;   writeln('Knowledge Base Loaded Successfully.')
    ).