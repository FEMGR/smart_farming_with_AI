"""
Frontend page for managing individual plant records.

Key Point:
Allows users to create, view, edit, duplicate, and delete their plant entries,
including associating them with species and locations, and managing watering settings.

Responsibilities:
- Display a form for adding new plants, optionally linking to a species.
- List existing plants with their key details (type, location, watering).
- Provide quick actions like watering and duplicating plants.
- Offer an expandable section for editing plant details.
- Handle form submissions for creating, updating, and deleting plants.
- Trigger data refresh and invalidate recommendations upon successful changes.

Architecture Role:
- User interface component for detailed plant management.
- Interacts with the backend API for all plant-related CRUD operations.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (plants.py, irrigation.py for backend calls), State management (for data refresh).
- Called by: Streamlit application routing.

Data Flow:
User input for new/edited plant details
        ↓
Frontend form captures input
        ↓
API call to `create_plant`, `create_plant_with_species`, `update_plant`, `delete_plant`, `water_plant`, or `duplicate_plant`
        ↓
Backend processes request and updates database
        ↓
Frontend receives response, refreshes local data, and re-renders
"""

# frontend_streamlit/pages/plants.py


from datetime import date

import streamlit as st

from api.irrigation import water_plant
from config import PLANT_TYPES
from state import invalidate_recommendations, refresh_data
from utils.formatting import format_date, location_options, plant_display_name
from api.plants import (
    create_plant,
    create_plant_with_species,
    delete_plant,
    duplicate_plant,
    update_plant,
)


def render_plants() -> None:
    """
    Renders the plants management page, allowing users to add, view, edit,
    duplicate, and delete their plant records.
    """
    st.subheader("Plants Management")

    if "plants_expanded_accordion" not in st.session_state:
        st.session_state["plants_expanded_accordion"] = "list"

    plants = st.session_state.get("plants", [])
    needs_water = st.session_state.get("needs_water", [])
    due_count = len([p for p in needs_water if p.get("needs_water")])
    total_plants = len(plants) or 1
    active_ratio = min(1.0, max(0.0, len(plants) / total_plants))

    accordion_items = [
        {
            "id": "list",
            "title": "My Crops & Plants",
            "due": f"Due: {due_count} need water",
            "finished_count": len(plants),
            "total_count": total_plants,
            "progress": active_ratio,
            "type": "list",
        },
        {
            "id": "add",
            "title": "Add New Plant",
            "due": "Form Ready",
            "finished_count": 0,
            "total_count": 1,
            "progress": 0.0,
            "type": "add",
        },
    ]

    for item in accordion_items:
        sec_id = item["id"]
        is_open = st.session_state.get("plants_expanded_accordion") == sec_id
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
            if st.button(arrow_icon, key=f"btn_acc_plants_{sec_id}", help=f"Toggle {item['title']}"):
                if is_open:
                    st.session_state["plants_expanded_accordion"] = None
                else:
                    st.session_state["plants_expanded_accordion"] = sec_id
                st.rerun()

        if is_open:
            st.divider()
            if item["type"] == "add":
                location_labels, location_ids = location_options()

                with st.form("create_plant"):
                    name = st.text_input("Plant name", placeholder="Tomato")
                    species_name = st.text_input("Scientific name override", placeholder="Solanum lycopersicum")
                    plant_type = st.selectbox("Plant type", PLANT_TYPES)
                    selected_location = st.selectbox("Location", location_labels)

                    set_planting_date = st.checkbox("Set planting date")
                    planting_date = st.date_input(
                        "Planting date",
                        value=date.today(),
                        disabled=not set_planting_date,
                    )

                    use_sensor = st.checkbox("Uses sensor")
                    watering_interval = st.number_input(
                        "Watering interval override",
                        min_value=0,
                        max_value=60,
                        value=0,
                    )

                    species_id = st.number_input("Perenual species ID", min_value=0, value=0)
                    submitted = st.form_submit_button("Create plant")

                if submitted:
                    payload = {
                        "name": name,
                        "plant_type": plant_type,
                        "species_name": species_name.strip() or None,
                        "location_id": location_ids[selected_location],
                        "planting_date": planting_date.isoformat() if set_planting_date else None,
                        "use_sensor": use_sensor,
                        "watering_interval_days": watering_interval or None,
                    }

                    try:
                        if species_id:
                            create_plant_with_species(payload, int(species_id))
                        else:
                            create_plant(payload)

                        invalidate_recommendations()
                        refresh_data(show_errors=True)
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))

            elif item["type"] == "list":
                if not plants:
                    st.info("Add your first plant to begin tracking care.")
                else:
                    for plant in plants:
                        with st.container(border=True):
                            cols = st.columns([2.2, 1.2, 1.2, 1])

                            cols[0].write(f"**{plant_display_name(plant)}**")
                            location = plant.get("location") or {}
                            cols[0].caption(f"ID: {plant.get('id')} · Location: {location.get('name') or 'No location'}")

                            cols[1].write(plant.get("plant_type") or "unknown")
                            cols[1].caption(f"Source: {plant.get('data_source')}")

                            cols[2].write(f"{plant.get('effective_watering_interval', plant.get('watering_interval_days') or 4)} days")
                            cols[2].caption(f"Last watered: {format_date(plant.get('last_watered'))}")

                            identity_parts = [
                                plant.get("plant_atom"),
                                plant.get("scientific_name"),
                                plant.get("genus"),
                            ]
                            identity_text = " · ".join(str(part) for part in identity_parts if part)
                            if identity_text:
                                st.caption(f"Identity: {identity_text}")

                            timeline = plant.get("timeline_snapshot") or {}
                            timeline_events = timeline.get("events") or []
                            if timeline_events:
                                with st.expander("Timeline snapshot"):
                                    guidance = timeline.get("guidance") or {}
                                    if timeline.get("growth_fact_match_level"):
                                        st.caption(
                                            f"Basis: {timeline.get('growth_fact_match_level')} · " f"Confidence: {timeline.get('confidence') or 'unknown'}"
                                        )
                                    if guidance.get("sowing_depth_cm") is not None:
                                        st.write(f"Sowing depth: `{guidance.get('sowing_depth_cm')}` cm")
                                    if guidance.get("germination_days_min") is not None:
                                        st.write("Germination: " f"`{guidance.get('germination_days_min')}`-" f"`{guidance.get('germination_days_max')}` days")

                                    for event in timeline_events:
                                        st.write(f"- {event.get('date')}: {event.get('label')}")

                                    for warning in timeline.get("warnings") or []:
                                        st.warning(warning)

                            quick_cols = st.columns([1, 2])

                            if quick_cols[0].button(
                                "Add same plant",
                                key=f"duplicate_plant_{plant['id']}",
                                width="stretch",
                            ):
                                try:
                                    duplicate = duplicate_plant(plant["id"])
                                    invalidate_recommendations()
                                    refresh_data(show_errors=True)
                                    st.success(f"Added another {plant.get('name')} as plant ID {duplicate.get('id')}.")
                                    st.rerun()
                                except RuntimeError as exc:
                                    st.error(str(exc))

                            if cols[3].button("Water", key=f"water_plant_{plant['id']}", width="stretch"):
                                try:
                                    water_plant(plant["id"])
                                    refresh_data(show_errors=True)
                                    st.rerun()
                                except RuntimeError as exc:
                                    st.error(str(exc))

                            with st.expander("Edit"):
                                location_labels, location_ids = location_options()

                                current_label = "No location"
                                for label, location_id in location_ids.items():
                                    if location_id == plant.get("location_id"):
                                        current_label = label
                                        break

                                with st.form(f"edit_plant_{plant['id']}"):
                                    new_name = st.text_input("Name", value=plant.get("name") or "")
                                    current_species_name = plant.get("scientific_name") or ""
                                    new_species_name = st.text_input(
                                        "Scientific name override",
                                        value=current_species_name,
                                        help="Optional. Example: Fragaria vesca. Only sent when changed.",
                                    )

                                    new_type = st.selectbox(
                                        "Type",
                                        PLANT_TYPES,
                                        index=PLANT_TYPES.index(plant.get("plant_type")) if plant.get("plant_type") in PLANT_TYPES else 0,
                                    )

                                    new_location = st.selectbox(
                                        "Location",
                                        location_labels,
                                        index=location_labels.index(current_label),
                                    )

                                    new_interval = st.number_input(
                                        "Watering interval",
                                        min_value=0,
                                        max_value=60,
                                        value=int(plant.get("watering_interval_days") or 0),
                                    )

                                    new_use_sensor = st.checkbox(
                                        "Uses sensor",
                                        value=bool(plant.get("use_sensor")),
                                    )

                                    save = st.form_submit_button("Save")

                                delete = st.button("Delete plant", key=f"delete_plant_{plant['id']}")

                                if save:
                                    try:
                                        payload = {
                                            "name": new_name,
                                            "plant_type": new_type,
                                            "location_id": location_ids[new_location],
                                            "watering_interval_days": new_interval or None,
                                            "use_sensor": new_use_sensor,
                                        }
                                        payload["species_name"] = new_species_name.strip() or None

                                        update_plant(
                                            plant["id"],
                                            payload,
                                        )

                                        invalidate_recommendations()
                                        refresh_data(show_errors=True)
                                        st.rerun()
                                    except RuntimeError as exc:
                                        st.error(str(exc))

                                if delete:
                                    try:
                                        delete_plant(plant["id"])
                                        invalidate_recommendations()
                                        refresh_data(show_errors=True)
                                        st.rerun()
                                    except RuntimeError as exc:
                                        st.error(str(exc))

        st.markdown("</div>", unsafe_allow_html=True)
