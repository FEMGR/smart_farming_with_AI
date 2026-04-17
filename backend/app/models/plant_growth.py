from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class PlantGrowth(Base):
    __tablename__ = "plant_growth"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))

    recorded_at = Column(TIMESTAMP, server_default=func.now())
    height_cm = Column(Numeric(5, 2))
    leaf_count = Column(Integer)

    stage = Column(String(50))
    health_status = Column(String(50))

    notes = Column(String)

    # Relationships
    plant = relationship("Plant", back_populates="growth_records")
