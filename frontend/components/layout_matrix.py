# frontend/components/layout_matrix.py
# Companion layout matrix component.
# - Renders generated and saved plant bed layouts.
# - Handles manual plant moves, displacement, save, and clear actions.
# - Logs manual layout updates for debugging.

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import streamlit as st

from api.plants import get_recommendations, update_plant
from state import invalidate_recommendations, refresh_data
from utils.formatting import display_plant_name


def _get_manual_layout_logger() -> logging.Logger:
    # Separate file keeps manual layout traces easier to inspect.
    logger = logging.getLogger("smart_farming.manual_layout")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        log_dir = Path(__file__).resolve().parents[2] / "logs"
        log_dir.mkdir(exist_ok=True)
        handler = logging.FileHandler(log_dir / "manual_layout.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)

    return logger


manual_layout_logger = _get_manual_layout_logger()


def _placement_log_data(item: dict[str, Any] | None) -> dict[str, Any] | None:
    # Keep layout logs compact and focused on placement fields.
    if item is None:
        return None

    return {
        "plant_id": item.get("plant_id"),
        "name": item.get("name"),
        "group_id": item.get("group_id"),
        "x": item.get("x"),
        "y": item.get("y"),
        "saved_position": item.get("saved_position"),
    }


def _pair_key(name1: str, name2: str) -> str:
    return f"{str(name1).lower().strip()}-{str(name2).lower().strip()}"


def _reverse_pair(pair: str) -> str:
    try:
        a, b = pair.split("-")
        return f"{b}-{a}"
    except ValueError:
        return pair


def _is_pair(name1: str, name2: str, pairs: list[str]) -> bool:
    pair = _pair_key(name1, name2)
    return pair in pairs or _reverse_pair(pair) in pairs


def _distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def is_locked_plant(item: dict) -> bool:
    return item.get("group_id") is not None and item.get("x") is not None and item.get("y") is not None and item.get("saved_position") is True


def _find_best_fallback_position(
    displaced: dict,
    placements: list[dict],
    occupied: dict[tuple[int, int], dict],
    target_position: tuple[int, int],
    grid_width: int,
    grid_height: int,
    recommended_pairs: list[str],
    avoid_pairs: list[str],
) -> tuple[int, int] | None:
    best_position = None
    best_score = None

    displaced_name = displaced.get("name", "")
    displaced_group = displaced.get("group_id")

    for y in range(grid_height):
        for x in range(grid_width):
            pos = (x, y)

            if pos in occupied:
                continue

            score = 0

            for other in placements:
                if other.get("plant_id") == displaced.get("plant_id"):
                    continue

                other_pos = (int(other.get("x", 0)), int(other.get("y", 0)))
                dist = _distance(pos, other_pos)

                if _is_pair(displaced_name, other.get("name", ""), avoid_pairs) and dist < 2:
                    score -= 100

                if _is_pair(displaced_name, other.get("name", ""), recommended_pairs):
                    if dist == 1:
                        score += 20
                    else:
                        score += max(0, 8 - dist)

                if displaced_group is not None and other.get("group_id") == displaced_group:
                    score += max(0, 5 - dist)

            # Prefer staying near the original target row/area
            score -= _distance(pos, target_position)

            if best_score is None or score > best_score:
                best_score = score
                best_position = pos

    return best_position


def render_layout_matrix(
    layout: dict[str, Any],
    groups: list[dict[str, Any]] | None = None,
) -> None:
    placements = layout.get("placements") or []

    if not placements:
        groups = groups or []
        grouped_rows = []

        for group in groups:
            names = [str(plant.get("name", "Plant")).replace("_", " ").title() for plant in group.get("plants", [])]
            if names:
                grouped_rows.append(names)

        if grouped_rows:
            max_cols = max(len(row) for row in grouped_rows)
            matrix = []

            for index, row in enumerate(grouped_rows, start=1):
                padded = row + [""] * (max_cols - len(row))
                matrix.append(
                    {
                        "Group": f"Group {index}",
                        **{f"Bed {col + 1}": value for col, value in enumerate(padded)},
                    }
                )

            st.table(matrix)
            st.caption("Fallback matrix based on companion groups.")
            return

        st.caption("No layout placements were generated.")
        return

    placements = [dict(item) for item in placements]

    grid_width = int(layout.get("grid_width") or 0)
    grid_height = int(layout.get("grid_height") or 0)

    def clear_saved_layout() -> None:
        errors = []
        manual_layout_logger.info(
            "clear_saved_layout.start placements=%s",
            [_placement_log_data(item) for item in placements],
        )

        for item in placements:
            try:
                payload = {
                    "group_id": None,
                    "bed_x": None,
                    "bed_y": None,
                }
                manual_layout_logger.info(
                    "clear_saved_layout.update_request plant_id=%s payload=%s before=%s",
                    item.get("plant_id"),
                    payload,
                    _placement_log_data(item),
                )
                response = update_plant(
                    int(item["plant_id"]),
                    payload,
                )
                manual_layout_logger.info(
                    "clear_saved_layout.update_response plant_id=%s response=%s",
                    item.get("plant_id"),
                    response,
                )
            except RuntimeError as exc:
                manual_layout_logger.exception(
                    "clear_saved_layout.update_error plant_id=%s",
                    item.get("plant_id"),
                )
                errors.append(f"{display_plant_name(str(item.get('name') or 'Plant'))}: {exc}")

        refresh_data(show_errors=True)

        if errors:
            manual_layout_logger.info("clear_saved_layout.finished errors=%s", errors)
            st.error("\n".join(errors))
        else:
            invalidate_recommendations()
            st.session_state["recommendations"] = get_recommendations()
            manual_layout_logger.info("clear_saved_layout.finished success=true")
            st.success("Cleared saved group and bed assignments.")
            st.rerun()

    available_groups = sorted({int(item.get("group_id") or 1) for item in placements})
    movable_placements = [item for item in placements if not is_locked_plant(item)]

    plant_labels = {f"{display_plant_name(str(item.get('name') or 'Plant'))} (ID {item.get('plant_id')})": item for item in movable_placements}

    with st.expander("Manual Layout Adjustment", expanded=False):
        if not movable_placements:
            st.caption(
                "All displayed plants already have saved bed positions. " "Use the button below to clear saved positions if you want to redesign the layout."
            )
        else:
            st.caption("Only newly added or unassigned plants can be moved. " "Plants with saved group and bed positions are treated as already planted.")

            selected_plant_label = st.selectbox(
                "Plant to move",
                list(plant_labels.keys()),
                key="layout_move_plant",
            )

            target_group = st.selectbox(
                "Target group row",
                available_groups,
                key="layout_target_group",
            )

            selected_item = plant_labels[selected_plant_label]

            max_bed = max(1, grid_width)
            max_row = max(1, grid_height)

            position_cols = st.columns(2)

            target_bed = position_cols[0].number_input(
                "Target bed",
                min_value=1,
                max_value=max_bed,
                value=int(selected_item.get("x", 0)) + 1,
                step=1,
            )

            target_row = position_cols[1].number_input(
                "Target row",
                min_value=1,
                max_value=max_row,
                value=int(selected_item.get("y", 0)) + 1,
                step=1,
            )

            occupied = {(int(item.get("x", 0)), int(item.get("y", 0))): item for item in placements if item.get("plant_id") != selected_item.get("plant_id")}

            target_position = (int(target_bed) - 1, int(target_row) - 1)
            occupant = occupied.get(target_position)

            if occupant:
                st.warning(
                    "Target position is currently occupied by "
                    f"{display_plant_name(str(occupant.get('name') or 'Plant'))}. "
                    "Saving will move that plant to the best available fallback position."
                )

            action_cols = st.columns(2)

            if action_cols[0].button(
                "Save plant position",
                key="save_manual_layout_position",
                use_container_width=True,
            ):
                try:
                    recommended_pairs = [
                        item.get("pair")
                        for item in (st.session_state.get("recommendations", {}) or {}).get("existing_plant_interactions", {}).get("recommended", [])
                        if item.get("pair")
                    ]

                    avoid_pairs = [
                        item.get("pair")
                        for item in (st.session_state.get("recommendations", {}) or {}).get("existing_plant_interactions", {}).get("avoid", [])
                        if item.get("pair")
                    ]

                    # ==========================================
                    # Convert UI coordinates → DB coordinates
                    # UI is 1-based
                    # DB is 0-based
                    # ==========================================
                    target_x = int(target_bed) - 1
                    target_y = int(target_row) - 1

                    target_position = (target_x, target_y)

                    updates = []
                    manual_layout_logger.info(
                        "manual_layout.save.start selected_label=%s selected=%s "
                        "target_group=%s target_position=%s occupant=%s "
                        "available_groups=%s placements=%s",
                        selected_plant_label,
                        _placement_log_data(selected_item),
                        target_group,
                        target_position,
                        _placement_log_data(occupant),
                        available_groups,
                        [_placement_log_data(item) for item in placements],
                    )

                    # ==========================================
                    # OCCUPIED TARGET
                    # ==========================================
                    if occupant:

                        # Locked plants cannot be displaced
                        if is_locked_plant(occupant):
                            st.error(
                                f"{display_plant_name(str(occupant.get('name') or 'Plant'))} "
                                "is already planted and locked in place. "
                                "Choose another position."
                            )
                            st.stop()

                        # Find fallback for movable plant
                        fallback_position = _find_best_fallback_position(
                            displaced=occupant,
                            placements=placements,
                            occupied=occupied,
                            target_position=target_position,
                            grid_width=max_bed,
                            grid_height=max_row,
                            recommended_pairs=recommended_pairs,
                            avoid_pairs=avoid_pairs,
                        )

                        if fallback_position is None:
                            st.error("No valid fallback position exists for the displaced plant.")
                            st.stop()

                        fallback_x, fallback_y = fallback_position
                        manual_layout_logger.info(
                            "manual_layout.save.fallback occupant=%s fallback_position=%s",
                            _placement_log_data(occupant),
                            fallback_position,
                        )

                        updates.append(
                            (
                                int(occupant["plant_id"]),
                                {
                                    "group_id": occupant.get("group_id"),
                                    "bed_x": fallback_x,
                                    "bed_y": fallback_y,
                                },
                            )
                        )

                    # ==========================================
                    # SAVE SELECTED PLANT
                    # ==========================================
                    updates.append(
                        (
                            int(selected_item["plant_id"]),
                            {
                                "group_id": target_group,
                                "bed_x": target_x,
                                "bed_y": target_y,
                            },
                        )
                    )

                    # ==========================================
                    # EXECUTE DB UPDATES
                    # ==========================================
                    for plant_id, payload in updates:
                        before = next(
                            (item for item in placements if item.get("plant_id") is not None and int(item.get("plant_id")) == int(plant_id)),
                            None,
                        )
                        manual_layout_logger.info(
                            "manual_layout.save.update_request plant_id=%s payload=%s before=%s",
                            plant_id,
                            payload,
                            _placement_log_data(before),
                        )
                        response = update_plant(plant_id, payload)
                        manual_layout_logger.info(
                            "manual_layout.save.update_response plant_id=%s response=%s",
                            plant_id,
                            response,
                        )

                    refresh_data(show_errors=True)

                    invalidate_recommendations()

                    st.session_state["recommendations"] = get_recommendations()
                    manual_layout_logger.info(
                        "manual_layout.save.finished success=true updates=%s",
                        updates,
                    )

                    # ==========================================
                    # SUCCESS MESSAGE
                    # ==========================================
                    if occupant:
                        st.success(
                            f"Moved {selected_plant_label}. "
                            f"{display_plant_name(str(occupant.get('name') or 'Plant'))} "
                            f"was automatically moved to "
                            f"Row {fallback_y + 1}, Bed {fallback_x + 1}."
                        )
                    else:
                        st.success(f"Saved {selected_plant_label} to " f"Group {target_group}, " f"Row {target_y + 1}, " f"Bed {target_x + 1}.")

                    st.rerun()

                except RuntimeError as exc:
                    manual_layout_logger.exception(
                        "manual_layout.save.error selected=%s target_group=%s " "target_position=%s occupant=%s",
                        _placement_log_data(selected_item),
                        target_group,
                        (int(target_bed) - 1, int(target_row) - 1),
                        _placement_log_data(occupant),
                    )
                    st.error(str(exc))

            if action_cols[1].button(
                "Clear saved layout",
                key="clear_saved_layout_manual_adjustment",
                use_container_width=True,
            ):
                clear_saved_layout()

    placement_map = {(int(item.get("x", 0)), int(item.get("y", 0))): item for item in placements}

    max_x = max(grid_width - 1, max(int(item.get("x", 0)) for item in placements))
    max_y = max(grid_height - 1, max(int(item.get("y", 0)) for item in placements))

    table_rows = []

    for y in range(0, max_y + 1):
        row = {"Row": y + 1}

        for x in range(0, max_x + 1):
            plant = placement_map.get((x, y))
            row[f"Bed {x + 1}"] = str(plant.get("name", "")).replace("_", " ").title() if plant else ""

        table_rows.append(row)

    st.table(table_rows)
    st.caption("Rows and beds use backend layout coordinates. " "Location dimensions are treated as meter-based grid capacity.")

    st.markdown("##### Plant Details")

    detail_rows = []

    for item in sorted(
        placements,
        key=lambda plant: (
            plant.get("group_id") or 0,
            plant.get("y") or 0,
            plant.get("x") or 0,
        ),
    ):
        detail_rows.append(
            {
                "Plant": str(item.get("name") or "Plant").replace("_", " ").title(),
                "Group": item.get("group_id"),
                "Position": f"Row {int(item.get('y', 0)) + 1}, Bed {int(item.get('x', 0)) + 1}",
                "Status": "Saved" if item.get("saved_position") else "Generated",
                "Zone": str(item.get("zone") or "unknown").replace("_", " "),
                "Sunlight": str(item.get("sunlight") or "unknown").replace("_", " "),
                "Water": str(item.get("water") or "unknown").replace("_", " "),
            }
        )

    st.table(detail_rows)

    st.markdown("##### Group Rows")

    grouped_by_group: dict[Any, list[dict[str, Any]]] = {}

    for item in placements:
        grouped_by_group.setdefault(item.get("group_id"), []).append(item)

    group_matrix = []
    max_group_size = max(len(items) for items in grouped_by_group.values())

    for group_id, items in sorted(grouped_by_group.items(), key=lambda pair: pair[0] or 0):
        items = sorted(items, key=lambda plant: (plant.get("y") or 0, plant.get("x") or 0))

        row = {"Group": f"Group {group_id}"}

        for index in range(max_group_size):
            value = ""

            if index < len(items):
                value = str(items[index].get("name") or "Plant").replace("_", " ").title()

            row[f"Plant {index + 1}"] = value

        group_matrix.append(row)

    st.table(group_matrix)

    if st.button("Save generated groups", use_container_width=True):
        errors = []

        # Sort by group_id first so saved data follows the displayed group order
        sorted_placements = sorted(
            placements,
            key=lambda item: (
                int(item.get("group_id") or 999),
                int(item.get("y") or 0),
                int(item.get("x") or 0),
            ),
        )

        occupied_positions = {}

        for item in sorted_placements:
            if is_locked_plant(item):
                continue
            plant_id = int(item["plant_id"])
            group_id = int(item.get("group_id") or 1)
            position = (int(item.get("x") or 0), int(item.get("y") or 0))

            if position in occupied_positions:
                old_item = occupied_positions[position]
                errors.append(
                    f"{display_plant_name(str(item.get('name') or 'Plant'))} conflicts with "
                    f"{display_plant_name(str(old_item.get('name') or 'Plant'))} at "
                    f"Row {position[1] + 1}, Bed {position[0] + 1}."
                )
                continue

            occupied_positions[position] = item

            try:
                update_plant(
                    plant_id,
                    {
                        "group_id": group_id,
                        "bed_x": position[0],
                        "bed_y": position[1],
                    },
                )
            except RuntimeError as exc:
                errors.append(f"{display_plant_name(str(item.get('name') or 'Plant'))}: {exc}")

        refresh_data(show_errors=True)

        if errors:
            st.error("\n".join(errors))
        else:
            invalidate_recommendations()
            st.session_state["recommendations"] = get_recommendations()
            st.success("Saved the displayed group and bed assignments to the database.")
            st.rerun()

    st.divider()

    if st.button(
        "Clear saved layout",
        key="clear_saved_layout_group_table",
        use_container_width=True,
    ):
        clear_saved_layout()

    warnings = layout.get("warnings") or []

    if warnings:
        st.warning("\n".join(str(item) for item in warnings))

    shade_relationships = layout.get("shade_relationships") or []

    if shade_relationships:
        st.markdown("##### Shade Support")

        for relation in shade_relationships:
            st.caption(relation.get("reason") or relation)
