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

# app.models.plant_species_cache.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float

from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from app.database.db import Base


class PlantSpeciesCache(Base):

    __tablename__ = "plant_species"

    # =====================================
    # INTERNAL IDENTIFIERS
    # =====================================

    id = Column(Integer, primary_key=True, index=True)

    external_species_id = Column(String(100), unique=True, nullable=False, index=True)

    # =====================================
    # CORE IDENTITY
    # =====================================

    scientific_name = Column(String(255), nullable=False)

    common_name = Column(String(255))

    other_names = Column(String(500))

    plant_type = Column(String(100))

    description = Column(String)

    # =====================================
    # EDIBILITY
    # =====================================

    is_edible = Column(Boolean, default=False)

    is_fruit = Column(Boolean, default=False)

    is_veg = Column(Boolean, default=False)

    cuisine = Column(Boolean, default=False)

    medicinal = Column(Boolean, default=False)

    poisonous_to_humans = Column(Boolean)

    poisonous_to_pets = Column(Boolean)

    # =====================================
    # GROWTH & CARE
    # =====================================

    growth_rate = Column(String(50))

    life_cycle = Column(String(50))

    care_level = Column(String(50))

    watering = Column(String(50))

    watering_interval_days = Column(Integer, default=3)

    drought_tolerant = Column(Boolean)

    salt_tolerant = Column(Boolean)

    thorny = Column(Boolean)

    invasive = Column(Boolean)

    tropical = Column(Boolean)

    indoor = Column(Boolean)

    # =====================================
    # ENVIRONMENT
    # =====================================

    sunlight_requirement = Column(String(255))

    recommended_soil = Column(String(255))

    propagation_method = Column(String(255))

    pest_susceptibility = Column(String(500))

    hardiness = Column(String(100))

    hardiness_location = Column(String(255))

    # =====================================
    # DIMENSIONS
    # =====================================

    max_height_ft = Column(Float)

    max_width_ft = Column(Float)

    # =====================================
    # MEDIA
    # =====================================

    default_image_url = Column(String)

    thumbnail_url = Column(String)

    # =====================================
    # RAW PAYLOAD
    # =====================================

    data = Column(JSON().with_variant(JSONB, "postgresql"))

    # =====================================
    # TIMESTAMPS
    # =====================================

    created_at = Column(DateTime, server_default=func.now())

    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())


""" 
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from app.database.db import Base


class PlantSpeciesCache(Base):
    __tablename__ = "plant_species"
    #Fields
    id = Column(Integer, primary_key=True, index=True)
    external_species_id = Column(String(100))
    scientific_name = Column(String(100))
    common_name = Column(String(100))
    is_edible = Column(Boolean, default=False)
    is_fruit = Column(Boolean, default=False)
    is_veg = Column(Boolean, default=False)
    growth_rate = Column(String(10))
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

"""
