import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

COLOR_BG_MAIN = "#FFFFFF"
COLOR_PINK_SOFT = "#FFF5F8"
COLOR_PINK_HEADER = "#FFC0CB"
COLOR_PINK_ACCENT = "#FF69B4"

COLOR_TEXT_MAIN = "#2C2C2C"
COLOR_TEXT_SUB = "#888888"
COLOR_TEXT_VAL = "#D81B60"

COLOR_DISCORD = "#9C27B0"
COLOR_WATCHLIST = "#F06292"
COLOR_GOLD = "#FF80AB"

UI_RADIUS = 10

FONT_HEADER = ("Kanit", 16, "bold")
FONT_SUBHEADER = ("Kanit", 12, "bold")
FONT_NORMAL = ("Kanit", 13)
FONT_NUMBER = ("Impact", 36)
FONT_STATS = ("Impact", 22)

LOGO_FILENAME = resource_path("logo.png")
ICON_FILENAME = resource_path("icon.ico")