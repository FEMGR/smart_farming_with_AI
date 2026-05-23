# frontend/api/auth.py
# Authentication API helpers.
# - login stores the JWT and refreshes dashboard data.
# - register creates an account, then signs in.

import streamlit as st

from api.client import api_request
from state import refresh_data


def login(email: str, password: str) -> None:
    payload = {"username": email, "password": password}
    token = api_request("POST", "/auth/login", data=payload, auth=False)

    st.session_state.token = token["access_token"]
    st.session_state.email = email

    refresh_data(show_errors=True)


def register(email: str, password: str) -> None:
    api_request(
        "POST",
        "/auth/register",
        json={"email": email, "password": password},
        auth=False,
    )
    login(email, password)
