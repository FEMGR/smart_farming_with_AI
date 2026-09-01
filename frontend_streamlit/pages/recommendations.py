"""
Frontend page for displaying companion planting recommendations.

Key Point:
Generates and visualizes companion planting suggestions based on user's existing plants.

Responsibilities:
- Trigger the generation of companion planting recommendations from the backend.
- Display "Highest Value Additions" for new plants, allowing users to select and add them.
- Show "Suggested Additions By Plant" for more detailed recommendations.
- Present "Avoid Adding" suggestions for incompatible plants.
- Summarize "Existing Plant Pairs" with recommended and avoid interactions.
- Handle user interactions for adding suggested plants and refreshing recommendations.

Architecture Role:
- User interface component for companion planting analysis.
- Orchestrates calls to the backend API for recommendation generation and plant creation.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (plants.py for recommendations and plant creation), State management (for data refresh).
- Called by: Streamlit application routing.

Data Flow:
User triggers recommendation generation
        ↓
API call to `get_recommendations`
        ↓
Backend processes companion planting rules
        ↓
Frontend receives recommendations data
        ↓
Recommendations are displayed to the user
        ↓
User selects and adds new plants
        ↓
API call to `create_plant`
        ↓
Backend creates new plant entries
        ↓
Frontend refreshes data and re-renders
"""

# frontend_streamlit/pages/recommendations.py


import streamlit as st

from api.plants import create_plant, get_recommendations
from config import PLANT_TYPES
from state import invalidate_recommendations, refresh_data
from utils.formatting import display_plant_name, location_options, plant_name_key
from utils.recommendation_helpers import (
    aggregate_companion_suggestions,
    recommendation_purpose,
)


def render_recommendations() -> None:
    st.subheader("Companion Planting & Recommendations")

    plants = st.session_state.get("plants", [])

    if not plants:
        st.info("Add plants before generating recommendations.")
        return

    if "recs_expanded_accordion" not in st.session_state:
        st.session_state["recs_expanded_accordion"] = "highest"

    if st.button("Generate recommendations", width="content"):
        try:
            with st.spinner("Running companion planting rules..."):
                refresh_data(show_errors=True)
                invalidate_recommendations()
                st.session_state["recommendations"] = get_recommendations()
                st.session_state["recommendations_generated_for"] = len(st.session_state.get("plants", []))
        except RuntimeError as exc:
            st.error(str(exc))

    recommendations = st.session_state.get("recommendations")

    if not recommendations:
        st.caption("Run the recommendation engine above to analyze companion planting rules for your current crops.")
        return

    generated_for = st.session_state.get("recommendations_generated_for")
    if generated_for is not None:
        st.caption(f"Recommendations generated for {generated_for} plant(s).")

    interactions = recommendations.get("existing_plant_interactions") or {}
    suggestions = recommendations.get("new_companion_suggestions") or {}
    good_suggestions = suggestions.get("suggest_good") or {}
    bad_suggestions = suggestions.get("suggest_bad") or {}
    ranked_suggestions = aggregate_companion_suggestions(good_suggestions)

    accordion_items = [
        {
            "id": "highest",
            "title": "Highest Value Additions",
            "due": f"Suggested: {len(ranked_suggestions)} additions",
            "finished_count": len(ranked_suggestions),
            "total_count": len(ranked_suggestions) or 1,
            "progress": 1.0,
            "type": "highest",
        },
        {
            "id": "by_plant",
            "title": "Suggested Additions By Plant",
            "due": f"Plant rules: {len(good_suggestions)} matched",
            "finished_count": len(good_suggestions),
            "total_count": len(good_suggestions) or 1,
            "progress": 1.0,
            "type": "by_plant",
        },
        {
            "id": "avoid",
            "title": "Avoid Adding (Incompatible)",
            "due": f"Avoid: {len(bad_suggestions)} warnings",
            "finished_count": len(bad_suggestions),
            "total_count": len(bad_suggestions) or 1,
            "progress": 1.0,
            "type": "avoid",
        },
        {
            "id": "existing",
            "title": "Existing Plant Pair Interactions",
            "due": "Active Pair Matrix",
            "finished_count": len(interactions.get("recommended", [])),
            "total_count": len(interactions.get("recommended", [])) + len(interactions.get("avoid", [])) or 1,
            "progress": 1.0,
            "type": "existing",
        },
    ]

    for item in accordion_items:
        sec_id = item["id"]
        is_open = st.session_state.get("recs_expanded_accordion") == sec_id
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
            if st.button(arrow_icon, key=f"btn_acc_rec_{sec_id}", help=f"Toggle {item['title']}"):
                if is_open:
                    st.session_state["recs_expanded_accordion"] = None
                else:
                    st.session_state["recs_expanded_accordion"] = sec_id
                st.rerun()

        if is_open:
            st.divider()
            if item["type"] == "highest":
                if not ranked_suggestions:
                    st.caption("No ranked additions were suggested.")
                else:
                    location_labels, location_ids = location_options()
                    control_cols = st.columns([1, 1, 1])
                    selected_type = control_cols[0].selectbox("Type for added plants", PLANT_TYPES, key="suggested_add_type")
                    selected_location = control_cols[1].selectbox("Location for added plants", location_labels, key="suggested_add_location")
                    selected_location_id = location_ids[selected_location]

                    existing_names = {plant_name_key(plant.get("name", "")) for plant in plants}
                    selected_plants = []

                    for sug_item in ranked_suggestions:
                        with st.container(border=True):
                            plant_label = display_plant_name(sug_item["plant"])
                            supports = ", ".join(display_plant_name(name) for name in sug_item["supports"])
                            sources = ", ".join(source.upper() for source in sug_item["sources"])
                            purposes = ", ".join(purpose.replace("_", " ").title() for purpose in sug_item["purposes"])
                            already_added = plant_name_key(sug_item["plant"]) in existing_names

                            cols = st.columns([0.2, 3])

                            checked = cols[0].checkbox(
                                "Add",
                                key=f"add_suggestion_{sug_item['plant']}",
                                label_visibility="collapsed",
                                disabled=already_added,
                            )

                            cols[1].write(f"**{plant_label}**")
                            cols[1].caption(f"Supports {sug_item['support_count']} existing plant(s): {supports}")

                            st.markdown(
                                f'<span class="status-pill">avg score {sug_item["average_score"]:.1f}</span>'
                                f'<span class="status-pill">{purposes}</span>'
                                f'<span class="status-pill">{sources}</span>',
                                unsafe_allow_html=True,
                            )

                            if already_added:
                                st.caption("Already in your plant list.")
                            elif checked:
                                selected_plants.append(sug_item["plant"])

                    if st.button("Add selected plants", width="stretch", disabled=not selected_plants):
                        added = []
                        errors = []

                        for plant_name in selected_plants:
                            try:
                                create_plant(
                                    {
                                        "name": display_plant_name(plant_name),
                                        "plant_type": selected_type,
                                        "location_id": selected_location_id,
                                        "use_sensor": False,
                                    }
                                )
                                added.append(display_plant_name(plant_name))
                            except RuntimeError as exc:
                                errors.append(f"{display_plant_name(plant_name)}: {exc}")

                        refresh_data(show_errors=True)

                        if added:
                            st.success(f"Added {len(added)} plant(s): {', '.join(added)}")

                        if errors:
                            st.error("\n".join(errors))

                        st.rerun()

            elif item["type"] == "by_plant":
                if not good_suggestions:
                    st.caption("No companion additions were suggested.")
                else:
                    for plant_name, items in good_suggestions.items():
                        seen = set()

                        with st.container(border=True):
                            st.write(f"**For {plant_name.replace('_', ' ').title()}**")

                            for g_item in items:
                                companion = g_item.get("plant")

                                if not companion or companion in seen:
                                    continue

                                seen.add(companion)

                                label = companion.replace("_", " ").title()
                                reason = g_item.get("description") or "Companion planting support"
                                confidence = g_item.get("confidence")
                                confidence_text = f" · score {confidence:g}" if isinstance(confidence, (int, float)) else ""

                                st.markdown(
                                    f'<span class="status-pill">{label}</span> '
                                    f'<span class="farm-subtle">{recommendation_purpose(g_item)} · {reason}{confidence_text}</span>',
                                    unsafe_allow_html=True,
                                )

            elif item["type"] == "avoid":
                if not bad_suggestions:
                    st.caption("No incompatible plants recorded for your current selection.")
                else:
                    for plant_name, items in bad_suggestions.items():
                        seen = set()

                        with st.container(border=True):
                            st.write(f"**Near {plant_name.replace('_', ' ').title()}**")

                            for b_item in items:
                                avoid_plant = b_item.get("plant")

                                if not avoid_plant or avoid_plant in seen:
                                    continue

                                seen.add(avoid_plant)

                                st.markdown(
                                    f'<span class="status-pill">{avoid_plant.replace("_", " ").title()}</span>',
                                    unsafe_allow_html=True,
                                )

            elif item["type"] == "existing":
                rec_col, avoid_col = st.columns(2)

                with rec_col:
                    st.markdown("##### Recommended Pairs")
                    ex_items = interactions.get("recommended", [])

                    if not ex_items:
                        st.caption("No recommended pairs found.")

                    for ex_item in ex_items:
                        with st.container(border=True):
                            st.write(f"**{ex_item.get('pair')}**")
                            st.caption(ex_item.get("description") or "Recommended by rules.")
                            st.markdown(
                                f'<span class="status-pill">{recommendation_purpose(ex_item)}</span>',
                                unsafe_allow_html=True,
                            )

                with avoid_col:
                    st.markdown("##### Avoid Pairs")
                    ex_items = interactions.get("avoid", [])

                    if not ex_items:
                        st.caption("No avoid pairs found.")

                    for ex_item in ex_items:
                        with st.container(border=True):
                            st.write(f"**{ex_item.get('pair')}**")
                            st.caption(ex_item.get("description") or "Avoided by rules.")
                            st.markdown(
                                f'<span class="status-pill">{recommendation_purpose(ex_item)}</span>',
                                unsafe_allow_html=True,
                            )

        st.markdown("</div>", unsafe_allow_html=True)
