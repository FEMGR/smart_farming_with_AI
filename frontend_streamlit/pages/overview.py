"""
Frontend page for displaying a system overview.

Key Point:
Provides a summary of key metrics, watering tasks, recent notifications, and a visual representation of the saved plant layout.

Responsibilities:
- Display metrics for total plants, locations, plants needing water, and unread alerts.
- Show a "Watering Queue" with plants due for watering and allow users to mark them as watered.
- Present "Recent Notifications" with their read status and messages.
- Render a tabular representation of the saved plant layout, if available.
- Handle user interactions like watering a plant, triggering data refresh.

Architecture Role:
- Dashboard-like component providing a quick glance at the system's status.
- Aggregates and displays data from various parts of the application.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (irrigation.py for watering), State management (for data refresh).
- Called by: Streamlit application routing.

Data Flow:
Session state data (plants, locations, notifications, needs_water)
        ↓
Metrics calculated and displayed
        ↓
Watering queue and notifications filtered and rendered
        ↓
User waters a plant
        ↓
API call to `water_plant`
        ↓
Backend updates plant status
        ↓
Frontend receives response, refreshes local data, and re-renders
"""

# frontend_streamlit/pages/overview.py

import streamlit as st

from api.irrigation import water_plant
from state import refresh_data
from utils.formatting import display_plant_name, format_date


def _has_saved_layout_position(plant: dict) -> bool:
    return plant.get("group_id") is not None and plant.get("bed_x") is not None and plant.get("bed_y") is not None


def _render_saved_layout_content(plants: list[dict]) -> None:
    saved_plants = [plant for plant in plants if _has_saved_layout_position(plant)]

    if not saved_plants:
        st.caption("No saved layout positions yet.")
        return

    placement_map = {(int(plant.get("bed_x") or 0), int(plant.get("bed_y") or 0)): plant for plant in saved_plants}
    max_x = max(int(plant.get("bed_x") or 0) for plant in saved_plants)
    max_y = max(int(plant.get("bed_y") or 0) for plant in saved_plants)

    table_rows = []

    for y in range(max_y + 1):
        row = {"Row": y + 1}

        for x in range(max_x + 1):
            plant = placement_map.get((x, y))
            row[f"Bed {x + 1}"] = display_plant_name(str(plant.get("name") or "Plant")) if plant else ""

        table_rows.append(row)

    st.table(table_rows)


def render_overview() -> None:
    plants = st.session_state.get("plants", [])
    locations = st.session_state.get("locations", [])
    notifications = st.session_state.get("notifications", [])
    needs_water = st.session_state.get("needs_water", [])

    if "overview_expanded_accordion" not in st.session_state:
        st.session_state["overview_expanded_accordion"] = "watering"

    metric_cols = st.columns(4)
    metric_cols[0].metric("Plants", len(plants))
    metric_cols[1].metric("Locations", len(locations))
    metric_cols[2].metric("Need Water", len([p for p in needs_water if p.get("needs_water")]))
    metric_cols[3].metric("Unread Alerts", len([n for n in notifications if not n.get("is_read")]))

    st.subheader("Overview Accordion Dashboard")

    due_plants = [plant for plant in needs_water if plant.get("needs_water")]
    total_water_tasks = len(needs_water) or len(plants) or 1
    finished_water_tasks = max(0, total_water_tasks - len(due_plants))
    water_progress = min(1.0, max(0.0, finished_water_tasks / total_water_tasks))

    unread_notifications = [n for n in notifications if not n.get("is_read")]
    total_notifications = len(notifications) or 1
    read_notifications = total_notifications - len(unread_notifications)
    notification_progress = min(1.0, max(0.0, read_notifications / total_notifications))

    saved_plants = [plant for plant in plants if _has_saved_layout_position(plant)]
    total_plants = len(plants) or 1
    layout_progress = min(1.0, max(0.0, len(saved_plants) / total_plants))

    accordion_items = [
        {
            "id": "watering",
            "title": "Watering Queue",
            "due": f"Due Today: {len(due_plants)} pending",
            "finished_count": finished_water_tasks,
            "total_count": total_water_tasks,
            "progress": water_progress,
            "type": "watering",
        },
        {
            "id": "notifications",
            "title": "Recent Notifications",
            "due": f"Alerts: {len(unread_notifications)} unread",
            "finished_count": read_notifications,
            "total_count": total_notifications,
            "progress": notification_progress,
            "type": "notifications",
        },
        {
            "id": "layout",
            "title": "Saved Bed Layout",
            "due": "Active Layout",
            "finished_count": len(saved_plants),
            "total_count": total_plants,
            "progress": layout_progress,
            "type": "layout",
        },
    ]

    for item in accordion_items:
        sec_id = item["id"]
        is_open = st.session_state.get("overview_expanded_accordion") == sec_id
        arrow_icon = "▲" if is_open else "▼"

        st.markdown('<div class="farm-panel" style="margin-bottom: 12px; padding: 16px;">', unsafe_allow_html=True)
        col_title, col_due, col_progress, col_arrow = st.columns([3, 2, 4, 1])

        with col_title:
            st.markdown(f"### {item['title']}")

        with col_due:
            st.markdown(f"**Deadline / Due:**<br>`{item['due']}`", unsafe_allow_html=True)

        with col_progress:
            st.markdown(f"**Tasks:** {item['finished_count']} / {item['total_count']} finished ({int(item['progress'] * 100)}%)")
            st.progress(item["progress"])

        with col_arrow:
            if st.button(arrow_icon, key=f"btn_acc_{sec_id}", help=f"Toggle {item['title']}"):
                if is_open:
                    st.session_state["overview_expanded_accordion"] = None
                else:
                    st.session_state["overview_expanded_accordion"] = sec_id
                st.rerun()

        if is_open:
            st.divider()
            if item["type"] == "watering":
                if not due_plants:
                    st.caption("No plants are currently due for watering.")
                else:
                    for item_plant in due_plants[:6]:
                        cols = st.columns([2, 1])
                        cols[0].write(f"**{item_plant.get('name')}**")
                        cols[0].caption(f"Last watered: {format_date(item_plant.get('last_watered'))}")

                        if cols[1].button("Water", key=f"overview_water_{item_plant['plant_id']}", width="stretch"):
                            try:
                                water_plant(item_plant["plant_id"])
                                refresh_data(show_errors=True)
                                st.rerun()
                            except RuntimeError as exc:
                                st.error(str(exc))
            elif item["type"] == "notifications":
                if not notifications:
                    st.caption("No notifications yet.")
                else:
                    for notification in notifications[:5]:
                        status = "Unread" if not notification.get("is_read") else "Read"
                        st.write(f"**[{status}]** {notification.get('message', '')}")
                        st.caption(f"Timestamp: {format_date(notification.get('created_at'))}")
            elif item["type"] == "layout":
                _render_saved_layout_content(plants)

        st.markdown("</div>", unsafe_allow_html=True)
