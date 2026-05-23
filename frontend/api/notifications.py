# frontend/api/notifications.py
# Notification API helpers.
# - Loads notification list.
# - Marks notifications as read.

from typing import Any

from api.client import api_request


def get_notifications() -> list[dict[str, Any]]:
    return api_request("GET", "/notifications/") or []


def mark_notification_read(notification_id: int) -> dict[str, Any]:
    return api_request("PUT", f"/notifications/{notification_id}/read")
