from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Numeric, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class SoilCondition(Base):
    __tablename__ = "soil_conditions"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))

    recorded_at = Column(TIMESTAMP, server_default=func.now())

    moisture = Column(Numeric(5, 2))
    temperature = Column(Numeric(5, 2))
    humidity = Column(Numeric(5, 2))
    ph = Column(Numeric(4, 2))

    nitrogen = Column(Numeric(6, 2))
    phosphorus = Column(Numeric(6, 2))
    potassium = Column(Numeric(6, 2))

    source = Column(String(50), default="manual")

    # Relationships
    plant = relationship("Plant", back_populates="soil_records")
