# frontend/pages/planning.py

import streamlit as st

from api import locations as location_api
from api import planning as planning_api


def render_planning_page():
    st.title("Polyculture Production Planning")

    st.caption("Plan compatible crop groups, assign them to farm sections, " "preview timelines, and confirm production batches.")

    tab_sections, tab_preview = st.tabs(["Farm Sections", "Polyculture Preview"])

    with tab_sections:
        render_sections_tab()

    with tab_preview:
        render_polyculture_preview_tab()


def render_sections_tab():
    st.subheader("Create Farm Section")

    locations = location_api.get_locations() or []
    sections = planning_api.get_sections() or []

    if not locations:
        st.warning("Create a location first before adding farm sections.")
        return

    location_options = {f"{loc['name']} (ID {loc['id']})": loc["id"] for loc in locations}
    locations_by_id = {loc["id"]: loc for loc in locations}

    with st.form("create_section_form"):
        selected_location = st.selectbox("Location", list(location_options.keys()))
        selected_location_id = location_options[selected_location]
        selected_location_data = locations_by_id[selected_location_id]
        location_width = selected_location_data.get("width_m")
        location_length = selected_location_data.get("length_m")

        existing_area = sum(float(section.get("area_m2") or 0) for section in sections if section.get("location_id") == selected_location_id)
        location_area = float(location_width) * float(location_length) if location_width is not None and location_length is not None else None
        remaining_area = max(location_area - existing_area, 0) if location_area is not None else None

        if location_area is None:
            st.warning("Set this location's width and length before creating sections.")
        else:
            st.caption(f"Location size: {location_width} m x {location_length} m. " f"Remaining section capacity: {remaining_area:.2f} m².")

        name = st.text_input("Section name", placeholder="Backyard Section A")
        section_type = st.selectbox("Section type", ["production", "nursery", "reserve"])

        col1, col2 = st.columns(2)
        with col1:
            width_m = st.number_input(
                "Width (m)",
                min_value=0.1,
                max_value=float(location_width) if location_width is not None else None,
                value=min(2.0, float(location_width)) if location_width is not None else 2.0,
                step=0.1,
            )
        with col2:
            length_m = st.number_input(
                "Length (m)",
                min_value=0.1,
                max_value=float(location_length) if location_length is not None else None,
                value=min(3.0, float(location_length)) if location_length is not None else 3.0,
                step=0.1,
            )

        submitted = st.form_submit_button("Create section", disabled=location_area is None or remaining_area <= 0)

    if submitted:
        section_area = width_m * length_m

        if remaining_area is not None and section_area > remaining_area:
            st.error(f"Section area exceeds remaining location capacity ({remaining_area:.2f} m² available).")
            return

        payload = {
            "location_id": selected_location_id,
            "name": name,
            "section_type": section_type,
            "width_m": width_m,
            "length_m": length_m,
            "area_m2": section_area,
        }

        result = planning_api.create_section(payload)

        if result:
            st.success("Section created.")
            st.json(result)

    st.divider()
    st.subheader("Existing Sections")

    if not sections:
        st.info("No farm sections yet.")
        return

    for section in sections:
        with st.container(border=True):
            st.write(f"**{section['name']}**")
            st.write(f"ID: `{section['id']}`")
            st.write(f"Location ID: `{section.get('location_id')}`")
            st.write(f"Size: `{section.get('width_m')}` m x `{section.get('length_m')}` m")
            st.write(f"Area: `{section.get('area_m2')}` m²")
            st.write(f"Type: `{section.get('section_type')}`")

            with st.expander("Edit section"):
                edit_location_id = section.get("location_id")
                edit_location_label = next(
                    (label for label, location_id in location_options.items() if location_id == edit_location_id),
                    list(location_options.keys())[0],
                )

                with st.form(f"edit_section_{section['id']}"):
                    new_location_label = st.selectbox(
                        "Location",
                        list(location_options.keys()),
                        index=list(location_options.keys()).index(edit_location_label),
                        key=f"edit_section_location_{section['id']}",
                    )
                    new_location_id = location_options[new_location_label]
                    new_location = locations_by_id[new_location_id]
                    new_location_width = new_location.get("width_m")
                    new_location_length = new_location.get("length_m")

                    other_section_area = sum(
                        float(other.get("area_m2") or 0)
                        for other in sections
                        if other.get("location_id") == new_location_id and other.get("id") != section.get("id")
                    )
                    new_location_area = (
                        float(new_location_width) * float(new_location_length) if new_location_width is not None and new_location_length is not None else None
                    )
                    section_remaining_area = max(new_location_area - other_section_area, 0) if new_location_area is not None else None

                    if section_remaining_area is not None:
                        st.caption(f"Available capacity for this section: {section_remaining_area:.2f} m².")

                    new_name = st.text_input("Section name", value=section.get("name") or "")
                    new_section_type = st.selectbox(
                        "Section type",
                        ["production", "nursery", "reserve"],
                        index=(
                            ["production", "nursery", "reserve"].index(section.get("section_type"))
                            if section.get("section_type") in ["production", "nursery", "reserve"]
                            else 0
                        ),
                        key=f"edit_section_type_{section['id']}",
                    )

                    edit_col1, edit_col2 = st.columns(2)
                    with edit_col1:
                        new_width = st.number_input(
                            "Width (m)",
                            min_value=0.1,
                            max_value=float(new_location_width) if new_location_width is not None else None,
                            value=(
                                min(float(section.get("width_m") or 1.0), float(new_location_width))
                                if new_location_width is not None
                                else float(section.get("width_m") or 1.0)
                            ),
                            step=0.1,
                            key=f"edit_section_width_{section['id']}",
                        )
                    with edit_col2:
                        new_length = st.number_input(
                            "Length (m)",
                            min_value=0.1,
                            max_value=float(new_location_length) if new_location_length is not None else None,
                            value=(
                                min(float(section.get("length_m") or 1.0), float(new_location_length))
                                if new_location_length is not None
                                else float(section.get("length_m") or 1.0)
                            ),
                            step=0.1,
                            key=f"edit_section_length_{section['id']}",
                        )

                    save_section = st.form_submit_button("Save section")

                if save_section:
                    new_area = new_width * new_length

                    if section_remaining_area is not None and new_area > section_remaining_area:
                        st.error(f"Section area exceeds available capacity ({section_remaining_area:.2f} m² available).")
                    else:
                        result = planning_api.update_section(
                            section["id"],
                            {
                                "location_id": new_location_id,
                                "name": new_name,
                                "section_type": new_section_type,
                                "width_m": new_width,
                                "length_m": new_length,
                                "area_m2": new_area,
                            },
                        )

                        if result:
                            st.success("Section updated.")
                            st.rerun()

            with st.expander("Delete section"):
                confirm_delete = st.checkbox(
                    f"Delete {section.get('name')}",
                    key=f"confirm_delete_section_{section['id']}",
                )

                if st.button(
                    "Delete section",
                    key=f"delete_section_{section['id']}",
                    disabled=not confirm_delete,
                    width="stretch",
                ):
                    result = planning_api.delete_section(section["id"])

                    if result:
                        st.success("Section deleted.")
                        st.rerun()


def render_polyculture_preview_tab():
    st.subheader("Generate Polyculture Plan Preview")

    locations = location_api.get_locations() or []
    sections = planning_api.get_sections() or []

    if not locations:
        st.warning("Create a location first.")
        return

    if not sections:
        st.warning("Create at least one farm section first.")
        return

    location_options = {f"{loc['name']} (ID {loc['id']})": loc["id"] for loc in locations}

    selected_location_label = st.selectbox("Location", list(location_options.keys()))
    selected_location_id = location_options[selected_location_label]

    location_sections = [section for section in sections if section.get("location_id") == selected_location_id]

    if not location_sections:
        st.warning("This location has no farm sections yet.")
        return

    section_options = {f"{section['name']} — {section.get('area_m2')} m² (ID {section['id']})": section["id"] for section in location_sections}

    selected_sections = st.multiselect(
        "Sections to use",
        list(section_options.keys()),
        default=list(section_options.keys())[:1],
    )

    crops_text = st.text_area(
        "Intended crops",
        value="cabbage, tomato, carrot, cucumber, lettuce, potato, asparagus",
        help="Separate crops with commas.",
    )

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date")
    with col2:
        harvest_interval_days = st.number_input(
            "Desired harvest interval days",
            min_value=1,
            value=14,
            step=1,
        )

    preview_clicked = st.button("Generate preview", width="stretch")

    if preview_clicked:
        intended_crops = [crop.strip() for crop in crops_text.split(",") if crop.strip()]

        payload = {
            "location_id": selected_location_id,
            "section_ids": [section_options[label] for label in selected_sections],
            "intended_crops": intended_crops,
            "start_date": str(start_date),
            "harvest_interval_days": harvest_interval_days,
        }

        preview = planning_api.polyculture_preview(payload)

        if preview:
            st.session_state["polyculture_preview_payload"] = payload
            st.session_state["polyculture_preview_result"] = preview
            st.success("Preview generated.")

    preview = st.session_state.get("polyculture_preview_result")

    if not preview:
        return

    render_preview_result(preview)

    st.divider()
    plan_name = st.text_input("Plan name", value="Polyculture Production Plan")

    if st.button("Confirm and save plan", width="stretch"):
        payload = st.session_state.get("polyculture_preview_payload", {})
        payload["name"] = plan_name

        result = planning_api.polyculture_confirm(payload)

        if result:
            st.success("Polyculture plan confirmed.")
            st.json(result)


def render_preview_result(preview: dict):
    st.subheader("Preview Result")

    warnings = preview.get("warnings", [])
    if warnings:
        st.warning("Review these planning warnings:")
        for warning in warnings:
            st.write(f"- {warning}")

    suggested_sections = preview.get("suggested_additional_sections", [])
    if suggested_sections:
        st.info("Suggested additional sections:")
        for section in suggested_sections:
            st.write(f"- {section['name']} " f"(ID {section['id']}, {section.get('area_m2')} m²)")

    st.metric("Safe groups", preview.get("group_count", 0))
    st.metric("Total selected area", f"{preview.get('total_available_area_m2')} m²")

    st.divider()
    st.subheader("Generated Groups")

    for group in preview.get("groups", []):
        with st.container(border=True):
            st.write(f"### Group {group.get('group_id')}")
            st.write(f"Section: `{group.get('section_name') or 'Not assigned'}`")
            st.write(f"Allocated area: `{group.get('allocated_area_m2')}` m²")

            st.write("**Main crops**")
            st.write(", ".join(group.get("main_crops", [])))

            companions = group.get("suggested_companions", [])
            if companions:
                st.write("**Suggested companions**")
                for item in companions:
                    st.write(f"- {item.get('plant')} — " f"{item.get('description', 'Recommended companion')}")

            group_warnings = group.get("warnings", [])
            if group_warnings:
                st.warning("Group warnings:")
                for warning in group_warnings:
                    st.write(f"- {warning}")

            timeline = group.get("timeline", [])
            if timeline:
                st.write("**Timeline**")
                for item in timeline:
                    st.write(
                        f"Batch {item['batch_number']}: "
                        f"Seed {item['seed_start_date']} → "
                        f"Germinate {item['expected_germination_date']} → "
                        f"Transplant {item.get('expected_transplant_date')} → "
                        f"Harvest {item['expected_harvest_date']}"
                    )

    st.divider()
    st.subheader("Layout Preview")

    layout = preview.get("layout", {})
    placements = layout.get("placements", [])

    if placements:
        st.dataframe(placements, width="stretch")
    else:
        st.info("No layout placements generated.")
