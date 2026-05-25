"""
Frontend page for managing plant irrigation.

Key Point:
Provides an interface for users to check watering status, water individual plants,
or water all plants that are currently due.

Responsibilities:
- Display the current watering status of all plants.
- List plants that are due for watering ("Due" section).
- List plants that are currently watered ("Current" section).
- Allow users to manually mark individual plants as watered.
- Provide a "Water all due" button to water all plants that need it.
- Display success or error messages related to irrigation actions.
- Trigger data refresh upon any irrigation action.

Architecture Role:
- User interface component for irrigation management.
- Interacts with the backend API to update plant watering records.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (irrigation.py for backend calls), State management (for data refresh).
- Called by: Streamlit application routing.

Data Flow:
User navigates to irrigation page
        ↓
Frontend fetches watering status of all plants from session state
        ↓
Plants are categorized into "Due" and "Current" and displayed
        ↓
User clicks "Water" for a plant or "Water all due"
        ↓
API call to `water_plant` or `water_all_due`
        ↓
Backend updates plant watering records
        ↓
Frontend receives response, updates session state, and re-renders
"""

# frontend/pages/irrigation.py


import streamlit as st

from api.irrigation import water_all_due, water_plant
from state import refresh_data
from utils.formatting import format_date


def render_irrigation() -> None:
    """
    Renders the irrigation management page.
    Allows users to check watering status, water individual plants, or water all due plants.
    """
    st.subheader("Irrigation")

    cols = st.columns([1, 1, 3])

    if cols[0].button("Check watering", use_container_width=True):
        st.session_state.irrigation_message = ""
        refresh_data(show_errors=True)
        st.rerun()

    if cols[1].button("Water all due", use_container_width=True):
        try:
            result = water_all_due()
            watered_count = result.get("count", 0) if isinstance(result, dict) else 0
            st.session_state.irrigation_message = f"{watered_count} plant(s) watered. All due watering tasks are now cleared."
            refresh_data(show_errors=True)
            st.rerun()
        except RuntimeError as exc:
            st.error(str(exc))

    if st.session_state.get("irrigation_message"):
        st.success(st.session_state.irrigation_message)

    needs_water = st.session_state.get("needs_water", [])

    if not needs_water:
        plants = st.session_state.get("plants", [])

        if plants:
            st.success("All plants are current. No plants need watering right now.")
        else:
            st.info("No plants are available for irrigation tracking yet.")

        return

    due = [item for item in needs_water if item.get("needs_water")]
    not_due = [item for item in needs_water if not item.get("needs_water")]

    left, right = st.columns(2)

    with left:
        st.markdown("#### Due")

        if not due:
            st.caption("All plants are current.")

        for item in due:
            with st.container(border=True):
                st.write(f"**{item.get('name')}**")
                st.caption(f"Every {item.get('watering_interval_days') or 'unknown'} days. " f"Last watered: {format_date(item.get('last_watered'))}")

                if st.button("Mark watered", key=f"due_water_{item['plant_id']}"):
                    try:
                        water_plant(item["plant_id"])
                        st.session_state.irrigation_message = f"{item.get('name')} was marked as watered."
                        refresh_data(show_errors=True)
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))

    with right:
        st.markdown("#### Current")

        for item in not_due:
            with st.container(border=True):
                st.write(f"**{item.get('name')}**")
                st.caption(f"Last watered: {format_date(item.get('last_watered'))}")
