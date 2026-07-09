# Main Streamlit entry point.
# - Applies page config and custom styles.
# - Initializes session state and sidebar auth controls.
# - Routes signed-in users through the dashboard tabs.

# frontend/streamlit_app.py

import streamlit as st

from components.sidebar import render_sidebar
from pages.irrigation import render_irrigation
from pages.locations import render_locations
from pages.notifications import render_notifications
from pages.overview import render_overview
from pages.pest_query import render_pest_query
from pages.plants import render_plants
from pages.recommendations import render_recommendations
from pages.signed_out import render_signed_out
from pages.species_lookup import render_species_lookup
from pages.layout import render_layout  # Import the new layout page
from state import init_state
from styles import apply_page_config, apply_styles
from pages.planning import render_planning_page


def main() -> None:
    # App shell setup.
    apply_page_config()
    apply_styles()
    init_state()
    render_sidebar()

    # Signed-out users only see the welcome/auth prompt.
    if not st.session_state.get("token"):
        render_signed_out()
        return

    # Main authenticated dashboard navigation.
    st.title("Smart Urban Farming")
    st.caption("Manage care tasks, plant data, growing locations, and companion planting decisions.")

    tabs = st.tabs(
        [
            "Overview",
            "Plants",
            "Locations",
            "Irrigation",
            "Recommendations",
            "Planning",
            "Layout",
            "Notifications",
            "Species Lookup",
            "Pest Query",
        ]
    )

    with tabs[0]:
        render_overview()

    with tabs[1]:
        render_plants()

    with tabs[2]:
        render_locations()

    with tabs[3]:
        render_irrigation()

    with tabs[4]:
        render_recommendations()

    with tabs[5]:
        render_planning_page()

    with tabs[6]:
        render_layout()

    with tabs[7]:
        render_notifications()

    with tabs[8]:
        render_species_lookup()

    with tabs[9]:
        render_pest_query()


if __name__ == "__main__":
    main()
