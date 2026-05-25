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

# frontend/pages/recommendations.py


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
    st.subheader("Companion Planting")

    # Recommendation generation depends on the current plant list.
    plants = st.session_state.get("plants", [])

    if not plants:
        st.info("Add plants before generating recommendations.")
        return

    if st.button("Generate recommendations", use_container_width=False):
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
        st.caption("Run the recommendation engine to analyze your current plants.")
        return

    generated_for = st.session_state.get("recommendations_generated_for")
    if generated_for is not None:
        st.caption(f"Recommendations generated for {generated_for} plant(s).")

    interactions = recommendations.get("existing_plant_interactions") or {}
    suggestions = recommendations.get("new_companion_suggestions") or {}
    good_suggestions = suggestions.get("suggest_good") or {}
    bad_suggestions = suggestions.get("suggest_bad") or {}

    if len(plants) < 2:
        st.info("You have one plant, so there are no existing plant pairs to compare yet. " "Suggested companion additions are shown below.")

    with st.expander("Highest Value Additions", expanded=True):
        ranked_suggestions = aggregate_companion_suggestions(good_suggestions)

        if not ranked_suggestions:
            st.caption("No ranked additions were suggested.")

        selected_location_id = None
        selected_type = "vegetable"

        if ranked_suggestions:
            location_labels, location_ids = location_options()
            control_cols = st.columns([1, 1, 1])
            selected_type = control_cols[0].selectbox("Type for added plants", PLANT_TYPES, key="suggested_add_type")
            selected_location = control_cols[1].selectbox("Location for added plants", location_labels, key="suggested_add_location")
            selected_location_id = location_ids[selected_location]

        existing_names = {plant_name_key(plant.get("name", "")) for plant in plants}
        selected_plants = []

        for item in ranked_suggestions:
            with st.container(border=True):
                plant_label = display_plant_name(item["plant"])
                supports = ", ".join(display_plant_name(name) for name in item["supports"])
                sources = ", ".join(source.upper() for source in item["sources"])
                purposes = ", ".join(purpose.replace("_", " ").title() for purpose in item["purposes"])
                already_added = plant_name_key(item["plant"]) in existing_names

                cols = st.columns([0.2, 3])

                checked = cols[0].checkbox(
                    "Add",
                    key=f"add_suggestion_{item['plant']}",
                    label_visibility="collapsed",
                    disabled=already_added,
                )

                cols[1].write(f"**{plant_label}**")
                cols[1].caption(f"Supports {item['support_count']} existing plant(s): {supports}")

                st.markdown(
                    f'<span class="status-pill">avg score {item["average_score"]:.1f}</span>'
                    f'<span class="status-pill">{purposes}</span>'
                    f'<span class="status-pill">{sources}</span>',
                    unsafe_allow_html=True,
                )

                if already_added:
                    st.caption("Already in your plant list.")
                elif checked:
                    selected_plants.append(item["plant"])

        if ranked_suggestions:
            if st.button("Add selected plants", use_container_width=True, disabled=not selected_plants):
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
                    st.error("\\n".join(errors))

                st.rerun()

    with st.expander("Suggested Additions By Plant", expanded=False):
        if not good_suggestions:
            st.caption("No companion additions were suggested.")

        for plant_name, items in good_suggestions.items():
            seen = set()

            with st.container(border=True):
                st.write(f"**For {plant_name.replace('_', ' ').title()}**")

                for item in items:
                    companion = item.get("plant")

                    if not companion or companion in seen:
                        continue

                    seen.add(companion)

                    label = companion.replace("_", " ").title()
                    reason = item.get("description") or "Companion planting support"
                    confidence = item.get("confidence")
                    confidence_text = f" · score {confidence:g}" if isinstance(confidence, (int, float)) else ""

                    st.markdown(
                        f'<span class="status-pill">{label}</span> '
                        f'<span class="farm-subtle">{recommendation_purpose(item)} · {reason}{confidence_text}</span>',
                        unsafe_allow_html=True,
                    )

    if bad_suggestions:
        with st.expander("Avoid Adding", expanded=False):
            for plant_name, items in bad_suggestions.items():
                seen = set()

                with st.container(border=True):
                    st.write(f"**Near {plant_name.replace('_', ' ').title()}**")

                    for item in items:
                        avoid_plant = item.get("plant")

                        if not avoid_plant or avoid_plant in seen:
                            continue

                        seen.add(avoid_plant)

                        st.markdown(
                            f'<span class="status-pill">{avoid_plant.replace("_", " ").title()}</span>',
                            unsafe_allow_html=True,
                        )

    with st.expander("Existing Plant Pairs", expanded=False):
        rec_col, avoid_col = st.columns(2)

        with rec_col:
            st.markdown("##### Recommended")
            items = interactions.get("recommended", [])

            if not items:
                st.caption("No recommended pairs found.")

            for item in items:
                with st.container(border=True):
                    st.write(f"**{item.get('pair')}**")
                    st.caption(item.get("description") or "Recommended by rules.")
                    st.markdown(
                        f'<span class="status-pill">{recommendation_purpose(item)}</span>',
                        unsafe_allow_html=True,
                    )

        with avoid_col:
            st.markdown("##### Avoid")
            items = interactions.get("avoid", [])

            if not items:
                st.caption("No avoid pairs found.")

            for item in items:
                with st.container(border=True):
                    st.write(f"**{item.get('pair')}**")
                    st.caption(item.get("description") or "Avoided by rules.")
                    st.markdown(
                        f'<span class="status-pill">{recommendation_purpose(item)}</span>',
                        unsafe_allow_html=True,
                    )
