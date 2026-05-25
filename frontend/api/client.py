"""
Shared HTTP client for making requests to the FastAPI backend.

Key Point:
Provides a centralized function for all API interactions, handling authentication
headers, error responses, and JSON parsing consistently.

Responsibilities:
- Construct full API URLs using the base URL from `config.py`.
- Attach authentication headers (JWT bearer token) from Streamlit's session state.
- Execute HTTP requests (GET, POST, PUT, DELETE, PATCH).
- Handle network errors and API-specific error responses, raising `RuntimeError` for clarity.
- Parse JSON responses or return raw text if JSON parsing fails.

Architecture Role:
- Acts as the foundational layer for all frontend-to-backend communication.
- Ensures consistency and robustness in API calls.

Layer Interaction:
- Communicates with: `config` (for `API_BASE_URL`), `streamlit` (for `st.session_state`),
  `requests` library (for HTTP operations).
- Called by: All other API client modules (e.g., `api.auth`, `api.plants`).

Data Flow:
Frontend component needs to interact with backend
        ↓
Calls a specific API helper function (e.g., `api.plants.get_plants()`)
        ↓
API helper function calls `api_request()`
        ↓
`api_request()` constructs URL, adds auth headers, sends HTTP request
        ↓
Backend processes request and sends response
        ↓
`api_request()` handles response (error checking, JSON parsing)
        ↓
Result (data or error) returned to the calling API helper function
"""

# frontend/api/client.py


from __future__ import annotations

from typing import Any

import requests
import streamlit as st

from config import API_BASE_URL


def auth_headers() -> dict[str, str]:
    # Central place for bearer token construction.
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def api_request(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    auth: bool = True,
) -> Any:
    # All page-specific API helpers call through this function.
    url = f"{API_BASE_URL}{path}"
    headers = auth_headers() if auth else {}

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json,
            data=data,
            params=params,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Cannot reach API at {API_BASE_URL}: {exc}") from exc

    if response.status_code >= 400:
        detail = response.text
        try:
            detail = response.json().get("detail", detail)
        except ValueError:
            pass
        raise RuntimeError(f"{response.status_code}: {detail}")

    if not response.content:
        return None

    try:
        return response.json()
    except ValueError:
        return response.text
