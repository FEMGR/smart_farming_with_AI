

:- consult('load.pl').

recommend(X, Y) :-
    companion(X, Y),
    \+ antagonist(X, Y).