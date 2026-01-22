class Theme:
    # Text Colors - Optimized for dark mode visibility
    TEXT_DEFAULT = "gray10" # Light mode
    TEXT_DEFAULT_DARK = "#E0E0E0" # Dark mode - much lighter for visibility
    
    TEXT_STATUS_NEUTRAL = "#FFFFFF"  # Pure White for better readability
    TEXT_STATUS_SUCCESS = "#2cc985" # Bright Green
    TEXT_STATUS_ERROR = "#ff4d4d"   # Bright Red
    TEXT_STATUS_INFO = "#3b8ed0"    # Bright Blue
    TEXT_DIM = "#CCCCCC"  # Lighter gray for dim text

    # Aliases
    TEXT_ERROR = TEXT_STATUS_ERROR
    TEXT_SUCCESS = TEXT_STATUS_SUCCESS
    TEXT_NORMAL = TEXT_STATUS_NEUTRAL  # Use light gray instead of default

    # Button Colors
    BTN_PRIMARY = "#1f6aa5"
    BTN_PRIMARY_TEXT = "white"
    
    BTN_SECONDARY = "#606060"
    BTN_INFO = "#3b8ed0"
    
    BTN_WARNING = "#FF9800" # Better Orange
    BTN_WARNING_HOVER = "#F57C00" # Darker Orange for hover
    BTN_WARNING_TEXT = "#000000" # Black for contrast on orange
    
    BTN_DANGER = "#C62828" # Red for Danger/Delete
    BTN_SUCCESS = "#158c56" # Darker Green for Success/Generate
    BTN_SUCCESS_HOVER = "#106e42" # Even darker for hover

    # Backgrounds
    BG_COLOR_2 = "#333333" # Lighter background for headers/bars

    # Font
    FONT_HEADER = ("Arial", 20)
    FONT_BOLD = ("Arial", 12, "bold")
