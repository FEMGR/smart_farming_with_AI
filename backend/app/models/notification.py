"""
Database model for Notification.

Key Point:
Represents system-generated notifications for users.

Responsibilities:
- Store notification messages
- Track read/unread status
- Associate notifications with users and events

Architecture Role:
- Enables communication of system events to users

Layer Interaction:
- Used by: Services, Database layer

Notes:
- Triggered by system events (e.g., irrigation alerts)
"""

#app.models.notification.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database.db import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    plant_id = Column(Integer, ForeignKey("plants.id", ondelete="CASCADE"))
    message = Column(String, nullable=False)
    type = Column(String(50), default="irrigation")
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="notifications")
    plant = relationship("Plant", back_populates="notifications")
