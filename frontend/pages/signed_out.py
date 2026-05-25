"""
Frontend page displayed when the user is signed out.

Key Point:
Serves as a landing page for signed-out users, providing a brief introduction
to the application and highlighting its core technologies.

Responsibilities:
- Display a welcome message and instructions to sign in.
- Showcase key backend technologies used in the application.

Architecture Role:
- Entry point for unauthenticated users.
- Provides a static informational view of the application.

Layer Interaction:
- Communicates with: Streamlit (UI rendering).
- Called by: Streamlit application routing when no user is authenticated.

Data Flow:
User is not authenticated
        ↓
`render_signed_out()` is called
        ↓
Static content is displayed to the user
"""

# frontend/pages/signed_out.py


import streamlit as st


def render_signed_out() -> None:
    """
    Renders the page displayed when a user is signed out.
    Provides a welcome message and highlights key technologies.
    """
    st.title("Smart Urban Farming")
    st.write("Sign in from the sidebar to manage plants, watering, locations, " "and companion planting recommendations.")

    cols = st.columns(3)
    cols[0].metric("Backend", "FastAPI")
    cols[1].metric("Reasoning", "Prolog")
    cols[2].metric("Species Data", "Perenual")
