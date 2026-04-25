"""
Utility layer for Data Reliability Scoring.

Key Point:
Calculates a reliability score for plant data based on source, completeness, and context.

Responsibilities:
- Assign base trust levels based on data source
- Evaluate data completeness (e.g., watering, species, care attributes)
- Adjust score using contextual factors (e.g., sensor usage, freshness)
- Provide a normalized reliability score (0.0 – 1.0)

Architecture Role:
- Decision-support utility for intelligent features
- Enhances system behavior without modifying core business logic

Layer Interaction:
- Communicates with: Plant model (and optionally Species Cache)
- Called by: Services (irrigation, plant, notifications, AI modules)

Data Flow:
Plant object passed into utility
        ↓
Source-based base score assigned
        ↓
Completeness and context adjustments applied
        ↓
Score normalized between 0 and 1
        ↓
Reliability score returned to caller
"""


#app/utils/reliability.py

from datetime import datetime

SOURCE_WEIGHTS = {
    "manual": 0.4,
    "perenual": 0.7,
    "import": 0.5,
    "sensor": 0.9,
    "ai": 0.6,
}


def calculate_reliability(plant) -> float:
    """
    Calculate reliability score for a plant (0.0 - 1.0)
    """

    # 1. Base score from source
    score = SOURCE_WEIGHTS.get(plant.source, 0.5)

    # 2. Increase reliability if sensor is used
    if plant.use_sensor:
        score += 0.15

    # 3. Data completeness, higher value
    completeness_fields = [
        plant.watering_interval_days,
        plant.species,
        getattr(plant, "sunlight_requirement", None),
        getattr(plant, "recommended_soil", None),
    ]
    filled = sum(1 for f in completeness_fields if f)
    completeness_score = filled / len(completeness_fields)
    score += 0.2 * completeness_score

    # 4. Penalty
    if plant.last_watered:
        days_since_watered = (datetime.utcnow().date() - plant.last_watered).days
        if days_since_watered > 14:
            score -= 0.1
        elif days_since_watered > 30:
            score -= 0.2

    # Normalizing
    return max(0.0, min(1.0, score))
