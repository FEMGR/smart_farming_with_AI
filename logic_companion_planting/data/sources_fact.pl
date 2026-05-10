% FILE: sources_fact.pl
%
% PURPOSE:
% This file defines the authoritative sources used throughout the Smart Farming System's
% companion planting knowledge base. Each source is declared with a unique atom name,
% allowing for traceability and confidence assessment of the facts derived from them.
%
% PREDICATES DEFINED:
% - source(SourceName): Declares a recognized source of information.
%
% RELATED MODULES:
% - `companion_fact.pl`: References these sources to indicate the origin of companion planting relationships.
% - `disease_fact.pl`: May reference these sources for disease-related information.
% - Other fact files: Can use these sources to attribute data.
%
% USAGE:
% This file is consulted to maintain a consistent and transparent record of where
% information originates, which is crucial for evaluating the reliability and
% applicability of the advice provided by the system.
%

% =========================================================
%
% SOURCES:
% - attra      : ATTRA / NCAT Companion Planting Guide
% - rhs        : Royal Horticultural Society
% - cornell    : Cornell Cooperative Extension
% - uc_anr     : UC Agriculture & Natural Resources (IPM)
% - traditional: widely accepted horticultural practice
%
% =========================================================

% =========================
% SOURCES
% =========================
source(attra).
source(uc_anr).
source(rhs).
source(cornell).
source(usda).
source(traditional).