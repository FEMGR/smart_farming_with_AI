"""
Frontend page for querying pest knowledge.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from api.knowledge import get_pest_profile


def _display_name(value: Any) -> str:
    return str(value or "").replace("_", " ").strip().title()


def _source_label(record: dict[str, Any]) -> str:
    parts = []
    source = record.get("source")
    confidence = record.get("confidence")
    confidence_score = record.get("confidence_score")

    if source:
        parts.append(str(source).upper())
    if confidence:
        parts.append(f"confidence {confidence}")
    elif isinstance(confidence_score, (int, float)):
        parts.append(f"score {confidence_score:.2f}")

    return " · ".join(parts)


def _plant_from_record(record: dict[str, Any]) -> dict[str, Any]:
    plant = record.get("plant")
    return plant if isinstance(plant, dict) else {}


def _render_plant_records(title: str, records: list[dict[str, Any]], empty_text: str) -> None:
    with st.expander(title, expanded=True):
        if not records:
            st.caption(empty_text)
            return

        for record in records:
            plant = _plant_from_record(record)
            species = plant.get("species") or {}
            name = plant.get("name") or _display_name(plant.get("atom"))
            image_url = species.get("thumbnail_url") or species.get("default_image_url")

            with st.container(border=True):
                cols = st.columns([1, 4])
                if image_url:
                    cols[0].image(image_url, width="stretch")
                else:
                    cols[0].caption("No image")

                cols[1].write(f"**{name or 'Unknown plant'}**")
                if species:
                    cols[1].caption(species.get("scientific_name") or species.get("common_name") or "Species matched from database")
                else:
                    cols[1].caption("Plant from Prolog knowledge base")

                label = _source_label(record)
                if label:
                    cols[1].markdown(f'<span class="status-pill">{label}</span>', unsafe_allow_html=True)


def _render_predators(records: list[dict[str, Any]]) -> None:
    with st.expander("Predators", expanded=True):
        if not records:
            st.caption("No predators are recorded for this pest.")
            return

        for record in records:
            name = record.get("name") or _display_name(record.get("predator"))
            st.markdown(f'<span class="status-pill">{name}</span>', unsafe_allow_html=True)


def _render_damage_symptoms(records: list[dict[str, Any]]) -> None:
    with st.expander("Damage Symptoms", expanded=True):
        if not records:
            st.caption("No damage symptoms are recorded for this pest.")
            return

        for record in records:
            name = record.get("name") or _display_name(record.get("symptom"))
            st.markdown(f"- {name}")


def _render_sources(records: list[dict[str, Any]]) -> None:
    with st.expander("Sources", expanded=False):
        if not records:
            st.caption("No explicit sources are recorded for this pest.")
            return

        for record in records:
            source = record.get("source") or record
            st.markdown(f'<span class="status-pill">{source}</span>', unsafe_allow_html=True)


def render_pest_query() -> None:
    st.subheader("Pest Query")

    query = st.text_input("Search pest", placeholder="aphids, thrips, flea beetles, spider mites")

    if not query:
        st.caption("Search a pest name to query the Prolog knowledge base and matched plant database records.")
        return

    try:
        with st.spinner("Querying pest knowledge..."):
            profile = get_pest_profile(query)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    pest_name = profile.get("pest") or _display_name(query)
    normalized = profile.get("normalized_pest")

    st.write(f"**{pest_name}**")
    if normalized:
        st.markdown(f'<span class="status-pill">atom {normalized}</span>', unsafe_allow_html=True)

    deterrents = profile.get("deterrents") or []
    hosts = profile.get("hosts") or []
    predators = profile.get("predators") or []
    symptoms = profile.get("damage_symptoms") or []
    sources = profile.get("sources") or []

    metric_cols = st.columns(4)
    metric_cols[0].metric("Deterrents", len(deterrents))
    metric_cols[1].metric("Host plants", len(hosts))
    metric_cols[2].metric("Predators", len(predators))
    metric_cols[3].metric("Symptoms", len(symptoms))

    _render_plant_records("Deterrent Plants", deterrents, "No deterrent plants are recorded for this pest.")
    _render_plant_records("Host Plants", hosts, "No host plants are recorded for this pest.")
    _render_predators(predators)
    _render_damage_symptoms(symptoms)
    _render_sources(sources)
