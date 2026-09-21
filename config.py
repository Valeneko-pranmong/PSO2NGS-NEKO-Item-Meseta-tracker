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
APP_VERSION = "V 7.1.0"
CLIENT_VERSION = "7.1.0"
MIN_SECURE_VERSION = "7.1.0"
REVOKED_VERSIONS = ["7.0.0-alpha", "7.0.0"]

# Internationalization (i18n) - 3 Languages: English (Primary/Default), Thai, Japanese
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ["en", "th", "ja"]

# ARKS War Room Web URL
DEFAULT_WAR_ROOM_URL = os.getenv(
    "WAR_ROOM_URL",
    os.getenv(
        "ARKS_WAR_ROOM_URL",
        "https://arks-war-room.vercel.app/",
    ),
)

# Discord Community & Credit
DEFAULT_DISCORD_URL = os.getenv("DISCORD_URL", "https://discord.gg/fkjXW9AJ6a")
DISCORD_INVITE_SHORT = "discord.gg/fkjXW9AJ6a"
DISCORD_COMMUNITY_NAME = "NEKO★FAMILY PSO2:NGS Community"
DISCORD_CREDIT_FULL = "NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a"

# Firebase Realtime Database
DEFAULT_FIREBASE_RTDB_URL = os.getenv(
    "FIREBASE_RTDB_URL",
    os.getenv(
        "ARKS_FIREBASE_RTDB_URL",
        "https://arks-war-room-default-rtdb.asia-southeast1.firebasedatabase.app",
    ),
)

# Coordinate Grid & Sub-Cell Defaults (Coordinate War Engine V9 Release)
# Authoritative Reference: Coordinate War Specification V9
# Core Rule: "เกมแค่เติมเงินเข้าไปในช่อง ใครใส่เยอะคนนั้นเป็นเจ้าของ"
SECTOR_X_MIN = -12
SECTOR_X_MAX = 25
SECTOR_Y_MIN = -11
SECTOR_Y_MAX = 9
SLOT_MIN = 1
SLOT_MAX = 4
SLOT_TARGET_MESETA = 10_000_000       # 10M per sub-cell capture threshold (V9 Release)
SECTOR_TARGET_MESETA = 40_000_000     # 40M total per macro sector (4 slots x 10M to fully liberate)

# Anti-Tamper & Security Heuristic Thresholds
MAX_SINGLE_MESETA_DROP = 300_000          # Maximum realistic single drop
MAX_MESETA_PER_MINUTE = 250_000           # ~15M/hr ceiling (physically impossible in NGS)
MAX_FUTURE_TIMESTAMP_SKEW_SEC = 60.0      # Max allowable future clock skew (seconds)
MAX_PAST_TIMESTAMP_SKEW_SEC = 300.0       # 5 minutes max historical replay (seconds)
MAX_SEQUENCE_JUMP_ALERT = 5000            # Sequence jump threshold for anomaly warning
MIN_CADENCE_SAMPLE_SIZE = 10
MIN_CADENCE_STDDEV_SEC = 0.05

# Test Mode detection (CLI flag or environment variable)
IS_TEST_MODE = (
    os.getenv("NEKO_TEST_MODE", "0").lower() in ("1", "true", "yes")
    or "--test" in sys.argv
    or "--test-mode" in sys.argv
    or "--mock" in sys.argv
)

if IS_TEST_MODE:
    ENFORCE_PROCESS_VALIDATION = os.getenv("NEKO_PROCESS_VALIDATION", "0").lower() in ("1", "true", "yes")
    ENFORCE_FILE_HANDLE_VALIDATION = os.getenv("NEKO_FILE_HANDLE_VALIDATION", "0").lower() in ("1", "true", "yes")
    ENFORCE_CANONICAL_PATH_GATING = os.getenv("NEKO_CANONICAL_PATH_GATING", "0").lower() in ("1", "true", "yes")
    ENFORCE_CADENCE_VALIDATION = os.getenv("NEKO_CADENCE_VALIDATION", "0").lower() in ("1", "true", "yes")
    ENFORCE_TIMESTAMP_VALIDATION = os.getenv("NEKO_TIMESTAMP_VALIDATION", "0").lower() in ("1", "true", "yes")
    ENFORCE_VELOCITY_VALIDATION = os.getenv("NEKO_VELOCITY_VALIDATION", "0").lower() in ("1", "true", "yes")
else:
    ENFORCE_PROCESS_VALIDATION = os.getenv("NEKO_PROCESS_VALIDATION", "1").lower() not in ("0", "false", "no")
    ENFORCE_FILE_HANDLE_VALIDATION = os.getenv("NEKO_FILE_HANDLE_VALIDATION", "1").lower() not in ("0", "false", "no")
    ENFORCE_CANONICAL_PATH_GATING = os.getenv("NEKO_CANONICAL_PATH_GATING", "0").lower() in ("1", "true", "yes")
    ENFORCE_CADENCE_VALIDATION = os.getenv("NEKO_CADENCE_VALIDATION", "1").lower() not in ("0", "false", "no")
    ENFORCE_TIMESTAMP_VALIDATION = os.getenv("NEKO_TIMESTAMP_VALIDATION", "1").lower() not in ("0", "false", "no")
    ENFORCE_VELOCITY_VALIDATION = os.getenv("NEKO_VELOCITY_VALIDATION", "1").lower() not in ("0", "false", "no")


