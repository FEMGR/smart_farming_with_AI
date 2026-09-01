"""
Centralized Color Management Configuration for Streamlit App
Forest Edition (Soft & Premium)

Single source of truth for base tokens, light & dark semantic themes,
status colors, domain-specific care actions, and Streamlit theme injection.
"""

# frontend_streamlit/theme/colours.py

from typing import Dict, Literal

import streamlit as st

ThemeMode = Literal["light", "dark"]

# -----------------------------------------------------------------------------
# 1. BASE COLOR PALETTE (TOKENS) - FOREST EDITION
# -----------------------------------------------------------------------------
FOREST_GREEN = {
    50: "#EAF2EC",
    100: "#CBDECE",
    200: "#B8C6BE",
    300: "#A0C4A5",
    400: "#7AAE83",
    500: "#4F7C59",  # Core Primary
    600: "#3F6847",
    700: "#33553A",
    800: "#26422D",
    900: "#1E2F21",
}

MOSS_GREEN = {
    50: "#F0F3ED",
    100: "#DCE5D6",
    200: "#C5D5C2",
    300: "#98B896",
    400: "#6FB872",  # Core Secondary
    500: "#65B072",
    600: "#5B7A5E",
    700: "#354A3A",
    800: "#2A362C",
    900: "#1D261E",
}

SAGE = {
    50: "#F2F4F1",
    100: "#E2E7E1",
    200: "#CCD7CD",
    300: "#B6C6B7",
    400: "#A8C9B0",
    500: "#7FA18A",  # Core Accent
    600: "#65826E",
    700: "#4D6354",
    800: "#35443A",
    900: "#2F3C33",
}

SOIL_BROWN = {
    50: "#FBF8F4",
    100: "#F1ECE6",
    200: "#E4D7C9",
    300: "#D7C2AF",
    400: "#C9A893",
    500: "#A47F63",
    600: "#8C644F",
    700: "#6C4B3F",
    800: "#5B3A2C",
    900: "#3E261F",
}

AMBER = {
    50: "#FFFAEB",
    100: "#FEF3C7",
    200: "#FDE6B3",
    300: "#FAD67A",
    400: "#F7C359",
    500: "#E0A534",  # Core Warning
    600: "#A37F16",
    700: "#7F5812",
    800: "#634710",
    900: "#5D3E0D",
}

TERRACOTTA = {
    50: "#FFF2F0",
    100: "#FCDAD6",
    200: "#F0B4A0",
    300: "#F08B81",
    400: "#E56363",
    500: "#D54B44",  # Core Error
    600: "#954944",
    700: "#893337",
    800: "#752726",
    900: "#5A1C19",
}

STONE_GRAY = {
    50: "#FAFBF8",
    100: "#F1F3F1",
    200: "#E3E7E3",
    300: "#CCD2CF",
    400: "#A6B0AF",
    500: "#8A938F",
    600: "#60746F",
    700: "#47524B",
    800: "#2A332E",
    900: "#1F2A22",
}

EMERALD = {
    50: "#ECFDF5",
    100: "#D1FAE5",
    200: "#A7F3D0",
    300: "#6EE7B7",
    400: "#34D399",
    500: "#10B981",
    600: "#059669",
    700: "#047857",
    800: "#065F46",
    900: "#064E3B",
}

BLUE = {
    50: "#EFF6FF",
    100: "#DBEAFE",
    200: "#BFDBFE",
    300: "#93C5FD",
    400: "#60A5FA",
    500: "#3B82F6",
    600: "#2563EB",
    700: "#1D4ED8",
    800: "#1E40AF",
    900: "#1E3A8A",
}

CYAN = {
    50: "#ECFEFF",
    100: "#CFFAFE",
    200: "#A5F3FC",
    300: "#67E8F9",
    400: "#22D3EE",
    500: "#06B6D4",
    600: "#0891B2",
    700: "#0E7490",
    800: "#155E75",
    900: "#164E63",
}

COMMON = {
    "white": "#FFFFFF",
    "black": "#0D0D0D",
    "transparent": "transparent",
    "overlay": "rgba(0, 0, 0, 0.45)",
    "lightOverlay": "rgba(0, 0, 0, 0.12)",
}

PALETTE = {
    "forestGreen": FOREST_GREEN,
    "mossGreen": MOSS_GREEN,
    "sage": SAGE,
    "soilBrown": SOIL_BROWN,
    "amber": AMBER,
    "terracotta": TERRACOTTA,
    "stoneGray": STONE_GRAY,
    "emerald": EMERALD,
    "blue": BLUE,
    "cyan": CYAN,
    "common": COMMON,
    "purple": {
        50: "#F5F3FF",
        100: "#EDE9FE",
        500: "#8E7CC3",
        600: "#371c65",
        700: "#6D28D9",
    },
    "red": TERRACOTTA,
    "gray": STONE_GRAY,
}

# -----------------------------------------------------------------------------
# 2. SEMANTIC COLOR CONFIGURATION
# -----------------------------------------------------------------------------
LIGHT_THEME = {
    # Surfaces & Backgrounds
    "background": "#d6dace",
    "backgroundElement": "#F5F7F4",
    "backgroundSelected": "#E2E7E1",
    "surface": "#FFFFFF",
    "surfaceSubtle": "#F5F7F4",
    "card": "#E2F7E3",
    "modal": "#FFFFFF",
    "border": "#E2E7E1",
    # Text Colors
    "text": "#1F2A22",
    "textSecondary": "#47524B",
    "textTertiary": "#6B756F",
    "textMuted": "#8C958F",
    "textInverse": "#FFFFFF",
    # Brand & Palette Colors
    "primary": "#4F7C59",
    "secondary": "#6FB872",
    "accent": "#7FA18A",
    "primaryLight": "#E6FEE8",
    "primaryDark": "#33553A",
    "tint": "#4F7C59",
    "emerald": "#10B981",
    "blue": "#3B82F6",
    "cyan": "#06B6D4",
    # Status Colors
    "success": "#4F7C59",
    "successBackground": "#EAF2EC",
    "successText": "#33553A",
    "warning": "#E0A534",
    "warningBackground": "#FFFAEB",
    "warningText": "#7F5812",
    "error": "#70120d",
    "errorBackground": "#FFF2F0",
    "errorText": "#893337",
    "info": "#4A90A6",
    "infoBackground": "#F2F4F1",
    "infoText": "#35443A",
    # Badges & Tag Highlights
    "badgeSuccessBackground": "rgba(16, 185, 129, 0.1)",
    "badgeSuccessText": "#10B981",
    "badgeWarningBackground": "#FEF3C7",
    "badgeWarningText": "#D97706",
    "badgeErrorBackground": "#FEE2E2",
    "badgeErrorText": "#EF4444",
    # Interactive & Controls
    "borderFocus": "#4F7C59",
    "divider": "#E2E7E1",
    "inputBackground": "#FFFFFF",
    "inputBorder": "#CCD2CF",
    "placeholder": "#8C958F",
    "disabled": "#E3E7E3",
    "disabledText": "#A6B0AF",
    # Domain Specific (Smart Farming Care Actions)
    "careWater": "#06B6D4",
    "careFertilize": "#7FA18A",
    "carePrune": "#8E7CC3",
    "careHarvest": "#6FB872",
}

DARK_THEME = {
    # Surfaces & Backgrounds
    "background": "#0E1411",
    "backgroundElement": "#1F2621",
    "backgroundSelected": "#2A332E",
    "surface": "#161C18",
    "surfaceSubtle": "#1F2621",
    "card": "#1A211D",
    "modal": "#161C18",
    "border": "#2A332E",
    # Text Colors
    "text": "#E6EEE7",
    "textSecondary": "#B0BBB4",
    "textTertiary": "#8A958F",
    "textMuted": "#6D776F",
    "textInverse": "#0E1411",
    # Brand & Palette Colors
    "primary": "#81B28A",
    "secondary": "#9BB896",
    "accent": "#A8C9B0",
    "primaryLight": "rgba(127, 162, 138, 0.15)",
    "primaryDark": "#4F7C59",
    "tint": "#81B28A",
    "emerald": "#81B28A",
    "blue": "#60A5FA",
    "cyan": "#22D3EE",
    # Status Colors
    "success": "#81B28A",
    "successBackground": "rgba(129, 178, 138, 0.15)",
    "successText": "#A8C9B0",
    "warning": "#E0A534",
    "warningBackground": "rgba(224, 165, 52, 0.15)",
    "warningText": "#FAD67A",
    "error": "#E56D63",
    "errorBackground": "rgba(229, 109, 99, 0.15)",
    "errorText": "#F08B81",
    "info": "#2f7e98",
    "infoBackground": "rgba(107, 163, 182, 0.15)",
    "infoText": "#A8C9B0",
    # Badges & Tag Highlights
    "badgeSuccessBackground": "rgba(129, 178, 138, 0.15)",
    "badgeSuccessText": "#81B28A",
    "badgeWarningBackground": "rgba(224, 165, 52, 0.15)",
    "badgeWarningText": "#FAD67A",
    "badgeErrorBackground": "rgba(229, 109, 99, 0.15)",
    "badgeErrorText": "#F08B81",
    # Interactive & Controls
    "borderFocus": "#81B28A",
    "divider": "#1F2621",
    "inputBackground": "#161C18",
    "inputBorder": "#2A332E",
    "placeholder": "#6D776F",
    "disabled": "#1F2621",
    "disabledText": "#6D776F",
    # Domain Specific (Care Actions)
    "careWater": "#22D3EE",
    "careFertilize": "#9BB896",
    "carePrune": "#8E7CC3",
    "careHarvest": "#81B28A",
}

THEME_COLORS = {
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}


# -----------------------------------------------------------------------------
# 3. HELPER UTILITIES & STREAMLIT INJECTION
# -----------------------------------------------------------------------------
def get_theme_colors(scheme: ThemeMode = "light") -> Dict[str, str]:
    """Returns theme color dictionary based on scheme name ('light' | 'dark')."""
    return THEME_COLORS.get(scheme, LIGHT_THEME)


def hex_to_rgba(hex_code: str, alpha: float = 1.0) -> str:
    """Utility to convert Hex color to RGBA string with dynamic opacity."""
    clean_hex = hex_code.lstrip("#")
    if len(clean_hex) != 6:
        return f"rgba(0, 0, 0, {alpha})"
    r = int(clean_hex[0:2], 16)
    g = int(clean_hex[2:4], 16)
    b = int(clean_hex[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def inject_streamlit_theme(mode: ThemeMode = "light") -> None:
    """Injects custom CSS to sync Streamlit elements with the chosen Forest theme."""
    theme = get_theme_colors(mode)

    css = f"""
    <style>
        /* Base App Background & Text */
        .stApp {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}

        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {theme['text']} !important;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background-color: {theme['surface']};
            border-right: 1px solid {theme['border']};
        }}

        /* Cards & Container Containers */
        div[data-testid="stVerticalBlock"] > div[style*="background-color"] {{
            background-color: {theme['card']};
            border-radius: 8px;
            border: 1px solid {theme['border']};
        }}

        /* Input Fields */
        .stTextInput input, .stSelectbox select, .stNumberInput input {{
            background-color: {theme['inputBackground']} !important;
            color: {theme['text']} !important;
            border-color: {theme['inputBorder']} !important;
        }}

        /* Primary Buttons */
        .stButton button[kind="primary"] {{
            background-color: {theme['primary']} !important;
            color: {theme['textInverse']} !important;
            border: none;
        }}

        /* Secondary / Standard Buttons */
        .stButton button {{
            background-color: {theme['surface']} !important;
            color: {theme['text']} !important;
            border: 1px solid {theme['border']} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 4. EXPORTS
# -----------------------------------------------------------------------------
Colors = {
    "palette": PALETTE,
    "theme": THEME_COLORS,
    "light": LIGHT_THEME,
    "dark": DARK_THEME,
}
