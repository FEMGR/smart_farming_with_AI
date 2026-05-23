# frontend/api/species.py
# Species lookup API helper for autocomplete/search.

from typing import Any

from api.client import api_request


def suggest_species(query: str) -> list[dict[str, Any]]:
    return api_request("GET", "/species/suggest", params={"query": query}) or []
