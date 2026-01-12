class Theme:
    # Text Colors
    TEXT_DEFAULT = "gray10" # Light mode
    TEXT_DEFAULT_DARK = "gray90" # Dark mode (handled by CTk usually, but for specific labels)
    
    TEXT_STATUS_NEUTRAL = "white"
    TEXT_STATUS_SUCCESS = "#2cc985" # Bright Green
    TEXT_STATUS_ERROR = "#ff4d4d"   # Bright Red
    TEXT_STATUS_INFO = "#3b8ed0"    # Bright Blue

    # Button Colors
    BTN_PRIMARY = "#1f6aa5"
    BTN_PRIMARY_TEXT = "white"
    
    BTN_WARNING = "orange"
    BTN_WARNING_TEXT = "#000000" # Black for contrast on orange

    # Font
    FONT_HEADER = ("Arial", 20)
    FONT_BOLD = ("Arial", 12, "bold")
