"""
Frontend styling and page configuration for the Streamlit application.

Key Point:
Centralizes the visual theme and initial page settings for the Streamlit application,
ensuring a consistent look and feel across all pages using centralized theme tokens.

Responsibilities:
- Configure Streamlit page settings (title, layout, sidebar state).
- Apply custom CSS styles using centralized tokens from theme.colors.

Architecture Role:
- Defines the presentation layer of the frontend_streamlit.
- Separates styling concerns from application logic.

Layer Interaction:
- Communicates with: Streamlit's `st.set_page_config` and `st.markdown` functions.
- Imports from: `theme.colors` (`get_theme_colors`, `hex_to_rgba`).
- Called by: The main Streamlit application file (`streamlit_app.py`) or individual pages.
"""

# frontend_streamlit/styles.py

import streamlit as st
from theme.colours import get_theme_colors, hex_to_rgba, ThemeMode


def apply_page_config() -> None:
    st.set_page_config(
        page_title="Smart Urban Farming",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def apply_styles(mode: ThemeMode = "light") -> None:
    # Resolve semantic theme colors from theme/colors.py
    c = get_theme_colors(mode)

    # Derive semi-transparent helper variations
    primary_light = hex_to_rgba(c["primary"], 0.14)
    ink_shadow = hex_to_rgba(c["text"], 0.05)
    ink_shadow_subtle = hex_to_rgba(c["text"], 0.04)

    st.markdown(
        f"""
        <style>
          :root {{
            /* ============================================================
               DYNAMIC SEMANTIC PALETTE (FROM theme.colors)
               ============================================================ */

            /* Main brand */
            --primary: {c['primary']};
            --primary-dark: {c['primaryDark']};
            --primary-light: {primary_light};

            /* Supporting forest tones */
            --secondary: {c['secondary']};
            --accent: {c['accent']};

            /* Main UI surfaces */
            --background: {c['background']};
            --surface: {c['surface']};
            --card: {c['card']};

            /* Borders */
            --border: {c['border']};
            --border-strong: {c['inputBorder']};

            /* Text */
            --ink: {c['text']};
            --muted: {c['textSecondary']};
            --muted-light: {c['textMuted']};

            /* Status */
            --success: {c['success']};
            --success-bg: {c['successBackground']};

            --warning: {c['warning']};
            --warning-bg: {c['warningBackground']};

            --error: {c['error']};
            --error-bg: {c['errorBackground']};

            --info: {c['info']};
            --info-bg: {c['infoBackground']};
          }}


          /* ============================================================
             APP BACKGROUND
             ============================================================ */

          .stApp {{
            background-color: var(--background);
            color: var(--ink);
          }}


          .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 2.5rem;
          }}


          /* ============================================================
             HEADINGS
             ============================================================ */

          h1,
          h2,
          h3,
          h4,
          h5,
          h6 {{
            letter-spacing: 0;
            color: var(--ink) !important;
            font-family: system-ui, -apple-system, sans-serif;
          }}


          /* ============================================================
             METRIC CARDS
             ============================================================ */

          div[data-testid="stMetric"] {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            box-shadow: 0 1px 3px {ink_shadow};
          }}

          div[data-testid="stMetricLabel"] p {{
            color: var(--muted) !important;
            font-weight: 600;
          }}

          div[data-testid="stMetricValue"] {{
            color: var(--primary) !important;
            font-weight: 700;
          }}


          /* ============================================================
             FARM PANELS
             ============================================================ */

          .farm-panel {{
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            background: var(--card);
            min-height: 100%;
            box-shadow: 0 1px 3px {ink_shadow_subtle};
          }}


          .farm-subtle {{
            color: var(--muted);
            font-size: 0.92rem;
          }}


          /* ============================================================
             STATUS PILLS
             ============================================================ */

          .status-pill {{
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
          }}


          /* ============================================================
             PROGRESS BAR
             ============================================================ */

          div[data-testid="stProgress"] > div > div > div {{
            background-color: var(--primary) !important;
            border-radius: 4px;
          }}

          div[data-testid="stProgress"] > div > div {{
            background-color: var(--primary-light) !important;
            border-radius: 4px;
          }}


          /* ============================================================
             BUTTONS
             ============================================================ */

          div.stButton > button {{
            border-radius: 8px;
            border: 1px solid var(--border);
            background-color: var(--surface);
            color: var(--ink);
            transition: all 0.2s ease;
          }}

          div.stButton > button:hover {{
            border-color: var(--primary);
            color: var(--primary-dark);
            background-color: var(--card);
          }}

          div.stButton > button[kind="primary"] {{
            background-color: var(--primary);
            color: {c['textInverse']};
            border: none;
          }}

          div.stButton > button[kind="primary"]:hover {{
            background-color: var(--primary-dark);
            color: {c['textInverse']};
          }}


          /* ============================================================
             LAYOUT GRID
             ============================================================ */

          .layout-grid {{
            display: grid;
            gap: 0.35rem;
            width: 100%;
            overflow-x: auto;
          }}


          .layout-cell {{
            min-height: 4.5rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: var(--surface);
            padding: 0.42rem;
            font-size: 0.78rem;
            color: var(--muted);
          }}


          .layout-cell.filled {{
            background: var(--primary-light);
            border-color: var(--primary);
            color: var(--ink);
          }}


          .layout-plant {{
            font-weight: 700;
            font-size: 0.88rem;
            line-height: 1.15;
            margin-bottom: 0.25rem;
            color: var(--primary-dark);
          }}


          .layout-meta {{
            font-size: 0.72rem;
            line-height: 1.2;
            color: var(--muted);
          }}


          /* ============================================================
             STATUS COLORS
             ============================================================ */

          .status-success {{
            color: var(--success);
            background: var(--success-bg);
          }}

          .status-warning {{
            color: var(--warning);
            background: var(--warning-bg);
          }}

          .status-error {{
            color: var(--error);
            background: var(--error-bg);
          }}

          .status-info {{
            color: var(--info);
            background: var(--info-bg);
          }}

        </style>
        """,
        unsafe_allow_html=True,
    )
