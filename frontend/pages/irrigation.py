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
    st.subheader("Irrigation Management")

    if "irrigation_expanded_accordion" not in st.session_state:
        st.session_state["irrigation_expanded_accordion"] = "due"

    cols = st.columns([1, 1, 3])

    if cols[0].button("Check watering", width="stretch"):
        st.session_state.irrigation_message = ""
        refresh_data(show_errors=True)
        st.rerun()

    if cols[1].button("Water all due", width="stretch"):
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
    due = [item for item in needs_water if item.get("needs_water")]
    not_due = [item for item in needs_water if not item.get("needs_water")]

    total_tasks = len(needs_water) or 1
    finished_tasks = len(not_due)
    progress_ratio = min(1.0, max(0.0, finished_tasks / total_tasks))

    accordion_items = [
        {
            "id": "due",
            "title": "Pending Irrigation (Due)",
            "due": f"Due: {len(due)} pending",
            "finished_count": finished_tasks,
            "total_count": total_tasks,
            "progress": progress_ratio,
            "type": "due",
        },
        {
            "id": "current",
            "title": "Current & Hydrated Plants",
            "due": f"Hydrated: {len(not_due)} plants",
            "finished_count": len(not_due),
            "total_count": total_tasks,
            "progress": 1.0 if not due else progress_ratio,
            "type": "current",
        },
    ]

    for item in accordion_items:
        sec_id = item["id"]
        is_open = st.session_state.get("irrigation_expanded_accordion") == sec_id
        arrow_icon = "▲" if is_open else "▼"

        st.markdown('<div class="farm-panel" style="margin-bottom: 12px; padding: 16px;">', unsafe_allow_html=True)
        col_title, col_due, col_progress, col_arrow = st.columns([3, 2, 4, 1])

        with col_title:
            st.markdown(f"### {item['title']}")

        with col_due:
            st.markdown(f"**Deadline / Status:**<br>`{item['due']}`", unsafe_allow_html=True)

        with col_progress:
            st.markdown(f"**Tasks:** {item['finished_count']} / {item['total_count']} ({int(item['progress'] * 100)}%)")
            st.progress(item["progress"])

        with col_arrow:
            if st.button(arrow_icon, key=f"btn_acc_irr_{sec_id}", help=f"Toggle {item['title']}"):
                if is_open:
                    st.session_state["irrigation_expanded_accordion"] = None
                else:
                    st.session_state["irrigation_expanded_accordion"] = sec_id
                st.rerun()

        if is_open:
            st.divider()
            if item["type"] == "due":
                if not due:
                    st.success("All plants are current. No plants need watering right now.")
                else:
                    for item_plant in due:
                        with st.container(border=True):
                            st.write(f"**{item_plant.get('name')}**")
                            st.caption(
                                f"Every {item_plant.get('watering_interval_days') or 'unknown'} "
                                f"days. Last watered: {format_date(item_plant.get('last_watered'))}"
                            )

                            if st.button("Mark watered", key=f"due_water_{item_plant['plant_id']}"):
                                try:
                                    water_plant(item_plant["plant_id"])
                                    st.session_state.irrigation_message = f"{item_plant.get('name')} was marked as watered."
                                    refresh_data(show_errors=True)
                                    st.rerun()
                                except RuntimeError as exc:
                                    st.error(str(exc))
            elif item["type"] == "current":
                if not not_due:
                    st.caption("No plants currently marked as hydrated.")
                else:
                    for item_plant in not_due:
                        with st.container(border=True):
                            st.write(f"**{item_plant.get('name')}**")
                            st.caption(f"Last watered: {format_date(item_plant.get('last_watered'))}")

        st.markdown("</div>", unsafe_allow_html=True)
