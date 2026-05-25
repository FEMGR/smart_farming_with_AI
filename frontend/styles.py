"""
Frontend styling and page configuration for the Streamlit application.

Key Point:
Centralizes the visual theme and initial page settings for the Streamlit application,
ensuring a consistent look and feel across all pages.

Responsibilities:
- Configure Streamlit page settings (title, layout, sidebar state).
- Apply custom CSS styles to override Streamlit's defaults and define a visual system.

Architecture Role:
- Defines the presentation layer of the frontend.
- Separates styling concerns from application logic.

Layer Interaction:
- Communicates with: Streamlit's `st.set_page_config` and `st.markdown` functions.
- Called by: The main Streamlit application file (`streamlit_app.py`) or individual pages
  to set up their appearance.

Data Flow:
Application starts
        ↓
`apply_page_config()` sets global page properties
        ↓
`apply_styles()` injects custom CSS rules into the Streamlit app
        ↓
UI components render according to the defined styles
"""

# frontend/styles.py

import streamlit as st


def apply_page_config() -> None:
    st.set_page_config(
        page_title="Smart Urban Farming",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_styles() -> None:
    st.markdown(
        """
        <style>
          :root {
            --border: #d8dfd6;
            --surface: #f7faf5;
            --ink: #172118;
            --muted: #647067;
            --accent: #2f6f4e;
          }

          .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2.5rem;
          }

          h1, h2, h3 {
            letter-spacing: 0;
            color: var(--ink);
          }

          div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.9rem 1rem;
          }

          div[data-testid="stMetricLabel"] p {
            color: var(--muted);
          }

          .farm-panel {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            background: #ffffff;
            min-height: 100%;
          }

          .farm-subtle {
            color: var(--muted);
            font-size: 0.92rem;
          }

          .status-pill {
            display: inline-block;
            padding: 0.12rem 0.5rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--ink);
            font-size: 0.78rem;
            margin-right: 0.25rem;
            margin-bottom: 0.25rem;
          }

          .layout-grid {
            display: grid;
            gap: 0.35rem;
            width: 100%;
            overflow-x: auto;
          }

          .layout-cell {
            min-height: 4.5rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: #fbfcfa;
            padding: 0.42rem;
            font-size: 0.78rem;
            color: var(--muted);
          }

          .layout-cell.filled {
            background: #edf6ef;
            border-color: #96baa1;
            color: var(--ink);
          }

          .layout-plant {
            font-weight: 700;
            font-size: 0.88rem;
            line-height: 1.15;
            margin-bottom: 0.25rem;
          }

          .layout-meta {
            font-size: 0.72rem;
            line-height: 1.2;
            color: var(--muted);
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
