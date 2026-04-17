from sqlalchemy.orm import Session
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
        type="irrigation"
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


# ===============================
# GET USER NOTIFICATIONS
# ===============================
def get_notifications(db: Session, user_id: int):
    return db.query(Notification).filter(
        Notification.user_id == user_id
    ).order_by(Notification.created_at.desc()).all()


# ===============================
# MARK AS READ
# ===============================
def mark_as_read(db: Session, notification_id: int, user_id: int):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id
    ).first()

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
    from datetime import date

    today = date.today()

    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.plant_id == plant_id,
        Notification.created_at >= today
    ).first() is not None
