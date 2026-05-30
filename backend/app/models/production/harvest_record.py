# app/models/production/harvest_record.py <<'PY'
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.database.db import Base


class HarvestRecord(Base):
    __tablename__ = "harvest_records"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(Integer, ForeignKey("production_batches.id", ondelete="CASCADE"), nullable=False)

    harvest_date = Column(Date, nullable=False)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), default="kg")
    quality_grade = Column(String(50), nullable=True)
    notes = Column(String, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    batch = relationship("ProductionBatch", back_populates="harvest_records")
