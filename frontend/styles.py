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
            /* ============================================================
               SOFT FOREST PALETTE
               ============================================================ */

            /* Main brand */
            --primary: #4F7C59;
            --primary-dark: #355B3F;
            --primary-light: rgba(79, 124, 89, 0.14);

            /* Supporting forest tones */
            --secondary: #6F8F72;
            --accent: #8FAF96;

            /* Main UI surfaces */
            --background: #E8EFE7;
            --surface: #F1F5F0;
            --card: #F7F9F6;

            /* Borders */
            --border: #CBD8CC;
            --border-strong: #B8C9BA;

            /* Text */
            --ink: #203027;
            --muted: #59685D;
            --muted-light: #718075;

            /* Status */
            --success: #4F7C59;
            --success-bg: #DDE9DE;

            --warning: #B8924A;
            --warning-bg: #F2E8D0;

            --error: #B85C50;
            --error-bg: #F2DDDA;

            --info: #648E91;
            --info-bg: #DDE9E8;
          }


          /* ============================================================
             APP BACKGROUND
             ============================================================ */

          .stApp {
            background-color: var(--background);
            color: var(--ink);
          }


          .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2.5rem;
          }


          /* ============================================================
             HEADINGS
             ============================================================ */

          h1,
          h2,
          h3,
          h4,
          h5,
          h6 {
            letter-spacing: 0;
            color: var(--ink) !important;
            font-family: system-ui, -apple-system, sans-serif;
          }


          /* ============================================================
             METRIC CARDS
             ============================================================ */

          div[data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            box-shadow: 0 1px 3px rgba(32, 48, 39, 0.05);
          }

          div[data-testid="stMetricLabel"] p {
            color: var(--muted) !important;
            font-weight: 600;
          }

          div[data-testid="stMetricValue"] {
            color: var(--primary) !important;
            font-weight: 700;
          }


          /* ============================================================
             FARM PANELS
             ============================================================ */

          .farm-panel {
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            background: var(--card);
            min-height: 100%;
            box-shadow: 0 1px 3px rgba(32, 48, 39, 0.04);
          }


          .farm-subtle {
            color: var(--muted);
            font-size: 0.92rem;
          }


          /* ============================================================
             STATUS PILLS
             ============================================================ */

          .status-pill {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: var(--ink);
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 0.25rem;
            margin-bottom: 0.25rem;
          }


          /* ============================================================
             PROGRESS BAR
             ============================================================ */

          div[data-testid="stProgress"] > div > div > div {
            background-color: var(--primary) !important;
            border-radius: 4px;
          }

          div[data-testid="stProgress"] > div > div {
            background-color: var(--primary-light) !important;
            border-radius: 4px;
          }


          /* ============================================================
             BUTTONS
             ============================================================ */

          div.stButton > button {
            border-radius: 8px;
            border: 1px solid var(--border);
            background-color: var(--surface);
            color: var(--ink);
            transition: all 0.2s ease;
          }

          div.stButton > button:hover {
            border-color: var(--primary);
            color: var(--primary-dark);
            background-color: var(--card);
          }

          div.stButton > button[kind="primary"] {
            background-color: var(--primary);
            color: #FFFFFF;
            border: none;
          }

          div.stButton > button[kind="primary"]:hover {
            background-color: var(--primary-dark);
            color: #FFFFFF;
          }


          /* ============================================================
             LAYOUT GRID
             ============================================================ */

          .layout-grid {
            display: grid;
            gap: 0.35rem;
            width: 100%;
            overflow-x: auto;
          }


          .layout-cell {
            min-height: 4.5rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            padding: 0.42rem;
            font-size: 0.78rem;
            color: var(--muted);
          }


          .layout-cell.filled {
            background: var(--primary-light);
            border-color: var(--primary);
            color: var(--ink);
          }


          .layout-plant {
            font-weight: 700;
            font-size: 0.88rem;
            line-height: 1.15;
            margin-bottom: 0.25rem;
            color: var(--primary-dark);
          }


          .layout-meta {
            font-size: 0.72rem;
            line-height: 1.2;
            color: var(--muted);
          }


          /* ============================================================
             STATUS COLORS
             ============================================================ */

          .status-success {
            color: var(--success);
            background: var(--success-bg);
          }

          .status-warning {
            color: var(--warning);
            background: var(--warning-bg);
          }

          .status-error {
            color: var(--error);
            background: var(--error-bg);
          }

          .status-info {
            color: var(--info);
            background: var(--info-bg);
          }

        </style>
        """,
        unsafe_allow_html=True,
    )
