% logic_companion_planting/main.pl

:- ['load.pl'].

main :-
    load_all,
    run_demo.

:- initialization(main).

% =========================================================
% SAMPLE QUERIES
% =========================================================

run_demo :-

    writeln('====================================='),
    writeln('SMART FARMING RECOMMENDATION ENGINE'),
    writeln('====================================='),

    nl,

    % =====================================================
    % RECOMMENDED COMPANIONS
    % =====================================================

    writeln('Recommended companions for tomato:'),

    (
        setof(
            (Plant, Reason),
            recommended_companion(
                tomato,
                Plant,
                Reason
            ),
            Recommendations
        ),

        forall(
            member((Plant, Reason), Recommendations),
            (
                write('- '),
                write(Plant),
                write(' : '),
                writeln(Reason)
            )
        )

        ;

        writeln('No recommendations found.')
    ),

    nl,

    % =====================================================
    % PLANTS TO AVOID
    % =====================================================

    writeln('Plants tomato should avoid:'),

    (
        setof(
            BadPlant,
            should_avoid(tomato, BadPlant),
            BadPlants
        ),

        forall(
            member(BadPlant, BadPlants),
            (
                write('- '),
                writeln(BadPlant)
            )
        )

        ;

        writeln('No conflicts detected.')
    ),

    nl,

    % =====================================================
    % ECOLOGICAL RISKS
    % =====================================================

    writeln('Plants currently at ecological risk:'),

    (
        setof(
            Plant,
            at_risk(Plant),
            Risks
        ),

        forall(
            member(Plant, Risks),
            (
                write('- '),
                writeln(Plant)
            )
        )

        ;

        writeln('No ecological risks detected.')
    ),

    nl,

    writeln('Done.').