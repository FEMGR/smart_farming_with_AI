# frontend/pages/overview.py
# Overview page.
# - Shows dashboard metrics, watering queue, recent notifications.
# - Displays the current saved bed layout.

import streamlit as st

from api.irrigation import water_plant
from state import refresh_data
from utils.formatting import display_plant_name, format_date


def _has_saved_layout_position(plant: dict) -> bool:
    return plant.get("group_id") is not None and plant.get("bed_x") is not None and plant.get("bed_y") is not None


def _render_saved_layout(plants: list[dict]) -> None:
    saved_plants = [plant for plant in plants if _has_saved_layout_position(plant)]

    st.subheader("Saved Layout")

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

    metric_cols = st.columns(4)
    metric_cols[0].metric("Plants", len(plants))
    metric_cols[1].metric("Locations", len(locations))
    metric_cols[2].metric("Need Water", len([p for p in needs_water if p.get("needs_water")]))
    metric_cols[3].metric("Unread Alerts", len([n for n in notifications if not n.get("is_read")]))

    st.subheader("Today")
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="farm-panel">', unsafe_allow_html=True)
        st.markdown("#### Watering Queue")

        due = [plant for plant in needs_water if plant.get("needs_water")]

        if not due:
            st.caption("No plants are currently due for watering.")

        for item in due[:6]:
            cols = st.columns([2, 1])
            cols[0].write(f"**{item.get('name')}**")
            cols[0].caption(f"Last watered: {format_date(item.get('last_watered'))}")

            if cols[1].button("Water", key=f"overview_water_{item['plant_id']}", use_container_width=True):
                try:
                    water_plant(item["plant_id"])
                    refresh_data(show_errors=True)
                    st.rerun()
                except RuntimeError as exc:
                    st.error(str(exc))

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="farm-panel">', unsafe_allow_html=True)
        st.markdown("#### Recent Notifications")

        if not notifications:
            st.caption("No notifications yet.")

        for notification in notifications[:5]:
            status = "Unread" if not notification.get("is_read") else "Read"
            st.write(f"**{status}**")
            st.caption(notification.get("message", ""))

        st.markdown("</div>", unsafe_allow_html=True)

    _render_saved_layout(plants)
