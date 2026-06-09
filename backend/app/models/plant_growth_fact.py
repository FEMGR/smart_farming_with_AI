"""Persistent growth facts imported from local Prolog/CSV-generated data."""

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from app.database.db import Base


class PlantGrowthFact(Base):
    __tablename__ = "plant_growth_facts"
    __table_args__ = (UniqueConstraint("plant_key", name="uq_plant_growth_facts_plant_key"),)

    id = Column(Integer, primary_key=True, index=True)

    plant_key = Column(String(120), nullable=False, index=True)
    scientific_name = Column(String(255), nullable=True, index=True)
    genus = Column(String(120), nullable=True, index=True)
    family = Column(String(120), nullable=True, index=True)

    germination_days_min = Column(Integer, nullable=True)
    germination_days_max = Column(Integer, nullable=True)
    germination_light = Column(String(80), nullable=True)

    stratification_required = Column(Boolean, nullable=True)
    stratification_days_min = Column(Integer, nullable=True)
    stratification_days_max = Column(Integer, nullable=True)

    sowing_depth_cm = Column(Float, nullable=True)
    minimum_soil_temp_c = Column(Float, nullable=True)
    optimum_soil_temp_c = Column(Float, nullable=True)
    viable_temp_min_c = Column(Float, nullable=True)
    viable_temp_max_c = Column(Float, nullable=True)

    special_treatments = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    source_names = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    source_urls = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)
    raw_facts = Column(JSON().with_variant(JSONB, "postgresql"), nullable=True)

    confidence = Column(String(50), nullable=True)
    source_type = Column(String(80), nullable=False, default="local_generated_prolog")

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
