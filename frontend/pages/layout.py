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

# frontend/pages/layout.py

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
    Renders the plant layout management page.

    This page allows users to:
    - View their current saved plant layout.
    - Assign positions and groups to unassigned plants.
    - Manually adjust positions or clear saved positions for existing plants.
    - Clear all saved layout positions.
    - Save a generated layout from the recommendations as fixed positions.
    """
    st.subheader("Plant Layout")

    plants = st.session_state.get("plants", [])
    recommendations = st.session_state.get("recommendations")

    if not plants:
        st.info("Add plants to see and manage your layout.")
        return

    # Filter plants into locked, unassigned, and assigned
    locked_plants = [p for p in plants if p.get("bed_x") is not None and p.get("bed_y") is not None]
    unassigned_plants = [p for p in plants if p.get("bed_x") is None or p.get("bed_y") is None]

    st.markdown("#### Current Saved Planting Layout")
    _render_saved_layout_table(plants)

    st.markdown("#### Unassigned Plants")
    if unassigned_plants:
        for plant in unassigned_plants:
            with st.container(border=True):
                st.write(f"**{plant_display_name(plant)}**")
                st.caption(f"ID: {plant.get('id')}")

                with st.expander("Assign Position"):
                    cols = st.columns(2)
                    # Display 1-indexed, save 0-indexed
                    new_x_input = cols[0].number_input("Bed X (1-indexed)", min_value=1, value=(plant.get("bed_x") or 0) + 1, key=f"unassigned_x_{plant['id']}")
                    new_y_input = cols[1].number_input("Row Y (1-indexed)", min_value=1, value=(plant.get("bed_y") or 0) + 1, key=f"unassigned_y_{plant['id']}")

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
                                    "bed_x": new_x_input - 1,  # Convert back to 0-indexed
                                    "bed_y": new_y_input - 1,  # Convert back to 0-indexed
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

    st.markdown("#### Manual Adjustments (Locked Plants)")
    if locked_plants:
        for plant in locked_plants:
            with st.container(border=True):
                bed = int(plant["bed_x"]) + 1
                row = int(plant["bed_y"]) + 1
                st.write(f"**{plant_display_name(plant)}** at Bed {bed}, Row {row}")
                st.caption(f"ID: {plant.get('id')}")

                with st.expander("Adjust Position / Clear"):
                    cols = st.columns(2)
                    # Display 1-indexed, save 0-indexed
                    new_x_input = cols[0].number_input("Bed X (1-indexed)", min_value=1, value=(plant.get("bed_x") or 0) + 1, key=f"locked_x_{plant['id']}")
                    new_y_input = cols[1].number_input("Row Y (1-indexed)", min_value=1, value=(plant.get("bed_y") or 0) + 1, key=f"locked_y_{plant['id']}")

                    group_options = recommended_group_options_for_plant(plant, recommendations)
                    group_labels = [opt["label"] for opt in group_options]
                    group_ids = {opt["label"]: opt["group_id"] for opt in group_options}

                    current_group_label = "None"
                    if plant.get("group_id"):
                        for opt in group_options:
                            if opt["group_id"] == plant["group_id"]:
                                current_group_label = opt["label"]
                                break
                        if current_group_label == "None":  # If current group is not in recommended options
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
                                    "bed_x": new_x_input - 1,  # Convert back to 0-indexed
                                    "bed_y": new_y_input - 1,  # Convert back to 0-indexed
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

    st.markdown("#### Layout Actions")
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
