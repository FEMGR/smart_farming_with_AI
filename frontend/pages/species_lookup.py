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
    st.subheader("Species Lookup & Discovery")

    if "species_expanded_accordion" not in st.session_state:
        st.session_state["species_expanded_accordion"] = "search"

    query = st.session_state.get("species_search_query", "")

    accordion_items = [
        {
            "id": "search",
            "title": "Species Search Query",
            "due": f"Query: '{query}'" if query else "Ready to Search",
            "finished_count": 1 if query else 0,
            "total_count": 1,
            "progress": 1.0 if query else 0.0,
            "type": "search",
        },
        {
            "id": "results",
            "title": "Matching Species Results",
            "due": "Live Results",
            "finished_count": 1,
            "total_count": 1,
            "progress": 1.0,
            "type": "results",
        },
    ]

    for item in accordion_items:
        sec_id = item["id"]
        is_open = st.session_state.get("species_expanded_accordion") == sec_id
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
            if st.button(arrow_icon, key=f"btn_acc_spec_{sec_id}", help=f"Toggle {item['title']}"):
                if is_open:
                    st.session_state["species_expanded_accordion"] = None
                else:
                    st.session_state["species_expanded_accordion"] = sec_id
                st.rerun()

        if is_open:
            st.divider()
            if item["type"] == "search":
                new_query = st.text_input("Search species", value=query, placeholder="tomato, basil, lettuce")
                if new_query != query:
                    st.session_state["species_search_query"] = new_query
                    st.session_state["species_expanded_accordion"] = "results"
                    st.rerun()
            elif item["type"] == "results":
                if not query:
                    st.caption("Enter a search term in the query section above.")
                else:
                    try:
                        suggestions = suggest_species(query)
                    except RuntimeError as exc:
                        st.error(str(exc))
                        suggestions = []

                    if not suggestions:
                        st.info("No species suggestions found.")
                    else:
                        for species in suggestions:
                            with st.container(border=True):
                                cols = st.columns([1, 3, 1])
                                thumbnail = species.get("thumbnail_url")

                                if thumbnail:
                                    cols[0].image(thumbnail, width="stretch")
                                else:
                                    cols[0].caption("No image")

                                cols[1].write(f"**{species.get('common_name') or 'Unknown common name'}**")
                                cols[1].caption(species.get("scientific_name") or "Unknown scientific name")

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

                                cols[2].write(f"ID `{species.get('id')}`")

        st.markdown("</div>", unsafe_allow_html=True)
