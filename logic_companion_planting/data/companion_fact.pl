
#logic_companion_planting/data/companion_fact.pl

% =========================================================
% COMPANION PLANTING DATA (TRACEABLE)
%
% Sources:
% - attra      : ATTRA / NCAT Companion Planting Guide
% - rhs        : Royal Horticultural Society
% - cornell    : Cornell Cooperative Extension
% - uc_anr     : UC Agriculture & Natural Resources (IPM)
% - traditional: widely accepted horticultural practice
%
% Confidence:
% - high   : well-documented / widely confirmed
% - medium : commonly accepted but less rigorous evidence
% =========================================================


% ====================================================================================================
% ATTRA Companion Planting Dataset (Structured)
% Source: ATTRA / NCAT
% Confidence: high
% ====================================================================================================

% =========================
% AMARANTH
% =========================
companion(amaranth, corn, attra, high).
companion(amaranth, onion, attra, high).
companion(amaranth, potato, attra, high).
antagonist(amaranth, brassica, attra, high).


% =========================
% ASPARAGUS
% =========================
companion(asparagus, basil, attra, high).
companion(asparagus, cilantro, attra, high).
companion(asparagus, parsley, attra, high).
companion(asparagus, tomato, attra, high).
companion(asparagus, comfrey, attra, high).
antagonist(asparagus, allium, attra, high).


% =========================
% BASIL
% =========================
companion(basil, vegetable, attra, medium).
antagonist(basil, rue, attra, high).


% =========================
% BEAN
% =========================
companion(bean, vegetable, attra, medium).
companion(bean, herb, attra, medium).
companion(bean, marigold, attra, high).
antagonist(bean, allium, attra, high).
antagonist(bean, gladiolus, attra, medium).


% =========================
% BEAN BUSH
% =========================
companion(bean_bush, potato, attra, high).
companion(bean_bush, cucumber, attra, high).
companion(bean_bush, corn, attra, high).
companion(bean_bush, strawberries, attra, high).
companion(bean_bush, celery, attra, high).
companion(bean_bush, summer_savory, attra, high).
antagonist(bean_bush, allium, attra, high).


% =========================
% BEAN POLE
% =========================
companion(bean_pole, corn, attra, high).
companion(bean_pole, marigold, attra, high).
companion(bean_pole, summer_savory, attra, high).
companion(bean_pole, radish, attra, high).
antagonist(bean_pole, allium, attra, high).
antagonist(bean_pole, beets, attra, high).
antagonist(bean_pole, kohlrabi, attra, high).
antagonist(bean_pole, sunflower, attra, high).


% =========================
% BEETS
% =========================
companion(beets, brassica, attra, high).
companion(beets, allium, attra, high).
companion(beets, lettuce, attra, high).
antagonist(beets, bean_pole, attra, high).


% =========================
% CABBAGE
% =========================
companion(cabbage, allium, attra, high).
companion(cabbage, chamomile, attra, high).
companion(cabbage, celery, attra, high).
companion(cabbage, clover, attra, high).
companion(cabbage, spinach, attra, high).

antagonist(cabbage, dill, attra, high).
antagonist(cabbage, bean_pole, attra, high).
antagonist(cabbage, strawberries, attra, high).
antagonist(cabbage, tomato, attra, high).


% =========================
% CARROT
% =========================
companion(carrot, allium, attra, high).
companion(carrot, pea_english, attra, high).
companion(carrot, lettuce, attra, high).
companion(carrot, rosemary, attra, high).
companion(carrot, sage, attra, high).
companion(carrot, tomato, attra, high).

antagonist(carrot, dill, attra, high).
antagonist(carrot, fennel, attra, high).


% =========================
% CORN
% =========================
companion(corn, bean, attra, high).
companion(corn, cucumber, attra, high).
companion(corn, pea_english, attra, high).
companion(corn, potato, attra, high).
companion(corn, pumpkin, attra, high).
companion(corn, squash, attra, high).

antagonist(corn, tomato, attra, high).


% =========================
% CUCUMBER
% =========================
companion(cucumber, bean, attra, high).
companion(cucumber, cabbage, attra, high).
companion(cucumber, corn, attra, high).
companion(cucumber, pea_english, attra, high).
companion(cucumber, radish, attra, high).
companion(cucumber, sunflower, attra, high).

antagonist(cucumber, herb, attra, medium).
antagonist(cucumber, potato, attra, high).


% =========================
% FENNEL
% =========================
antagonist(fennel, vegetable, attra, high).


% =========================
% LETTUCE
% =========================
companion(lettuce, carrot, attra, high).
companion(lettuce, cucumber, attra, high).
companion(lettuce, radish, attra, high).
companion(lettuce, strawberries, attra, high).


% =========================
% ONION
% =========================
companion(onion, beets, attra, high).
companion(onion, brassica, attra, high).
companion(onion, carrot, attra, high).
companion(onion, lettuce, attra, high).
companion(onion, summer_savory, attra, high).


% =========================
% PEPPER
% =========================
companion(pepper, basil, attra, high).
companion(pepper, clover, attra, high).
companion(pepper, tomato, attra, high).

antagonist(pepper, brassica, attra, high).


% =========================
% POTATO
% =========================
companion(potato, basil, attra, high).
companion(potato, bean, attra, high).
companion(potato, brassica, attra, high).
companion(potato, horseradish, attra, high).
companion(potato, marigold, attra, high).


% =========================
% RADISH
% =========================
companion(radish, cucumber, attra, high).
companion(radish, pea_english, attra, high).
companion(radish, lettuce, attra, high).
companion(radish, nasturtium, attra, high).

antagonist(radish, potato, attra, high).


% =========================
% SPINACH
% =========================
companion(spinach, celery, attra, high).
companion(spinach, strawberries, attra, high).

antagonist(spinach, hyssop, attra, high).


% =========================
% STRAWBERRIES
% =========================
companion(strawberries, borage, attra, high).
companion(strawberries, bean_bush, attra, high).
companion(strawberries, lettuce, attra, high).
companion(strawberries, pyrethrum, attra, high).
companion(strawberries, caraway, attra, high).

antagonist(strawberries, potato, attra, high).


% =========================
% TOMATO
% =========================
companion(tomato, allium, attra, high).
companion(tomato, asparagus, attra, high).
companion(tomato, basil, attra, high).
companion(tomato, carrot, attra, high).
companion(tomato, cucumber, attra, high).
companion(tomato, marigold, attra, high).
companion(tomato, nasturtium, attra, high).
companion(tomato, parsley, attra, high).
companion(tomato, rosemary, attra, high).

antagonist(tomato, bean_pole, attra, high).


% =========================
% WATERMELON
% =========================
companion(watermelon, nasturtium, attra, high).
companion(watermelon, marigold, attra, high).

antagonist(watermelon, potato, attra, high).
antagonist(watermelon, mustard, attra, high).


% =========================
% MELONS
% =========================
companion(melons, amaranth, attra, high).
companion(melons, bean, attra, high).
companion(melons, chamomile, attra, high).
companion(melons, corn, attra, high).

antagonist(melons, brassica, attra, high).


% =========================
% OKRA
% =========================
companion(okra, pepper, attra, high).
companion(okra, squash, attra, high).
companion(okra, sweet_potato, attra, high).

antagonist(okra, bean, attra, high).
antagonist(okra, pea_english, attra, high).


% =========================
% PUMPKIN
% =========================
companion(pumpkin, corn, attra, high).
companion(pumpkin, marigold, attra, high).

antagonist(pumpkin, squash, attra, medium).
antagonist(pumpkin, tomato, attra, high).
antagonist(pumpkin, sunflower, attra, high).


% =========================
% SQUASH
% =========================
companion(squash, nasturtium, attra, high).
companion(squash, corn, attra, high).
companion(squash, marigold, attra, high).


% =========================
% SUNFLOWER
% =========================
companion(sunflower, bean, attra, high).
companion(sunflower, corn, attra, high).
companion(sunflower, cucumber, attra, high).
companion(sunflower, melons, attra, high).
companion(sunflower, peanut, attra, high).

antagonist(sunflower, potato, attra, high).

% =========================
% ALLIUM (ONION, GARLIC, CHIVE)
% =========================
% Reason: Strong sulfurous scents mask the smell of host plants from pests.
companion(allium, carrot, ua, high). % Masks carrot rust fly scent.
companion(allium, rose, cornell, high). % Deters aphids.
companion(allium, lettuce, ua, medium). % Deters slugs and snails.

% =========================
% ASPARAGUS
% =========================
% Reason: Tomato plants produce solanine, which repels asparagus beetles.
companion(asparagus, tomato, cornell, high).
antagonist(asparagus, allium, traditional, medium). % General competition for nutrients.

% =========================
% BASIL
% =========================
% Reason: Strong essential oils interfere with the sensory receptors of many pests.
companion(basil, tomato, ua, high). % Deters tomato hornworms and whiteflies.


% =========================
% BRASSICA (CABBAGE, BROCCOLI, KALE)
% =========================
% Reason: Aromatic herbs mask the brassica scent from egg-laying moths.
companion(brassica, sage, cornell, high). % Deters cabbage moths.
companion(brassica, mint, ua, medium). % Deters ants and earth fleas.
antagonist(brassica, strawberries, traditional, medium). % Strawberries can attract pests that harm young brassicas.

% =========================
% CUCUMBER
% =========================
% Reason: Radish and Nasturtium act as sacrificial trap crops or deterrents.
companion(cucumber, nasturtium, ua, high). % Trap crop for aphids; deters beetles.
antagonist(cucumber, potato, traditional, high). % Both are heavy feeders and share blight susceptibility.
antagonist(cucumber, sage, ua, medium). % Sage is thought to stunt cucumber growth.

% =========================
% POTATO
% =========================
% Reason: Strong-smelling herbs prevent beetles from locating the potato foliage.
companion(potato, tansy, ua, high). % Specifically deters Colorado potato beetles.
antagonist(potato, tomato, traditional, high). % Both are susceptible to the same early/late blights.
antagonist(potato, sunflower, ua, medium). % Sunflowers can increase the risk of potato blight.

% =========================
% SQUASH
% =========================
% Reason: Nasturtium acts as a "decoy" for squash bugs.
companion(squash, corn, traditional, high). % Corn provides shade; squash mulch keeps roots cool.
antagonist(squash, potato, traditional, high). % Both compete for the same heavy nutrient load.



% ====================================================================================================
% COMPANION PLANTING DATA (TRACEABLE)
% Sources: attra, cornell, almanac, traditional
% ====================================================================================================

% =========================================================
% PEST-PLANT INTERACTION DATA
% =========================================================

% --- Cabbage Pests ---
deters(sage, cabbage_worm, traditional, high).
deters(mint, cabbage_moth, attra, high).

% --- Tomato Pests ---
deters(basil, hornworm, cornell, high).
deters(marigold, whitefly, attra, high).
deters(borage, hornworm, attra, high).

% --- Cucumber & Squash Pests ---
deters(nasturtium, cucumber_beetle, attra, medium).
deters(nasturtium, squash_bug, attra, high).
deters(radish, cucumber_beetle, traditional, medium).

% --- Carrot & Bean Pests ---
deters(onion, carrot_rust_fly, attra, high).
deters(rosemary, bean_beetle, attra, high).

% --- General Pest Interactions ---
deters(garlic, aphid, cornell, high).
deters(marigold, nematode, attra, high).

deters(mint, cabbage_moth, cornell, high).
deters(rosemary, cabbage_moth, attra, high).
deters(borage, hornworm, attra, high).
deters(radish, cucumber_beetle, attra, medium).
deters(catnip, flea_beetle, cornell, medium).
deters(leek, carrot_rust_fly, attra, high).
deters(horseradish, colorado_potato_beetle, attra, medium).
deters(chives, aphid, cornell, high).
deters(tomato, asparagus_beetle, cornell, high).
deters(thyme, armyworm, attra, medium).


% =========================================================
% UNIVERSITY OF ARIZONA (UA) COMPANION DATA
% =========================================================

% --- Scent Masking & Deterrents ---
deters(onion, carrot_fly, ua, high).
deters(chives, aphid, ua, high).
deters(chives, slug, ua, medium).
deters(chives, snail, ua, medium).

% --- General Pest Protection ---
deters(marigold, nematode, ua, high).
deters(marigold, beetle, ua, medium).
deters(basil, hornworm, ua, high).
deters(basil, mosquito, ua, medium).

% --- Beneficial Attraction (Arizona Guide) ---
attracts_beneficial(chamomile, hoverfly, ua, medium).
attracts_beneficial(chamomile, wasp, ua, medium).
attracts_beneficial(carrot, ladybug, ua, high). % Carrots in flower

% --- Disease Suppression ---
prevents(chives, apple_scab, ua, high).
