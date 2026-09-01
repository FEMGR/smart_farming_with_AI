"""
Frontend page for managing plant layout and positions.

Key Point:
Provides tools for users to visualize, manually adjust, and save plant positions
within a grid, integrating with generated layout recommendations.

Responsibilities:
- Display the current saved planting layout, optionally using a generated layout matrix.
- List unassigned plants and allow users to manually assign them positions and groups.
- Provide options to adjust positions or clear saved positions for "locked" (assigned) plants.
- Offer actions to clear all saved layouts or save a generated layout as fixed positions.
- Handle user interactions for updating plant positions and groups.
- Trigger data refresh and invalidate recommendations upon layout changes.

Architecture Role:
- User interface component for spatial plant arrangement and management.
- Interacts with the backend API to persist plant position data.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (plants.py for backend calls),
  State management (for data refresh), `components.layout_matrix` (for visualization),
  `utils.recommendation_helpers` (for group suggestions).
- Called by: Streamlit application routing.

Data Flow:
User navigates to layout page
        ↓
Frontend fetches plant data and recommendations from session state
        ↓
Plants are categorized (locked, unassigned) and displayed
        ↓
User interacts with forms/buttons to assign/adjust/save positions
        ↓
API call to `update_plant`
        ↓
Backend updates plant position/group data
        ↓
Frontend receives response, refreshes local data, and re-renders
"""

# frontend_streamlit/pages/layout.py

import streamlit as st

from state import refresh_data, invalidate_recommendations
from api.plants import update_plant
from utils.formatting import display_plant_name, plant_display_name
from utils.recommendation_helpers import recommended_group_options_for_plant


def _render_saved_layout_table(plants: list[dict]) -> None:
    saved_plants = [plant for plant in plants if plant.get("bed_x") is not None and plant.get("bed_y") is not None]

    if not saved_plants:
        st.caption("No plants have saved positions yet.")
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


def render_layout() -> None:
    """
    Renders the plant layout management page with accordion list structure.
    """
    st.subheader("Plant Layout Management")

    plants = st.session_state.get("plants", [])
    recommendations = st.session_state.get("recommendations")

    if not plants:
        st.info("Add plants to see and manage your layout.")
        return

    if "layout_expanded_accordion" not in st.session_state:
        st.session_state["layout_expanded_accordion"] = "grid"

    locked_plants = [p for p in plants if p.get("bed_x") is not None and p.get("bed_y") is not None]
    unassigned_plants = [p for p in plants if p.get("bed_x") is None or p.get("bed_y") is None]

    total_plants = len(plants) or 1
    placed_count = len(locked_plants)
    placed_ratio = min(1.0, max(0.0, placed_count / total_plants))

    accordion_items = [
        {
            "id": "grid",
            "title": "Saved Bed Layout Grid Matrix",
            "due": f"Placed: {placed_count} plants",
            "finished_count": placed_count,
            "total_count": total_plants,
            "progress": placed_ratio,
            "type": "grid",
        },
        {
            "id": "unassigned",
            "title": "Unassigned Plant Positions",
            "due": f"Unassigned: {len(unassigned_plants)} plants",
            "finished_count": total_plants - len(unassigned_plants),
            "total_count": total_plants,
            "progress": 1.0 - (len(unassigned_plants) / total_plants),
            "type": "unassigned",
        },
        {
            "id": "locked",
            "title": "Manual Adjustments (Locked Plants)",
            "due": f"Locked: {len(locked_plants)} positions",
            "finished_count": len(locked_plants),
            "total_count": total_plants,
            "progress": placed_ratio,
            "type": "locked",
        },
        {
            "id": "actions",
            "title": "Global Layout Actions",
            "due": "Layout Controls",
            "finished_count": 1,
            "total_count": 1,
            "progress": 1.0,
            "type": "actions",
        },
    ]

    for item in accordion_items:
        sec_id = item["id"]
        is_open = st.session_state.get("layout_expanded_accordion") == sec_id
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
            if st.button(arrow_icon, key=f"btn_acc_lay_{sec_id}", help=f"Toggle {item['title']}"):
                if is_open:
                    st.session_state["layout_expanded_accordion"] = None
                else:
                    st.session_state["layout_expanded_accordion"] = sec_id
                st.rerun()

        if is_open:
            st.divider()
            if item["type"] == "grid":
                _render_saved_layout_table(plants)
            elif item["type"] == "unassigned":
                if unassigned_plants:
                    for plant in unassigned_plants:
                        with st.container(border=True):
                            st.write(f"**{plant_display_name(plant)}**")
                            st.caption(f"ID: {plant.get('id')}")

                            with st.expander("Assign Position"):
                                cols = st.columns(2)
                                new_x_input = cols[0].number_input(
                                    "Bed X (1-indexed)", min_value=1, value=(plant.get("bed_x") or 0) + 1, key=f"unassigned_x_{plant['id']}"
                                )
                                new_y_input = cols[1].number_input(
                                    "Row Y (1-indexed)", min_value=1, value=(plant.get("bed_y") or 0) + 1, key=f"unassigned_y_{plant['id']}"
                                )

                                group_options = recommended_group_options_for_plant(plant, recommendations)
                                group_labels = [opt["label"] for opt in group_options]
                                group_ids = {opt["label"]: opt["group_id"] for opt in group_options}

                                selected_group_label = st.selectbox(
                                    "Assign to Group (optional)",
                                    ["None"] + group_labels,
                                    key=f"unassigned_group_{plant['id']}",
                                    help="Assigning to a group helps the layout engine place compatible plants together.",
                                )
                                new_group_id = group_ids.get(selected_group_label) if selected_group_label != "None" else None

                                if st.button("Save Position", key=f"save_unassigned_{plant['id']}"):
                                    try:
                                        update_plant(
                                            plant["id"],
                                            {
                                                "bed_x": new_x_input - 1,
                                                "bed_y": new_y_input - 1,
                                                "group_id": new_group_id,
                                            },
                                        )
                                        invalidate_recommendations()
                                        refresh_data(show_errors=True)
                                        st.rerun()
                                    except RuntimeError as exc:
                                        st.error(str(exc))
                else:
                    st.caption("All plants are assigned a position or are part of a generated layout.")

            elif item["type"] == "locked":
                if locked_plants:
                    for plant in locked_plants:
                        with st.container(border=True):
                            bed = int(plant["bed_x"]) + 1
                            row = int(plant["bed_y"]) + 1
                            st.write(f"**{plant_display_name(plant)}** at Bed {bed}, Row {row}")
                            st.caption(f"ID: {plant.get('id')}")

                            with st.expander("Adjust Position / Clear"):
                                cols = st.columns(2)
                                new_x_input = cols[0].number_input(
                                    "Bed X (1-indexed)", min_value=1, value=(plant.get("bed_x") or 0) + 1, key=f"locked_x_{plant['id']}"
                                )
                                new_y_input = cols[1].number_input(
                                    "Row Y (1-indexed)", min_value=1, value=(plant.get("bed_y") or 0) + 1, key=f"locked_y_{plant['id']}"
                                )

                                group_options = recommended_group_options_for_plant(plant, recommendations)
                                group_labels = [opt["label"] for opt in group_options]
                                group_ids = {opt["label"]: opt["group_id"] for opt in group_options}

                                current_group_label = "None"
                                if plant.get("group_id"):
                                    for opt in group_options:
                                        if opt["group_id"] == plant["group_id"]:
                                            current_group_label = opt["label"]
                                            break
                                    if current_group_label == "None":
                                        current_group_label = f"Group {plant['group_id']} (current)"
                                        group_labels.insert(0, current_group_label)
                                        group_ids[current_group_label] = plant["group_id"]

                                selected_group_label = st.selectbox(
                                    "Assign to Group (optional)",
                                    ["None"] + group_labels,
                                    index=group_labels.index(current_group_label) + 1 if current_group_label != "None" else 0,
                                    key=f"locked_group_{plant['id']}",
                                    help="Assigning to a group helps the layout engine place compatible plants together.",
                                )
                                new_group_id = group_ids.get(selected_group_label) if selected_group_label != "None" else None

                                if st.button("Update Position", key=f"update_locked_{plant['id']}"):
                                    try:
                                        update_plant(
                                            plant["id"],
                                            {
                                                "bed_x": new_x_input - 1,
                                                "bed_y": new_y_input - 1,
                                                "group_id": new_group_id,
                                            },
                                        )
                                        invalidate_recommendations()
                                        refresh_data(show_errors=True)
                                        st.rerun()
                                    except RuntimeError as exc:
                                        st.error(str(exc))

                                if st.button("Clear Saved Position", key=f"clear_locked_{plant['id']}"):
                                    try:
                                        update_plant(
                                            plant["id"],
                                            {
                                                "bed_x": None,
                                                "bed_y": None,
                                                "group_id": None,
                                            },
                                        )
                                        invalidate_recommendations()
                                        refresh_data(show_errors=True)
                                        st.rerun()
                                    except RuntimeError as exc:
                                        st.error(str(exc))
                else:
                    st.caption("No plants with locked positions to adjust.")

            elif item["type"] == "actions":
                col1, col2 = st.columns(2)
                if col1.button("Clear All Saved Layouts", help="This will remove all bed_x and bed_y assignments from all plants."):
                    try:
                        for plant in plants:
                            if plant.get("bed_x") is not None or plant.get("bed_y") is not None or plant.get("group_id") is not None:
                                update_plant(plant["id"], {"bed_x": None, "bed_y": None, "group_id": None})
                        invalidate_recommendations()
                        refresh_data(show_errors=True)
                        st.success("All saved layout positions cleared.")
                        st.rerun()
                    except RuntimeError as exc:
                        st.error(str(exc))

                if col2.button("Save Generated Layout", help="This will save the last generated layout positions as fixed positions for your plants."):
                    if recommendations and recommendations.get("layout"):
                        try:
                            layout_placements = recommendations["layout"].get("placements", [])
                            for placement in layout_placements:
                                plant_id = placement["plant_id"]
                                x = placement["x"]
                                y = placement["y"]
                                group_id = placement["group_id"]
                                update_plant(plant_id, {"bed_x": x, "bed_y": y, "group_id": group_id})
                            invalidate_recommendations()
                            refresh_data(show_errors=True)
                            st.success("Generated layout saved as fixed positions.")
                            st.rerun()
                        except RuntimeError as exc:
                            st.error(str(exc))
                    else:
                        st.warning("No generated layout available to save.")

        st.markdown("</div>", unsafe_allow_html=True)
