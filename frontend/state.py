"""
Frontend state management for Streamlit application.

Key Point:
Manages the application's session state, including user authentication, plant data,
location information, notifications, and irrigation needs.

Responsibilities:
- Initialize default values in Streamlit's session state.
- Refresh data from the backend API and update the session state.
- Invalidate cached plant recommendations.
- Clear authentication-related data upon logout.

Architecture Role:
- Centralized store for application-wide data accessible across Streamlit pages.
- Facilitates data flow between backend services and frontend UI components.

Layer Interaction:
- Communicates with: Streamlit's `st.session_state`, `api` module functions.
- Called by: Streamlit app initialization, page components, authentication handlers.

Data Flow:
Application startup/User login
        ↓
`init_state()` sets defaults
        ↓
`refresh_data()` fetches data from backend APIs (plants, locations, notifications, irrigation)
        ↓
`st.session_state` updated with fetched data
        ↓
UI components read from `st.session_state`
        ↓
User logout
        ↓
`clear_auth()` resets authentication and related data in `st.session_state`
"""

# frontend/state.py


import streamlit as st

from api.irrigation import get_needs_water
from api.locations import get_locations
from api.notifications import get_notifications
from api.plants import get_plants


def init_state() -> None:
    """
    Initializes default values in Streamlit's session state.
    Data Flow:
    Application starts
            ↓
    Default values assigned to `st.session_state`
    """
    defaults = {
        "token": None,
        "email": "",
        "plants": [],
        "locations": [],
        "notifications": [],
        "needs_water": [],
        "irrigation_message": "",
    }

    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def refresh_data(show_errors: bool = False) -> None:
    """
    Refreshes various data points in the session state by calling backend APIs.
    Data Flow:
    `refresh_data()` called
            ↓
    Backend APIs invoked
            ↓
    Fetched data updates `st.session_state` variables (e.g., `st.session_state.plants`)
    """
    if not st.session_state.get("token"):
        return

    loaders = {
        "plants": get_plants,
        "locations": get_locations,
        "notifications": get_notifications,
        "needs_water": get_needs_water,
    }

    for key, loader in loaders.items():
        try:
            st.session_state[key] = loader() or []
        except RuntimeError as exc:
            if show_errors:
                st.warning(f"Could not load {key.replace('_', ' ')}: {exc}")


def invalidate_recommendations() -> None:
    """
    Clears cached plant recommendation data from the session state.
    Data Flow:
    Action invalidates recommendations
            ↓
    `st.session_state.recommendations` and `st.session_state.recommendations_generated_for` are removed
    """
    st.session_state.pop("recommendations", None)
    st.session_state.pop("recommendations_generated_for", None)


def clear_auth() -> None:
    """
    Clears all authentication-related data and cached information from the session state.
    Data Flow:
    User logs out
            ↓
    Authentication tokens and user data cleared from `st.session_state`
            ↓
    Cached recommendations also cleared
    """
    st.session_state.token = None
    st.session_state.email = ""
    st.session_state.plants = []
    st.session_state.locations = []
    st.session_state.notifications = []
    st.session_state.needs_water = []
    invalidate_recommendations()
