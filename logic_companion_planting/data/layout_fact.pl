% FILE: logic_companion_planting/data/layout_fact.pl
%
% PURPOSE:
% Dynamic garden layout knowledge base.
%
% Stores:
% - plant proximity
% - garden placement
% - runtime spatial relationships
%
% Used by:
% - diagnostic_rules.pl
% - ecology_rules.pl
% - recommendation_rules.pl
%
% =========================================================
% DYNAMIC LAYOUT FACTS
% =========================================================

:- dynamic near/2.

% =========================================================
% EXAMPLE GARDEN LAYOUT
% =========================================================

near(tomato, basil).
near(cabbage, sage).
near(carrot, onion).
near(pepper, marigold).
near(bean_pole, corn).
near(marigold, tomato).
near(onion, carrot).
near(sage, cabbage).
near(bean_pole, corn).
near(radish, cucumber).