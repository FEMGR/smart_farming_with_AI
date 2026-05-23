# frontend/pages/notifications.py
# Notifications page.
# - Lists backend alerts.
# - Marks unread notifications as read.

import streamlit as st

from api.notifications import mark_notification_read
from state import refresh_data
from utils.formatting import format_date


def render_notifications() -> None:
    st.subheader("Notifications")

    notifications = st.session_state.get("notifications", [])

    if not notifications:
        st.info("No notifications yet.")
        return

    for notification in notifications:
        with st.container(border=True):
            cols = st.columns([3, 1, 1])

            cols[0].write(f"**{notification.get('type', 'notification').title()}**")
            cols[0].caption(notification.get("message", ""))

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
