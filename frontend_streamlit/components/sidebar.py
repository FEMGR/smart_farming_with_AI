# frontend_streamlit/components/sidebar.py
# Sidebar component.
# - Shows API target and signed-in status.
# - Handles refresh, sign out, login, and registration.

import streamlit as st

from api.auth import login, register
from config import API_BASE_URL
from state import clear_auth, refresh_data


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Farm Console")
        st.caption(f"API: {API_BASE_URL}")

        if st.session_state.get("token"):
            st.write(st.session_state.get("email") or "Signed in")

            cols = st.columns(2)

            if cols[0].button("Refresh", width="stretch"):
                refresh_data(show_errors=True)
                st.rerun()

            if cols[1].button("Sign out", width="stretch"):
                clear_auth()
                st.rerun()

            st.divider()
            st.caption("Set SMART_FARMING_API_URL to point this dashboard at another backend.")
            return

        mode = st.radio("Access", ["Login", "Register"], horizontal=True)

        with st.form("auth_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button(mode, width="stretch")

        if submitted:
            try:
                if mode == "Register":
                    register(email, password)
                else:
                    login(email, password)

                st.rerun()
            except RuntimeError as exc:
                st.error(str(exc))
