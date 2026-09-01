"""
Frontend page for managing growing locations.

Key Point:
Allows users to create, view, and edit details of their growing locations.

Responsibilities:
- Display a form for adding new locations.
- List existing locations with their details.
- Provide an interface for editing location metadata (name, description, environment type).
- Handle form submissions for creating and updating locations.
- Trigger data refresh and invalidate recommendations upon successful updates.

Architecture Role:
- User interface component for location management.
- Interacts with the backend API to persist location data.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (locations.py for backend calls), State management (for data refresh).
- Called by: Streamlit application routing.

Data Flow:
User input for new/edited location details
        ↓
Frontend form captures input
        ↓
API call to `create_location` or `update_location`
        ↓
Backend processes request and updates database
        ↓
Frontend receives response, refreshes local data, and re-renders
"""

# frontend_streamlit/pages/locations.py


import streamlit as st

from api.locations import create_location, delete_location, update_location
from config import ENVIRONMENT_TYPES
from state import invalidate_recommendations, refresh_data
from utils.formatting import format_date


def render_locations() -> None:
    st.subheader("Locations Management")

    if "locations_expanded_accordion" not in st.session_state:
        st.session_state["locations_expanded_accordion"] = "list"

    locations = st.session_state.get("locations", [])
    total_locations = len(locations) or 1
    progress_ratio = min(1.0, max(0.0, len(locations) / total_locations))

    accordion_items = [
        {
            "id": "list",
            "title": "Growing Locations",
            "due": f"Active: {len(locations)} locations",
            "finished_count": len(locations),
            "total_count": total_locations,
            "progress": progress_ratio,
            "type": "list",
        },
        {
            "id": "add",
            "title": "Create New Location",
            "due": "Form Ready",
            "finished_count": 0,
            "total_count": 1,
            "progress": 0.0,
            "type": "add",
        },
    ]

    for item in accordion_items:
        sec_id = item["id"]
        is_open = st.session_state.get("locations_expanded_accordion") == sec_id
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
            if st.button(arrow_icon, key=f"btn_acc_loc_{sec_id}", help=f"Toggle {item['title']}"):
                if is_open:
                    st.session_state["locations_expanded_accordion"] = None
                else:
                    st.session_state["locations_expanded_accordion"] = sec_id
                st.rerun()

        if is_open:
            st.divider()
            if item["type"] == "add":
                with st.form("create_location"):
                    name = st.text_input("Name", placeholder="Balcony, backyard, greenhouse shelf")
                    description = st.text_area("Description", height=80)
                    environment_type = st.selectbox("Environment", ENVIRONMENT_TYPES)
                    col1, col2 = st.columns(2)
                    with col1:
                        width_m = st.number_input("Width (m)", min_value=0.1, value=5.0, step=0.1)
                    with col2:
                        length_m = st.number_input("Length (m)", min_value=0.1, value=5.0, step=0.1)
                    submitted = st.form_submit_button("Create location")

                if submitted:
                    try:
                        create_location(
                            {
                                "name": name,
                                "description": description or None,
                                "environment_type": environment_type,
                                "width_m": width_m,
                                "length_m": length_m,
                            }
                        )
                        refresh_data(show_errors=True)
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))

            elif item["type"] == "list":
                if not locations:
                    st.info("Create a location before assigning plants.")
                else:
                    for location in locations:
                        with st.container(border=True):
                            cols = st.columns([2, 1, 1])

                            cols[0].write(f"**{location.get('name')}**")
                            cols[0].caption(location.get("description") or "No description")
                            cols[1].write(location.get("environment_type") or "unspecified")
                            cols[1].caption(f"{location.get('width_m') or '-'} m x {location.get('length_m') or '-'} m")
                            cols[2].caption(f"Created {format_date(location.get('created_at'))}")

                            with st.expander("Edit location"):
                                with st.form(f"edit_location_{location['id']}"):
                                    new_name = st.text_input("Name", value=location.get("name") or "")
                                    new_description = st.text_area(
                                        "Description",
                                        value=location.get("description") or "",
                                        height=80,
                                    )
                                    new_environment = st.selectbox(
                                        "Environment",
                                        ENVIRONMENT_TYPES,
                                        index=(
                                            ENVIRONMENT_TYPES.index(location.get("environment_type"))
                                            if location.get("environment_type") in ENVIRONMENT_TYPES
                                            else 0
                                        ),
                                    )
                                    edit_col1, edit_col2 = st.columns(2)
                                    with edit_col1:
                                        new_width = st.number_input(
                                            "Width (m)",
                                            min_value=0.1,
                                            value=float(location.get("width_m") or 5.0),
                                            step=0.1,
                                            key=f"edit_location_width_{location['id']}",
                                        )
                                    with edit_col2:
                                        new_length = st.number_input(
                                            "Length (m)",
                                            min_value=0.1,
                                            value=float(location.get("length_m") or 5.0),
                                            step=0.1,
                                            key=f"edit_location_length_{location['id']}",
                                        )
                                    save = st.form_submit_button("Save")

                                if save:
                                    try:
                                        update_location(
                                            location["id"],
                                            {
                                                "name": new_name,
                                                "description": new_description or None,
                                                "environment_type": new_environment,
                                                "width_m": new_width,
                                                "length_m": new_length,
                                            },
                                        )
                                        invalidate_recommendations()
                                        refresh_data(show_errors=True)
                                        st.rerun()
                                    except RuntimeError as exc:
                                        st.error(str(exc))

                            with st.expander("Delete location"):
                                confirm_delete = st.checkbox(
                                    f"Delete {location.get('name')}",
                                    key=f"confirm_delete_location_{location['id']}",
                                )

                                if st.button(
                                    "Delete location",
                                    key=f"delete_location_{location['id']}",
                                    disabled=not confirm_delete,
                                    width="stretch",
                                ):
                                    try:
                                        delete_location(location["id"])
                                        invalidate_recommendations()
                                        refresh_data(show_errors=True)
                                        st.rerun()
                                    except RuntimeError as exc:
                                        st.error(str(exc))

        st.markdown("</div>", unsafe_allow_html=True)
