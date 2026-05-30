"""
Streamlit planning page.

Key Point:
Renders farm section management, polyculture preview generation, saved plan
review, and plan confirmation workflows.
"""

# frontend/pages/planning.py

import math

import streamlit as st

from api import locations as location_api
from api import planning as planning_api

LAYOUT_POSITION_COLUMNS = [
    "plant_id",
    "name",
    "group_id",
    "x",
    "y",
    "soil",
    "saved_position",
    "section_name",
]


def layout_position_rows(placements: list[dict]) -> list[dict]:
    return [{column: placement.get(column) for column in LAYOUT_POSITION_COLUMNS} for placement in placements]


def section_layout_capacity(section: dict) -> dict | None:
    width_m = section.get("width_m")
    length_m = section.get("length_m")

    if width_m is None or length_m is None:
        return None

    columns = max(1, math.ceil(float(width_m)))
    rows = max(1, math.ceil(float(length_m)))

    return {
        "section_id": section.get("id"),
        "section_name": section.get("name"),
        "columns": columns,
        "rows": rows,
        "capacity": columns * rows,
    }


def plant_variation_recommendation(sections: list[dict]) -> tuple[int, list[dict]]:
    capacities = [capacity for section in sections if (capacity := section_layout_capacity(section))]

    if not capacities:
        return 0, []

    return min(capacity["capacity"] for capacity in capacities), capacities


def normalize_crop_name(name: str) -> str:
    return str(name or "").strip()


def crop_key(name: str) -> str:
    return normalize_crop_name(name).lower()


def merge_crop_names(existing_crops: list[str], added_crops: list[str]) -> list[str]:
    merged = []
    seen = set()

    for crop in existing_crops + added_crops:
        crop_name = normalize_crop_name(crop)

        if not crop_name:
            continue

        key = crop_key(crop_name)
        if key in seen:
            continue

        seen.add(key)
        merged.append(crop_name)

    return merged


def crop_text_from_list(crops: list[str]) -> str:
    return ", ".join(crops)


def saved_plan_crop_combination(plan: dict) -> str:
    crops = []

    for group in plan.get("groups", []):
        crops.extend(group.get("main_crops", []))

    combination = crop_text_from_list(merge_crop_names([], crops))

    return combination or "No plants"


def add_selected_plants_to_preview(selected_additions: list[str]) -> None:
    payload = st.session_state.get("polyculture_preview_payload")

    if not payload:
        st.warning("Generate a preview before adding recommended plants.")
        return

    current_crops = payload.get("intended_crops") or [crop.strip() for crop in st.session_state.get("polyculture_crops_text", "").split(",") if crop.strip()]
    updated_crops = merge_crop_names(current_crops, selected_additions)
    updated_payload = {
        **payload,
        "intended_crops": updated_crops,
    }

    preview = planning_api.polyculture_preview(updated_payload)

    if not preview:
        return

    st.session_state["polyculture_pending_crops_text"] = crop_text_from_list(updated_crops)
    st.session_state["polyculture_preview_payload"] = updated_payload
    st.session_state["polyculture_preview_result"] = preview
    st.rerun()


def render_planning_page():
    st.title("Polyculture Production Planning")

    st.caption("Plan compatible crop groups, assign them to farm sections, " "preview timelines, and confirm production batches.")

    tab_saved, tab_sections, tab_preview = st.tabs(["Saved Plans", "Farm Sections", "Polyculture Preview"])

    with tab_saved:
        render_saved_plans_tab()

    with tab_sections:
        render_sections_tab()
    with tab_preview:
        render_polyculture_preview_tab()


def render_saved_plans_tab():
    st.subheader("Saved Polyculture Plans")

    plans = planning_api.get_polyculture_plans() or []

    if not plans:
        st.info("No saved polyculture plans yet.")
        return

    for plan in plans:
        plan_title = f"{plan.get('name') or 'Polyculture Plan'} - {saved_plan_crop_combination(plan)}"

        with st.expander(plan_title, expanded=True):
            st.write(f"Status: `{plan.get('status')}`")
            st.write(f"Location ID: `{plan.get('location_id')}`")
            st.write(f"Harvest interval: `{plan.get('desired_harvest_interval_days')}` days")
            st.write(f"Groups: `{plan.get('group_count')}`")

            with st.expander("Delete saved plan"):
                confirm_delete = st.checkbox(
                    f"Delete {plan.get('name') or 'this saved plan'}",
                    key=f"confirm_delete_polyculture_plan_{plan.get('id')}",
                )

                if st.button(
                    "Delete saved plan",
                    key=f"delete_polyculture_plan_{plan.get('id')}",
                    disabled=not confirm_delete,
                    width="stretch",
                ):
                    result = planning_api.delete_polyculture_plan(plan["id"])

                    if result:
                        st.success("Saved plan deleted.")
                        st.rerun()

            for group in plan.get("groups", []):
                section_name = group.get("section_name") or "Not assigned"
                group_title = f"Group {group.get('group_id')} - {section_name}"

                with st.expander(group_title):
                    st.write(f"Section: `{section_name}`")
                    st.write(f"Allocated area: `{group.get('allocated_area_m2')}` m²")

                    st.write("**Main crops**")
                    st.write(", ".join(group.get("main_crops", [])))

                    layout = group.get("layout") or {}
                    placements = layout.get("placements", [])
                    if placements:
                        st.write("**Saved layout positions**")
                        st.caption(f"Grid: {layout.get('grid_width')} x {layout.get('grid_height')}")
                        st.dataframe(layout_position_rows(placements), width="stretch")

                    batches = group.get("batches", [])
                    if batches:
                        st.write("**Harvest batches**")
                        st.dataframe(batches, width="stretch")


def render_sections_tab():
    st.subheader("Create Farm Section")

    locations = location_api.get_locations() or []
    sections = planning_api.get_sections() or []

    if not locations:
        st.warning("Create a location first before adding farm sections.")
        return

    location_options = {f"{loc['name']} (ID {loc['id']})": loc["id"] for loc in locations}
    locations_by_id = {loc["id"]: loc for loc in locations}

    selected_location = st.selectbox("Location", list(location_options.keys()), key="create_section_location")
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

    with st.form(f"create_section_form_{selected_location_id}"):
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
                key=f"create_section_width_{selected_location_id}",
            )
        with col2:
            length_m = st.number_input(
                "Length (m)",
                min_value=0.1,
                max_value=float(location_length) if location_length is not None else None,
                value=min(3.0, float(location_length)) if location_length is not None else 3.0,
                step=0.1,
                key=f"create_section_length_{selected_location_id}",
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
        section_location = locations_by_id.get(section.get("location_id"), {})
        section_location_name = section_location.get("name") or f"Location {section.get('location_id')}"

        with st.container(border=True):
            st.write(f"**{section['name']} in {section_location_name}**")
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

                with st.form(f"edit_section_{section['id']}_{new_location_id}"):
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
                            key=f"edit_section_width_{section['id']}_{new_location_id}",
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
                            key=f"edit_section_length_{section['id']}_{new_location_id}",
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

    if "polyculture_crops_text" not in st.session_state:
        st.session_state["polyculture_crops_text"] = "cabbage, tomato, carrot, cucumber, lettuce, potato, asparagus"

    pending_crops_text = st.session_state.pop("polyculture_pending_crops_text", None)
    if pending_crops_text is not None:
        st.session_state["polyculture_crops_text"] = pending_crops_text

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
    selected_section_ids = [section_options[label] for label in selected_sections]
    selected_section_data = [section for section in location_sections if section.get("id") in selected_section_ids]
    recommended_variations, section_capacities = plant_variation_recommendation(selected_section_data)

    crops_text = st.text_area(
        "Intended crops",
        key="polyculture_crops_text",
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

    option_col1, option_col2 = st.columns(2)
    with option_col1:
        desired_harvest_batches = st.number_input(
            "Harvest batches wanted",
            min_value=0,
            value=0,
            step=1,
            help="Set 0 to calculate batches automatically from harvest days and interval.",
        )
    with option_col2:
        plant_variations_per_group = st.number_input(
            "Plant variations per group",
            min_value=0,
            value=recommended_variations,
            step=1,
            help="Set 0 for no limit. Use this to split compatible crops into smaller groups.",
        )

    if section_capacities:
        section_capacity_text = ", ".join(
            f"{capacity['section_name']}: {capacity['columns']} columns x {capacity['rows']} rows = {capacity['capacity']}" for capacity in section_capacities
        )
        st.caption(f"Recommended plant variations per group: {recommended_variations}. Section capacity: {section_capacity_text}.")

    preview_clicked = st.button("Generate preview", width="stretch")

    if preview_clicked:
        intended_crops = [crop.strip() for crop in crops_text.split(",") if crop.strip()]

        payload = {
            "location_id": selected_location_id,
            "section_ids": selected_section_ids,
            "intended_crops": intended_crops,
            "start_date": str(start_date),
            "harvest_interval_days": harvest_interval_days,
        }

        if desired_harvest_batches > 0:
            payload["desired_harvest_batches"] = desired_harvest_batches

        if plant_variations_per_group > 0:
            payload["plant_variations_per_group"] = plant_variations_per_group

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

    option_summary = []
    if preview.get("desired_harvest_batches"):
        option_summary.append(f"Harvest batches: {preview.get('desired_harvest_batches')}")
    if preview.get("plant_variations_per_group"):
        option_summary.append(f"Plant variations per group: {preview.get('plant_variations_per_group')}")
    if option_summary:
        st.caption(" | ".join(option_summary))

    st.divider()
    st.subheader("Generated Groups")

    for group in preview.get("groups", []):
        section_name = group.get("section_name") or "Not assigned"
        group_title = f"Group {group.get('group_id')} - {section_name}"

        with st.expander(group_title, expanded=True):
            st.write(f"Section: `{group.get('section_name') or 'Not assigned'}`")
            st.write(f"Allocated area: `{group.get('allocated_area_m2')}` m²")

            st.write("**Main crops**")
            st.write(", ".join(group.get("main_crops", [])))

            companions = group.get("suggested_companions", [])
            if companions:
                st.write("**Suggested companions**")
                for item in companions:
                    st.write(f"- {item.get('plant')} — " f"{item.get('description', 'Recommended companion')}")

            recommended_additions = group.get("recommended_additions", [])
            remaining_slots = group.get("remaining_plant_slots")
            if remaining_slots is not None:
                st.caption(f"Remaining plant slots in this group: {remaining_slots}")

            if recommended_additions:
                st.write("**Plants to add**")
                addition_options = {
                    f"{item.get('plant')} - {item.get('description', 'Recommended companion')}": item.get("plant")
                    for item in recommended_additions
                    if item.get("plant")
                }
                selected_addition_labels = st.multiselect(
                    "Choose plants to add",
                    list(addition_options.keys()),
                    key=f"add_plants_group_{group.get('group_id')}",
                    label_visibility="collapsed",
                )
                selected_additions = [addition_options[label] for label in selected_addition_labels]

                if st.button(
                    "Add selected plants and regenerate preview",
                    key=f"apply_add_plants_group_{group.get('group_id')}",
                    disabled=not selected_additions,
                    width="stretch",
                ):
                    add_selected_plants_to_preview(selected_additions)
            elif remaining_slots == 0:
                st.info("This group has no remaining plant slots for more recommendations.")

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

            group_layout = group.get("layout") or {}
            group_placements = group_layout.get("placements", [])
            if group_placements:
                st.write("**Layout positions**")
                st.caption(f"Grid: {group_layout.get('grid_width')} x {group_layout.get('grid_height')}")
                st.dataframe(layout_position_rows(group_placements), width="stretch")

    st.divider()
    st.subheader("Layout Preview")

    layout = preview.get("layout", {})
    placements = layout.get("placements", [])

    if placements:
        st.dataframe(layout_position_rows(placements), width="stretch")
    else:
        st.info("No layout placements generated.")

    layout_json = preview.get("layout_json", {})
    if layout_json:
        with st.expander("Section layout JSON"):
            st.json(layout_json)
