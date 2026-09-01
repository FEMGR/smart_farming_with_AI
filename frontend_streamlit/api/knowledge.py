"""
API helpers for Prolog-backed knowledge queries.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from api.client import api_request


def get_pest_profile(pest: str) -> dict[str, Any]:
    pest_path = quote(pest.strip(), safe="")
    return api_request("GET", f"/knowledge/pests/{pest_path}") or {}
