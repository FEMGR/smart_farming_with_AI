"""
API client for notification-related operations in the Smart Urban Farming application.

Key Point:
Provides functions to interact with the backend's notification endpoints,
allowing the frontend to retrieve user notifications and mark them as read.

Responsibilities:
- Abstract the API endpoint paths and HTTP methods for notification operations.
- Facilitate data exchange for fetching notifications and updating their read status.

Architecture Role:
- Acts as a dedicated interface for the frontend to manage notification data on the backend.
- Simplifies API calls for notification features.

Layer Interaction:
- Communicates with: `api.client.api_request` (for underlying HTTP requests).
- Called by: Frontend components that display user notifications.

Data Flow:
Frontend UI needs to display user notifications
        ↓
`get_notifications()` is called
        ↓
`api_request()` sends a GET request to the backend `/notifications/` endpoint
        ↓
Backend processes the request and returns a list of notifications
        ↓
List of notifications is returned to the frontend UI for display

User marks a notification as read
        ↓
`mark_notification_read()` is called
        ↓
`api_request()` sends a PUT request to the backend `/notifications/{notification_id}/read` endpoint
        ↓
Backend updates the notification's status
        ↓
Confirmation message or updated data is returned to the frontend UI
"""

# frontend/api/notifications.py

from typing import Any

from api.client import api_request


def get_notifications() -> list[dict[str, Any]]:
    return api_request("GET", "/notifications/") or []


def mark_notification_read(notification_id: int) -> dict[str, Any]:
    return api_request("PUT", f"/notifications/{notification_id}/read")
