# app/models/lifecycle/plant_event.py
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Date, JSON, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class PlantEvent(Base):
    __tablename__ = "plant_events"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(Integer, ForeignKey("production_batches.id", ondelete="SET NULL"), nullable=True)

    event_type = Column(String(50), nullable=False)
    event_date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    data = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    plant = relationship("Plant")
