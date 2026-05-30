# app/schemas/notification_schema.py

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PlanningNotificationCreate(BaseModel):
    batch_id: Optional[int] = None
    crop_plan_id: Optional[int] = None
    notification_type: str
    message: str
    trigger_date: date


class PlanningNotificationResponse(PlanningNotificationCreate):
    id: int
    user_id: int
    is_sent: bool
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
