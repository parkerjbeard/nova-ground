# Styles and constants for GUI components

# Colors
BACKGROUND_COLOR = "#2E2E2E"
TEXT_COLOR = "#FFFFFF"
BUTTON_COLOR = "#3C3C3C"
BUTTON_HOVER_COLOR = "#555555"
BUTTON_PRESS_COLOR = "#1E1E1E"
GAUGE_COLOR = "#4CAF50"
GRAPH_BG_COLOR = "#3C3C3C"

# Fonts
DEFAULT_FONT = "Arial"
TITLE_FONT = "Arial Bold"
LCD_FONT = "Arial"

# Dimensions
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
DASHBOARD_WIDTH = 300
CONTROLS_HEIGHT = 100

# Stylesheets
MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {BACKGROUND_COLOR};
    }}
"""

BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {BUTTON_COLOR};
        color: {TEXT_COLOR};
        border: none;
        padding: 10px;
        font: 14px {DEFAULT_FONT};
    }}
    QPushButton:hover {{
        background-color: {BUTTON_HOVER_COLOR};
    }}
    QPushButton:pressed {{
        background-color: {BUTTON_PRESS_COLOR};
    }}
"""

LCD_NUMBER_STYLE = f"""
    QLCDNumber {{
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
        border: 1px solid {TEXT_COLOR};
        font: 16px {LCD_FONT};
    }}
"""

LABEL_STYLE = f"""
    QLabel {{
        color: {TEXT_COLOR};
        font: 14px {DEFAULT_FONT};
    }}
"""

GAUGE_STYLE = f"""
    QProgressBar {{
        border: 1px solid {TEXT_COLOR};
        text-align: center;
        color: {TEXT_COLOR};
        font: 12px {DEFAULT_FONT};
    }}
    QProgressBar::chunk {{
        background-color: {GAUGE_COLOR};
    }}
"""

GRAPH_STYLE = f"""
    QWidget {{
        background-color: {GRAPH_BG_COLOR};
    }}
"""