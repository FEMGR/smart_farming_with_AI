# frontend/api/client.py
# Shared HTTP client for backend requests.
# - Adds auth headers from Streamlit session state.
# - Converts backend error responses into RuntimeError.

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
