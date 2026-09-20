import os
import sys
import ctypes

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_custom_fonts():
    """Register bundled fonts with Windows GDI so Tkinter/CustomTkinter can render them."""
    loaded_sarabun = False
    if sys.platform == "win32":
        try:
            gdi32 = ctypes.windll.gdi32
            FR_PRIVATE = 0x10
            font_files = [
                "fonts/Sarabun-Regular.ttf",
                "fonts/Sarabun-Medium.ttf",
                "fonts/Sarabun-SemiBold.ttf",
                "fonts/Sarabun-Bold.ttf",
                "fonts/Kanit-Regular.ttf",
                "fonts/Kanit-Medium.ttf",
                "fonts/Kanit-SemiBold.ttf",
                "fonts/Kanit-Bold.ttf",
            ]
            for rel_path in font_files:
                full_path = resource_path(rel_path)
                if os.path.exists(full_path):
                    res = gdi32.AddFontResourceExW(full_path, FR_PRIVATE, 0)
                    if res > 0 and "Sarabun" in rel_path:
                        loaded_sarabun = True
        except Exception as e:
            print(f"[config] Warning: Failed to load bundled fonts: {e}")
    return loaded_sarabun

_sarabun_available = load_custom_fonts()
FONT_FAMILY = "Sarabun" if _sarabun_available else "Leelawadee UI"

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

FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_HEADER = (FONT_FAMILY, 15, "bold")
FONT_SUBHEADER = (FONT_FAMILY, 12, "bold")
FONT_NORMAL = (FONT_FAMILY, 12)
FONT_SMALL = (FONT_FAMILY, 11)
FONT_NUMBER = ("Impact", 36)
FONT_STATS = ("Impact", 22)

LOGO_FILENAME = resource_path("logo.png")
ICON_FILENAME = resource_path("icon.ico")
APP_VERSION = "V 6.1.0"

# Firebase Realtime Database
DEFAULT_FIREBASE_RTDB_URL = os.getenv(
    "FIREBASE_RTDB_URL",
    os.getenv(
        "ARKS_FIREBASE_RTDB_URL",
        "https://arks-war-room-default-rtdb.asia-southeast1.firebasedatabase.app",
    ),
)

# Coordinate Grid & Sub-Cell Defaults (Sector + 4 Slots)
SECTOR_X_MIN = -12
SECTOR_X_MAX = 25
SECTOR_Y_MIN = -11
SECTOR_Y_MAX = 9
SLOT_MIN = 1
SLOT_MAX = 4
SLOT_TARGET_MESETA = 25_000_000    # 25M per sub-cell
SECTOR_TARGET_MESETA = 100_000_000 # 100M total per sector (4 slots)

