"""
Service layer for FastAPI (Notifications).

Key Point:
Handles business logic for generating and managing notifications.

Responsibilities:
- Create and store notifications
- Retrieve user notifications
- Mark notifications as read
- Trigger alerts based on system events

Architecture Role:
- Core logic layer for notification system
- Connects system events to user-facing alerts

Layer Interaction:
- Communicates with: Models (notification), Database
- Called by: Routes, Services (e.g., irrigation_service)

Data Flow:
Trigger event received (e.g., irrigation alert)
        ↓
Notification created
        ↓
Stored in database
        ↓
Retrieved when requested by route
        ↓
Returned to client
"""

# app.services.notification_service.py

from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.models.notification import Notification
from app.models.plant import Plant


# ===============================
# CREATE NOTIFICATION
# ===============================
def create_notification(db: Session, user_id: int, plant: Plant, message: str):
    notification = Notification(
        user_id=user_id,
        plant_id=plant.id,
        message=message,
        type="irrigation",
    )

    db.add(notification)
    db.flush()  # db.commit()
    db.refresh(notification)

    return notification


# ===============================
# GET USER NOTIFICATIONS
# ===============================
def get_notifications(db: Session, user_id: int):
    notifications = (
        db.query(Notification).options(joinedload(Notification.plant)).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()
    )

    return [
        {
            "id": notification.id,
            "user_id": notification.user_id,
            "plant_id": notification.plant_id,
            "message": notification.message,
            "type": notification.type,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
            "plant": (
                {
                    "id": notification.plant.id,
                    "name": notification.plant.name,
                    "bed_x": notification.plant.bed_x,
                    "bed_y": notification.plant.bed_y,
                }
                if notification.plant
                else None
            ),
        }
        for notification in notifications
    ]


# ===============================
# MARK AS READ
# ===============================
def mark_as_read(db: Session, notification_id: int, user_id: int):
    notification = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()

    if not notification:
        return None

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification


# ===============================
# PREVENT DUPLICATES (IMPORTANT)
# ===============================
def notification_exists_today(db: Session, user_id: int, plant_id: int):
    today = date.today()
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.plant_id == plant_id,
            Notification.created_at >= today,
        )
        .first()
        is not None
    )
