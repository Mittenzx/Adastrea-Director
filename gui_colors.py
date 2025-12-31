"""
Centralized color palette for Adastrea Director GUI.
Provides consistent UE5-inspired dark theme colors across all widgets.
"""

# Background colors
BG_PRIMARY = "#20232b"      # Main background
BG_SECONDARY = "#252526"    # Panel background
BG_TERTIARY = "#2d2d30"     # Card/widget background

# Text colors
FG_PRIMARY = "#e3e4e8"      # Main text
FG_SECONDARY = "#858585"    # Muted/disabled text

# Border colors
BORDER_COLOR = "#3e3e42"    # Default borders
BORDER_HIGHLIGHT = "#094771"  # Selection highlight

# Accent colors
ACCENT_BLUE = "#40a9ff"     # Primary actions, info status
ACCENT_BLUE_HOVER = "#5bb8ff"  # Hover state
ACCENT_BLUE_ACTIVE = "#005a9e"  # Active/pressed state

# Status colors
STATUS_SUCCESS = "#4ec9b0"  # Green - success, running, OK
STATUS_WARNING = "#ce9178"  # Orange - warning, attention needed
STATUS_ERROR = "#f48771"    # Red - error, failed, stopped
STATUS_INFO = "#40a9ff"     # Blue - info, idle
STATUS_NEUTRAL = "#858585"  # Gray - unknown, disabled

# Button style colors
BUTTON_PRIMARY_BG = "#40a9ff"
BUTTON_PRIMARY_FG = "#20232b"
BUTTON_PRIMARY_HOVER = "#5bb8ff"

BUTTON_SECONDARY_BG = "#343843"
BUTTON_SECONDARY_FG = "#e3e4e8"
BUTTON_SECONDARY_HOVER = "#4a4e5a"

BUTTON_SUCCESS_BG = "#4ec9b0"
BUTTON_SUCCESS_FG = "#20232b"
BUTTON_SUCCESS_HOVER = "#6dd6c0"

BUTTON_DANGER_BG = "#f48771"
BUTTON_DANGER_FG = "#20232b"
BUTTON_DANGER_HOVER = "#ff9a84"

# Font configuration
FONT_FAMILY = "Segoe UI"  # Default to Segoe UI, can be customized per platform

# Animation timings (milliseconds)
TRANSITION_DURATION = 150
COLLAPSE_DURATION = 200

# Spacing (pixels, based on 5px unit)
SPACING_XXS = 2
SPACING_XS = 5
SPACING_SM = 10
SPACING_MD = 15
SPACING_LG = 20
SPACING_XL = 30
