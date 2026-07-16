import customtkinter as ctk

BG_WINDOW = "#08090d"
BG_PANEL = "#11161d"
BG_SUBPANEL = "#0b0e14"
BORDER_COLOR = "#1f2937"

COLOR_ACCENT = "#0284c7"
COLOR_ACCENT_HOVER = "#0369a1"
COLOR_DROPDOWN_BG = "#1a2332"

COLOR_SUCCESS = "#10b981"
COLOR_CRITICAL = "#ef4444"
COLOR_CRITICAL_BG = "#161212"
COLOR_CRITICAL_ALERT = "#4a0d0d"

FONT_HUD_TITLE = ("Segoe UI", 11, "bold")
FONT_HUD_REGULAR = ("Segoe UI", 12, "bold")
FONT_HUD_CONSOLE = ("Consolas", 12, "bold")
FONT_HUD_ALERT_TITLE = ("Segoe UI", 12, "bold")
FONT_HUD_ALERT_BODY = ("Consolas", 12)

OPTIONMENU_STYLE = {
    "fg_color": COLOR_DROPDOWN_BG,
    "button_color": COLOR_ACCENT,
    "button_hover_color": COLOR_ACCENT_HOVER,
    "dropdown_fg_color": BG_PANEL,
    "dropdown_hover_color": COLOR_DROPDOWN_BG,
    "dropdown_text_color": "#ffffff",
    "text_color": "#ffffff"
}

TABVIEW_STYLE = {
    "fg_color": BG_PANEL,
    "segmented_button_fg_color": BG_SUBPANEL,
    "segmented_button_selected_color": COLOR_ACCENT,
    "segmented_button_selected_hover_color": COLOR_ACCENT_HOVER,
    "segmented_button_unselected_color": BG_PANEL,
    "segmented_button_unselected_hover_color": COLOR_DROPDOWN_BG,
    "text_color": "#ffffff"
}
