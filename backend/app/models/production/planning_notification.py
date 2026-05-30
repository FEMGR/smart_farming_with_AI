# app/models/production/planning_notification.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, TIMESTAMP, func

from app.database.db import Base


class PlanningNotification(Base):
    __tablename__ = "planning_notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    batch_id = Column(Integer, ForeignKey("production_batches.id", ondelete="CASCADE"), nullable=True)
    crop_plan_id = Column(Integer, ForeignKey("crop_plans.id", ondelete="CASCADE"), nullable=True)

    notification_type = Column(String(50), nullable=False)
    message = Column(String, nullable=False)

    trigger_date = Column(Date, nullable=False)
    is_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
