"""
Frontend page for displaying and managing user notifications.

Key Point:
Allows users to view a list of their notifications and mark them as read.

Responsibilities:
- Fetch and display all notifications for the current user.
- Show notification details including type, message, and creation date.
- Provide a button to mark unread notifications as read.
- Trigger data refresh upon marking a notification as read.

Architecture Role:
- User interface component for notification management.
- Interacts with the backend API to update notification status.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (notifications.py for backend calls), State management (for data refresh).
- Called by: Streamlit application routing.

Data Flow:
User navigates to notifications page
        ↓
Frontend fetches notifications from session state
        ↓
Notifications are displayed in a list
        ↓
User clicks "Mark read" for an unread notification
        ↓
API call to `mark_notification_read`
        ↓
Backend updates notification status in the database
        ↓
Frontend receives response, refreshes local data, and re-renders
"""

# frontend/pages/notifications.py


import streamlit as st

from api.notifications import mark_notification_read
from state import refresh_data
from utils.formatting import format_date


def _notification_location_label(notification: dict) -> str:
    plant = notification.get("plant") or {}
    bed_x = plant.get("bed_x")
    bed_y = plant.get("bed_y")
    location = plant.get("location") or {}
    location_name = location.get("name")

    parts = []
    if bed_x is not None and bed_y is not None:
        parts.append(f"Bed {int(bed_x) + 1} Row {int(bed_y) + 1}")

    if location_name:
        parts.append(location_name)

    if parts:
        return " • ".join(parts)

    return notification.get("type", "notification").title()


def render_notifications() -> None:
    """
    Renders the notifications page, displaying a list of user notifications
    and allowing them to be marked as read.
    """
    st.subheader("Notifications")

    notifications = st.session_state.get("notifications", [])

    if not notifications:
        st.info("No notifications yet.")
        return

    for notification in notifications:
        with st.container(border=True):
            cols = st.columns([3, 1, 1])

            cols[0].write(f"**{notification.get('message', '')}**")
            cols[0].caption(_notification_location_label(notification))

            cols[1].write("Unread" if not notification.get("is_read") else "Read")
            cols[1].caption(format_date(notification.get("created_at")))

            if not notification.get("is_read") and cols[2].button(
                "Mark read",
                key=f"read_{notification['id']}",
                use_container_width=True,
            ):
                try:
                    mark_notification_read(notification["id"])
                    refresh_data(show_errors=True)
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))
