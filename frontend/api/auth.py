"""
API client for authentication-related operations in the Smart Urban Farming application.

Key Point:
Provides functions to interact with the backend authentication endpoints,
handling user login and registration, and managing the authentication token
in the Streamlit session state.

Responsibilities:
- Send login requests to the backend and store the received JWT.
- Send registration requests to the backend and automatically log in the new user.
- Trigger data refresh after successful authentication.

Architecture Role:
- Acts as a bridge between the frontend UI and the backend authentication service.
- Encapsulates the logic for making authentication API calls.

Layer Interaction:
- Communicates with: `api.client` (for making HTTP requests), `state` (for managing session state).
- Called by: Frontend authentication forms/components.

Data Flow:
User enters credentials in UI
        ↓
`login()` or `register()` is called
        ↓
`api_request()` sends data to backend `/auth` endpoints
        ↓
Backend processes request, returns JWT (for login/registration)
        ↓
JWT and user email stored in `st.session_state`
        ↓
`refresh_data()` called to load user-specific data
"""

# frontend/api/auth.py


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
