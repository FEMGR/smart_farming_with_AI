# frontend/pages/locations.py
# Locations page.
# - Creates growing locations.
# - Edits location metadata and dimensions used by layout capacity.

import streamlit as st

from api.locations import create_location, update_location
from config import ENVIRONMENT_TYPES
from state import invalidate_recommendations, refresh_data
from utils.formatting import format_date


def render_locations() -> None:
    st.subheader("Locations")

    with st.expander("Add location", expanded=not st.session_state.get("locations")):
        with st.form("create_location"):
            name = st.text_input("Name", placeholder="Balcony, backyard, greenhouse shelf")
            description = st.text_area("Description", height=80)
            environment_type = st.selectbox("Environment", ENVIRONMENT_TYPES)
            submitted = st.form_submit_button("Create location")

        if submitted:
            try:
                create_location(
                    {
                        "name": name,
                        "description": description or None,
                        "environment_type": environment_type,
                    }
                )
                refresh_data(show_errors=True)
                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))

    locations = st.session_state.get("locations", [])

    if not locations:
        st.info("Create a location before assigning plants.")
        return

    for location in locations:
        with st.container(border=True):
            cols = st.columns([2, 1, 1])

            cols[0].write(f"**{location.get('name')}**")
            cols[0].caption(location.get("description") or "No description")
            cols[1].write(location.get("environment_type") or "unspecified")
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
                        index=ENVIRONMENT_TYPES.index(location.get("environment_type")) if location.get("environment_type") in ENVIRONMENT_TYPES else 0,
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
                            },
                        )
                        invalidate_recommendations()
                        refresh_data(show_errors=True)
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))
