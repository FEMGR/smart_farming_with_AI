# frontend/state.py
# Streamlit session state helpers.
# - init_state creates default values used by pages.
# - refresh_data reloads backend data into session_state.
# - auth cleanup also clears cached recommendations.

import streamlit as st

from api.irrigation import get_needs_water
from api.locations import get_locations
from api.notifications import get_notifications
from api.plants import get_plants


def init_state() -> None:
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
    st.session_state.pop("recommendations", None)
    st.session_state.pop("recommendations_generated_for", None)


def clear_auth() -> None:
    st.session_state.token = None
    st.session_state.email = ""
    st.session_state.plants = []
    st.session_state.locations = []
    st.session_state.notifications = []
    st.session_state.needs_water = []
    invalidate_recommendations()
