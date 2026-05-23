# frontend/pages/signed_out.py
# Signed-out landing view shown before authentication.

import streamlit as st


def render_signed_out() -> None:
    st.title("Smart Urban Farming")
    st.write("Sign in from the sidebar to manage plants, watering, locations, " "and companion planting recommendations.")

    cols = st.columns(3)
    cols[0].metric("Backend", "FastAPI")
    cols[1].metric("Reasoning", "Prolog")
    cols[2].metric("Species Data", "Perenual")
