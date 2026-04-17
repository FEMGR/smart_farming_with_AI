from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.api.deps import get_current_user_id
from app.services import notification_service

router = APIRouter()


# ===============================
# GET NOTIFICATIONS
# ===============================
@router.get("/")
def get_notifications(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return notification_service.get_notifications(db, user_id)


# ===============================
# MARK AS READ
# ===============================
@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    notification = notification_service.mark_as_read(
        db,
        notification_id,
        user_id
    )

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    return {"message": "Notification marked as read"}
