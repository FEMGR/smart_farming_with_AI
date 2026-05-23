# frontend/pages/species_lookup.py
# Species lookup page.
# - Searches external/cached species data.
# - Displays candidate species metadata and thumbnails.

import streamlit as st

from api.species import suggest_species


def render_species_lookup() -> None:
    st.subheader("Species Lookup")

    query = st.text_input("Search species", placeholder="tomato, basil, lettuce")

    if not query:
        st.caption("Search by common or scientific name.")
        return

    try:
        suggestions = suggest_species(query)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not suggestions:
        st.info("No species suggestions found.")
        return

    for species in suggestions:
        with st.container(border=True):
            cols = st.columns([1, 3, 1])
            thumbnail = species.get("thumbnail_url")

            if thumbnail:
                cols[0].image(thumbnail, use_container_width=True)
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
