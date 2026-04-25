"""
Database model for PlantSpeciesCache.

Key Point:
Stores cached plant species data from external APIs.

Responsibilities:
- Cache plant species information
- Reduce external API calls and improve performance

Architecture Role:
- Acts as a local data cache for external plant data

Layer Interaction:
- Used by: Services, Integrations

Notes:
- Improves efficiency and reduces dependency on third-party APIs
"""

#app.models.plant_species_cache.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, func, JSON , DateTime
from sqlalchemy.dialects.postgresql import JSONB
from app.database.db import Base


class PlantSpeciesCache(Base):
    __tablename__ = "plant_species"
    #Fields
    id = Column(Integer, primary_key=True, index=True)
    external_species_id = Column(String(100))
    scientific_name = Column(String(100))
    common_name = Column(String(100))
    life_cycle = Column(String(50))
    sunlight_requirement = Column(String(255))
    watering_interval_days = Column(Integer, default=3)  # default every 3 days
    recommended_soil = Column(String(255))
    propagation_method = Column(String(255))
    pest_susceptibility = Column(String(255))

    # Cross-compatible JSON column
    data = Column(JSON().with_variant(JSONB, "postgresql"))
    #last_updated = Column(TIMESTAMP, server_default=func.now())

    #instrumental for SQLLite db test
    last_updated = Column(DateTime, server_default=func.now())

