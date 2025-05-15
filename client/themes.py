"""
Wednesday client theme configuration
"""

# Colors
PRIMARY_COLOR = "#1f71b5"  # Main blue color
SECONDARY_COLOR = "#FF5722"  # Accent orange for highlights
BG_COLOR_DARK = "#0D1117"  # Dark background
BG_COLOR_LIGHT = "#161B22"  # Slightly lighter background
TEXT_COLOR = "#E6EDF3"  # Light text
HIGHLIGHT_COLOR = "#58A6FF"  # Highlight blue
WARNING_COLOR = "#F85149"  # Error/warning red
SUCCESS_COLOR = "#3FB950"  # Success green

# Fonts
MAIN_FONT = ("Roboto", 12)
HEADER_FONT = ("Roboto", 16, "bold")
TITLE_FONT = ("Roboto", 24, "bold")
MONOSPACE_FONT = ("Cascadia Code", 11)

# Text styling
USER_MESSAGE_STYLE = {"foreground": TEXT_COLOR}
ASSISTANT_MESSAGE_STYLE = {"foreground": HIGHLIGHT_COLOR}
USER_TAG_STYLE = {"foreground": SECONDARY_COLOR, "font": ("Roboto", 12, "bold")}
ASSISTANT_TAG_STYLE = {"foreground": PRIMARY_COLOR, "font": ("Roboto", 12, "bold")}

# Button styling
BUTTON_STYLE = {
    "bg_color": PRIMARY_COLOR,
    "hover_color": HIGHLIGHT_COLOR,
    "text_color": TEXT_COLOR,
    "border_width": 0,
    "border_color": PRIMARY_COLOR,
    "corner_radius": 6
}

SECONDARY_BUTTON_STYLE = {
    "bg_color": BG_COLOR_LIGHT,
    "hover_color": "#2D333B",
    "text_color": TEXT_COLOR,
    "border_width": 1,
    "border_color": "#30363D",
    "corner_radius": 6
}

# Animation settings
TYPING_ANIMATION_SPEED = 30  # ms between characters
FADE_ANIMATION_DURATION = 300  # ms for fade animations 