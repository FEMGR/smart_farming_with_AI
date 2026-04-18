"""
Route layer for FastAPI (Notifications).

Key Point:
Handles API endpoints for user notifications.

Responsibilities:
- Receive notification-related requests
- Retrieve or update notification data
- Call notification service layer
- Return notification responses

Architecture Role:
- Entry point for notification handling
- Delegates logic to notification service

Layer Interaction:
- Communicates with: Services (notification_service), Dependencies

Data Flow:
Client Request (notification action)
        ↓
Route receives request
        ↓
Service processes notification logic
        ↓
Database accessed via models
        ↓
Response returned to client
"""

#app.api.routes.notifications.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.api.dependencies import get_current_user_id
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
