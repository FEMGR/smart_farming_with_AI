"""
Frontend page for looking up plant species.

Key Point:
Allows users to search for plant species by common or scientific name and view suggestions
from external data sources.

Responsibilities:
- Provide a search input field for species queries.
- Display a list of suggested species based on the user's query.
- Show relevant details for each suggestion, such as common name, scientific name,
  source, score, plant type, and an optional thumbnail image.
- Handle cases where no suggestions are found or an error occurs during the search.

Architecture Role:
- User interface component for species discovery.
- Interacts with the backend API to fetch species suggestions.

Layer Interaction:
- Communicates with: Streamlit (UI rendering), API (species.py for backend calls).
- Called by: Streamlit application routing.

Data Flow:
User enters a search query
        ↓
API call to `suggest_species` with the query
        ↓
Backend queries external species data sources
        ↓
Frontend receives a list of species suggestions
        ↓
Suggestions are rendered on the page with their details
"""

# frontend/pages/species_lookup.py


import streamlit as st

from api.species import suggest_species


def render_species_lookup() -> None:
    """
    Renders the species lookup page, allowing users to search for plant species
    and view suggestions.
    """
    st.subheader("Species Lookup")

    query = st.text_input("Search species", placeholder="tomato, basil, lettuce")

    if not query:
        st.caption("Search by common or scientific name.")
        return

    try:
        # Fetch species suggestions from the backend API
        suggestions = suggest_species(query)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not suggestions:
        st.info("No species suggestions found.")
        return

    # Display each species suggestion in a container
    for species in suggestions:
        with st.container(border=True):
            cols = st.columns([1, 3, 1])
            thumbnail = species.get("thumbnail_url")

            # Display thumbnail image if available
            if thumbnail:
                cols[0].image(thumbnail, use_container_width=True)
            else:
                cols[0].caption("No image")

            # Display common and scientific names
            cols[1].write(f"**{species.get('common_name') or 'Unknown common name'}**")
            cols[1].caption(species.get("scientific_name") or "Unknown scientific name")

            # Display status pills for source, score, and plant type
            cols[1].markdown(
                " ".join(
                    [
                        f'<span class="status-pill">{species.get("source", "source")}</span>',
                        f'<span class="status-pill">score {species.get("score", 0):.2f}</span>',
                        f'<span class="status-pill">{species.get("plant_type") or "type unknown"}</span>',
                    ]
                ),
                unsafe_allow_html=True,
            )

            # Display species ID
            cols[2].write(f"ID `{species.get('id')}`")
