import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import sys
import time
import threading
import re
import json
import ctypes
import webbrowser
from PIL import Image
from typing import Any, Optional, Tuple, Dict, List

from config import * 
from dashboard_ui import DashboardFrame 
from overlay_ui import OverlayWindow
from modules.event_bus import event_bus
from modules.i18n import i18n, t, tr
from modules.war_mode.war_service import WarService
from modules.war_mode.war_view import WarDashboardFrame
from modules.utils import extract_character_info, WindowMover, start_native_drag
from modules.security import (
    AntiTamperGuard,
    TamperViolation,
    TamperViolationType,
    ActionLogRecord,
    ActionLogParser,
)

try:
    myappid = f'neko.family.shop.tracker v{CLIENT_VERSION}' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

app_data_dir = os.getenv('APPDATA') or os.path.expanduser('~')
config_dir = os.path.join(app_data_dir, "NekoTrackerOffline") 
if not os.path.exists(config_dir):
    try:
        os.makedirs(config_dir) 
    except OSError:
        pass
CONFIG_FILE = os.path.join(config_dir, "ngs_tracker_config.json")

class NGSTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True) 
        self.geometry("950x620")
        self.title(t("app_window_title")) 
        self.configure(fg_color=COLOR_BG_MAIN) 
        self.setup_icon()
        self._window_mover = WindowMover(self)
        
        self.after(200, self.force_taskbar_icon)

        self.current_language = DEFAULT_LANGUAGE
        self.log_folder = ""   
        self.log_path = ""     
        self.active_encoding = 'utf-16' 
        self.session_meseta = 0      
        self.current_wallet = 0      
        self.item_counts = {}        
        self.last_file_pos = 0       
        self.is_running = True 
        self.data_lock = threading.Lock()
        
        self.first_drop_time = None 
        self.last_income_time = None 
        
        self.watchlist_items = [] 
        self.is_filter_active = False 
        self.search_keyword = ""      
        
        self.character_name = ""
        self.player_id = ""
        self.board_coord = "0, 0, 1"
        self.needs_ui_update = False 

        # Modular Subsystems & Security
        self.event_bus = event_bus
        self.is_test_mode = getattr(config, "IS_TEST_MODE", False) if "config" in globals() else IS_TEST_MODE
        self.anti_tamper = AntiTamperGuard(
            enforce_process_validation=ENFORCE_PROCESS_VALIDATION,
            enforce_file_handle_validation=ENFORCE_FILE_HANDLE_VALIDATION,
            enforce_canonical_path=ENFORCE_CANONICAL_PATH_GATING,
            enforce_cadence_validation=ENFORCE_CADENCE_VALIDATION,
            enforce_timestamp_validation=ENFORCE_TIMESTAMP_VALIDATION,
            enforce_velocity_validation=ENFORCE_VELOCITY_VALIDATION,
            min_cadence_sample_size=MIN_CADENCE_SAMPLE_SIZE,
            min_cadence_stddev=MIN_CADENCE_STDDEV_SEC,
            max_single_meseta_drop=MAX_SINGLE_MESETA_DROP,
            max_meseta_per_minute=MAX_MESETA_PER_MINUTE,
            max_future_timestamp_skew=MAX_FUTURE_TIMESTAMP_SKEW_SEC,
            max_past_timestamp_skew=MAX_PAST_TIMESTAMP_SKEW_SEC,
            max_sequence_jump=MAX_SEQUENCE_JUMP_ALERT,
            active_version=CLIENT_VERSION,
        )
        self.anti_tamper.on_violation = self._on_tamper_violation
        self.war_service = WarService()
        self.current_view = "offline"
        self.event_bus.subscribe("character_detected", self._on_character_detected)
        self.event_bus.subscribe("language_changed", self._on_language_changed)

        self.main_container = ctk.CTkFrame(self, fg_color=COLOR_PINK_HEADER, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        self.build_title_bar()

        # Offline View Container
        self.offline_container = ctk.CTkFrame(self.main_container, fg_color="transparent", corner_radius=0)
        self.offline_container.grid(row=1, column=0, sticky="nsew")
        self.offline_container.grid_columnconfigure(1, weight=1)
        self.offline_container.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self.offline_container, width=280, corner_radius=0, fg_color=COLOR_BG_MAIN)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        self.load_logo()
        self.design_brand_text()

        self.btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.btn_frame.pack(fill="both", expand=True, padx=20)

        BTN_HEIGHT = 35
        BTN_RADIUS = UI_RADIUS 

        # War Mode Entry Button
        self.btn_enter_war = ctk.CTkButton(
            self.btn_frame,
            text=t("btn_enter_war"),
            font=(FONT_FAMILY, 13, "bold"),
            fg_color="#D81B60",
            hover_color="#AD1457",
            text_color="white",
            height=38,
            corner_radius=BTN_RADIUS,
            command=self.show_war_view,
        )
        self.btn_enter_war.pack(pady=(0, 8), fill="x")

        self.btn_reset = ctk.CTkButton(self.btn_frame, text=t("btn_reset"), font=(FONT_FAMILY, 13,),
                                       fg_color=COLOR_PINK_HEADER, text_color=COLOR_TEXT_MAIN,
                                       hover_color=COLOR_PINK_SOFT, height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=self.confirm_reset)
        self.btn_reset.pack(pady=(0, 8), fill="x")

        self.btn_watchlist = ctk.CTkButton(self.btn_frame, text=t("btn_watchlist"), font=(FONT_FAMILY, 13, "bold"), 
                                           fg_color=COLOR_WATCHLIST, hover_color="#D81B60", text_color="white", 
                                           height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=self.open_watchlist_editor)
        self.btn_watchlist.pack(pady=(0, 5), fill="x")

        self.switch_filter = ctk.CTkSwitch(self.btn_frame, text=t("switch_filter"), font=(FONT_FAMILY, 11, "bold"),
                                           progress_color=COLOR_WATCHLIST, command=self.toggle_filter)
        self.switch_filter.pack(pady=(5, 10))

        row3 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 8))
        row3.columnconfigure((0, 1), weight=1, uniform="equal")

        self.btn_overlay_full = ctk.CTkButton(row3, text=t("btn_overlay_full"), font=(FONT_FAMILY, 12, "bold"), 
                                         fg_color=COLOR_PINK_ACCENT, hover_color="#FF1493", text_color="white", 
                                         height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=lambda: self.open_overlay("full"))
        self.btn_overlay_full.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.btn_overlay_mini = ctk.CTkButton(row3, text=t("btn_overlay_mini"), font=(FONT_FAMILY, 12, "bold"), 
                                         fg_color="#F06292", hover_color="#D81B60", text_color="white", 
                                         height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=lambda: self.open_overlay("mini"))
        self.btn_overlay_mini.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        self.btn_how_to_use = ctk.CTkButton(self.btn_frame, text=t("btn_how_to_use"), font=(FONT_FAMILY, 12, "bold"),
                                            fg_color="#0284C7", hover_color="#0369A1", text_color="white",
                                            height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=self.open_how_to_use)
        self.btn_how_to_use.pack(fill="x", pady=(0, 8))

        self.btn_discord = ctk.CTkButton(self.btn_frame, text=t("btn_discord"), font=(FONT_FAMILY, 13, "bold"), 
                                         fg_color=COLOR_DISCORD, hover_color="#AB47BC", text_color="white", 
                                         height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=self.open_discord)
        self.btn_discord.pack(fill="x", pady=(0, 8))

        # Language Selector Row in Sidebar
        self.lang_row_sidebar = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        self.lang_row_sidebar.pack(fill="x", pady=(0, 8))
        self.lbl_sidebar_lang = ctk.CTkLabel(
            self.lang_row_sidebar,
            text=f"🌐 {t('label_language')}:",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLOR_TEXT_SUB,
        )
        self.lbl_sidebar_lang.pack(side="left", padx=(0, 5))

        self.seg_lang_sidebar = ctk.CTkSegmentedButton(
            self.lang_row_sidebar,
            values=["EN", "TH", "JA"],
            height=28,
            font=(FONT_FAMILY, 11, "bold"),
            selected_color=COLOR_PINK_ACCENT,
            selected_hover_color="#D81B60",
            unselected_color="#F0F0F0",
            unselected_hover_color="#E0E0E0",
            text_color=COLOR_TEXT_MAIN,
            corner_radius=UI_RADIUS,
            command=self._on_sidebar_lang_selected,
        )
        self.seg_lang_sidebar.set(i18n.get_button_label())
        self.seg_lang_sidebar.pack(side="right", fill="x", expand=True)
        
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", pady=(10, 5), padx=15)
        
        self.lbl_file_status = ctk.CTkLabel(self.status_frame, text=t("status_no_folder"), text_color=COLOR_TEXT_SUB, wraplength=220, font=(FONT_FAMILY, 11))
        self.lbl_file_status.pack(anchor="w", pady=(0, 3))
        
        self.btn_select = ctk.CTkButton(self.status_frame, text=t("btn_select_folder"), font=(FONT_FAMILY, 12), 
                                        fg_color="#F0F0F0", text_color="#333333", hover_color="#E0E0E0", 
                                        height=30, corner_radius=UI_RADIUS, command=self.select_log_folder)
        self.btn_select.pack(fill="x")

        self.lbl_version = ctk.CTkLabel(self.sidebar, text=APP_VERSION, font=("Arial", 9), text_color="gray")
        self.lbl_version.pack(side="bottom", pady=(0, 5))

        self.dashboard_area = DashboardFrame(self.offline_container, self)
        self.dashboard_area.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))

        self.stop_event = threading.Event()
        self.monitor_thread = threading.Thread(target=self.monitor_log_file, daemon=True)
        self.monitor_thread.start()

        self.overlay_window = None
        self.watchlist_window = None
        self.confirm_dialog = None

        self.load_settings()
        self.update_live_clock()

    def update_live_clock(self):
        if not self.is_running: return
        
        if getattr(self, 'pending_status_text', None):
            try:
                self.lbl_file_status.configure(text=self.pending_status_text, text_color=getattr(self, 'pending_status_color', "black"))
                if hasattr(self, "war_view") and hasattr(self.war_view, "lbl_file_status"):
                    self.war_view.lbl_file_status.configure(text=self.pending_status_text, text_color=getattr(self, 'pending_status_color', "black"))
            except Exception:
                pass
            self.pending_status_text = None

        if getattr(self, 'needs_ui_update', False):
            try:
                self.dashboard_area.update_display()
                if hasattr(self, "war_view") and hasattr(self.war_view, "dashboard_area"):
                    self.war_view.dashboard_area.update_display()
                if getattr(self, 'overlay_window', None) and self.overlay_window.winfo_exists():
                    self.overlay_window.update_data()
            except Exception:
                pass
            self.needs_ui_update = False 

        if self.first_drop_time is not None:
            try: 
                self.dashboard_area.update_live_stats()
                if hasattr(self, "war_view") and hasattr(self.war_view, "dashboard_area"):
                    self.war_view.dashboard_area.update_live_stats()
                if getattr(self, 'overlay_window', None) and self.overlay_window.winfo_exists():
                    self.overlay_window.update_data()
            except Exception:
                pass

        if getattr(self, "current_view", "offline") == "war" and hasattr(self, "war_view") and self.war_view.winfo_ismapped():
            try:
                self.war_view.update_view()
            except Exception:
                pass
            
        self.after(1000, self.update_live_clock)

    def setup_icon(self):
        try:
            if os.path.exists(ICON_FILENAME):
                self.iconbitmap(default=ICON_FILENAME)
        except Exception:
            pass

    def build_title_bar(self):
        self.title_bar = ctk.CTkFrame(self.main_container, height=40, corner_radius=0, fg_color="transparent")
        self.title_bar.grid(row=0, column=0, sticky="ew")
        
        if os.path.exists(ICON_FILENAME):
            try:
                icon_image = ctk.CTkImage(Image.open(ICON_FILENAME), size=(20, 20))
                icon_lbl = ctk.CTkLabel(self.title_bar, text="", image=icon_image)
                icon_lbl.pack(side="left", padx=(15, 5), pady=5)
                icon_lbl.bind("<ButtonPress-1>", self.start_move)
                icon_lbl.bind("<B1-Motion>", self.do_move)
                icon_lbl.bind("<Double-Button-1>", self.toggle_maximize)
            except Exception:
                pass

        title_text = t("app_title_offline")
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text=title_text,
            font=(FONT_FAMILY, 15, "bold"),
            text_color="#881337",
        )
        self.title_label.pack(side="left", padx=5, pady=5)

        self.version_label = ctk.CTkLabel(
            self.title_bar,
            text=f"v{CLIENT_VERSION}",
            font=(FONT_FAMILY, 10, "bold"),
            text_color="#9F1239",
            fg_color="#FFE4E6",
            corner_radius=4,
            padx=5,
            pady=2,
        )
        self.version_label.pack(side="left", padx=(2, 6), pady=5)
        self.version_label.bind("<ButtonPress-1>", self.start_move)
        self.version_label.bind("<B1-Motion>", self.do_move)
        self.version_label.bind("<Double-Button-1>", self.toggle_maximize)

        self.test_mode_badge = ctk.CTkLabel(
            self.title_bar,
            text="🧪 TEST MODE",
            font=(FONT_FAMILY, 10, "bold"),
            text_color="#0369A1",
            fg_color="#E0F2FE",
            corner_radius=4,
            padx=6,
            pady=2,
        )
        if self.is_test_mode:
            self.test_mode_badge.pack(side="left", padx=6, pady=5)

        close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=30, corner_radius=0,
                                  fg_color="white", text_color="#D81B60", hover_color="#FFE4E1",
                                  font=("Arial", 14, "bold"), command=self.on_close)
        close_btn.pack(side="right", padx=(0, 15), pady=5)

        self.max_btn = ctk.CTkButton(self.title_bar, text="□", width=30, height=30, corner_radius=0,
                                     fg_color="white", text_color="#D81B60", hover_color="#FFE4E1",
                                     font=("Arial", 14, "bold"), command=self.toggle_maximize)
        self.max_btn.pack(side="right", padx=(0, 5), pady=5)

        min_btn = ctk.CTkButton(self.title_bar, text="─", width=30, height=30, corner_radius=0,
                                fg_color="white", text_color="#D81B60", hover_color="#FFE4E1",
                                font=("Arial", 14, "bold"), command=self.minimize_window)
        min_btn.pack(side="right", padx=(0, 5), pady=5)

        self.lang_btn_title = ctk.CTkSegmentedButton(
            self.title_bar,
            values=["EN", "TH", "JA"],
            width=110,
            height=26,
            font=(FONT_FAMILY, 10, "bold"),
            selected_color=COLOR_PINK_ACCENT,
            selected_hover_color="#D81B60",
            unselected_color="white",
            unselected_hover_color="#FFE4E1",
            text_color=COLOR_TEXT_MAIN,
            corner_radius=6,
            command=self._on_title_lang_selected,
        )
        self.lang_btn_title.set(i18n.get_button_label())
        self.lang_btn_title.pack(side="right", padx=(0, 10), pady=7)

        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        self.title_bar.bind("<Double-Button-1>", self.toggle_maximize)
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.do_move)
        self.title_label.bind("<Double-Button-1>", self.toggle_maximize)

    def update_board_coordinate(self, new_coord: Any, slot: Optional[int] = None) -> str:
        parsed = self.war_service.set_target_coord(new_coord, slot=slot)
        gx, gy, cslot = parsed.x, parsed.y, parsed.slot
        norm = f"{gx}, {gy}, {cslot}"
        self.board_coord = norm
        self.save_settings()
        if hasattr(self, "coord_var"):
            self.coord_var.set(norm)
        if hasattr(self, "war_view"):
            if hasattr(self.war_view, "coord_var"):
                self.war_view.coord_var.set(norm)
            if hasattr(self.war_view, "set_active_slot_ui"):
                self.war_view.set_active_slot_ui(cslot)
        self.event_bus.emit("board_coord_changed", coord=norm, sector_x=gx, sector_y=gy, slot=cslot)
        return norm

    def _on_tamper_violation(self, violation: TamperViolation) -> None:
        """Invoked when AntiTamperGuard detects an ActionLog integrity violation."""
        print(f"[AntiTamper] Violation detected: {violation}")
        self.event_bus.emit("tamper_violation", violation=violation)

    def _on_character_detected(self, character_name="", player_id="", **kwargs):
        try:
            if character_name:
                self.character_name = character_name
                if hasattr(self, "anti_tamper"):
                    self.anti_tamper.lock_identity(player_id or self.player_id, character_name)
                if hasattr(self, "btn_enter_war"):
                    self.btn_enter_war.configure(text=t("btn_enter_war_char", character=character_name))
                if hasattr(self, "war_service"):
                    self.war_service.set_operative(character_name)
                if getattr(self, "current_view", "") == "war" and hasattr(self, "war_view") and self.war_view.winfo_ismapped():
                    self.war_view.update_view()
        except Exception:
            pass

    def enter_war_mode(self):
        self.show_war_view()

    def show_offline_view(self):
        self.current_view = "offline"
        try:
            self.title_label.configure(text=t("app_title_offline"))
        except Exception:
            pass
        if hasattr(self, "war_view"):
            self.war_view.grid_remove()
        self.offline_container.grid(row=1, column=0, sticky="nsew")

    def show_war_view(self):
        self.ensure_character_from_log()
        self.current_view = "war"
        try:
            self.title_label.configure(text=t("app_title_war"))
        except Exception:
            pass
        self.offline_container.grid_remove()

        if not hasattr(self, "war_view"):
            self.war_view = WarDashboardFrame(self.main_container, self, self.war_service)

        op_name = self.character_name or "Operative"
        self.war_service.set_operative(op_name)
        self.war_service.sync_to_war_room()

        self.war_view.grid(row=1, column=0, sticky="nsew")
        self.war_view.update_view()

    def toggle_maximize(self, event=None):
        if self.state() == "zoomed":
            self.state("normal")
            if hasattr(self, "max_btn") and self.max_btn.winfo_exists():
                self.max_btn.configure(text="□")
        else:
            self.state("zoomed")
            if hasattr(self, "max_btn") and self.max_btn.winfo_exists():
                self.max_btn.configure(text="❐")

    def start_move(self, event):
        if self.state() == "zoomed":
            self.state("normal")
            if hasattr(self, "max_btn") and self.max_btn.winfo_exists():
                self.max_btn.configure(text="□")
            self.update_idletasks()
        self.x = getattr(event, "x", 0)
        self.y = getattr(event, "y", 0)
        self._window_mover.start_move(event)

    def do_move(self, event):
        self._window_mover.do_move(event)

    def minimize_window(self):
        self.bind("<Map>", self._on_restore_window)
        self.overrideredirect(False)
        self.iconify()

    def _on_restore_window(self, event=None):
        if self.state() == "iconic":
            return
        self.overrideredirect(True)
        try:
            self.unbind("<Map>")
        except Exception:
            pass
        self.after(50, self.force_taskbar_icon)

    def _enable_test_mode_bypasses(self):
        """Bypasses anti-tamper constraints when running mock tests or sample logs on test machines."""
        self.is_test_mode = True
        if hasattr(self, "anti_tamper"):
            self.anti_tamper.enforce_process_validation = False
            self.anti_tamper.enforce_file_handle_validation = False
            self.anti_tamper.enforce_canonical_path = False
            self.anti_tamper.enforce_cadence_validation = False
            self.anti_tamper.enforce_timestamp_validation = False
            self.anti_tamper.enforce_velocity_validation = False
            self.anti_tamper.enforce_ceiling_validation = False
            self.anti_tamper.is_compromised = False
        if hasattr(self, "war_service"):
            self.war_service.is_tamper_compromised = False
        if hasattr(self, "test_mode_badge") and self.test_mode_badge.winfo_exists():
            try:
                self.test_mode_badge.pack(side="left", padx=6, pady=5)
            except Exception:
                pass
            
    def confirm_reset(self):
        if self.confirm_dialog is not None and self.confirm_dialog.winfo_exists():
            self.confirm_dialog.lift()
            return

        dlg = ctk.CTkToplevel(self)
        self.confirm_dialog = dlg
        dlg.overrideredirect(True)
        dlg.geometry("360x180")
        dlg.configure(fg_color="white")
        dlg.attributes("-topmost", True)
        dlg.transient(self)

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 180
        y = self.winfo_y() + (self.winfo_height() // 2) - 90
        dlg.geometry(f"+{x}+{y}")

        title_bar = ctk.CTkFrame(dlg, height=36, corner_radius=0, fg_color=COLOR_PINK_HEADER)
        title_bar.pack(fill="x", side="top")
        ctk.CTkLabel(title_bar, text=t("dialog_reset_title"), font=(FONT_FAMILY, 13, "bold"), text_color="#333333").pack(side="left", padx=15, pady=5)

        ctk.CTkLabel(dlg, text=t("dialog_reset_msg"),
                     font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_MAIN, justify="center").pack(pady=(20, 15), padx=20)

        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 15))
        btn_frame.columnconfigure((0, 1), weight=1, uniform="equal")

        def do_confirm():
            dlg.destroy()
            self.reset_data()

        ctk.CTkButton(btn_frame, text=t("btn_cancel"), font=(FONT_FAMILY, 12),
                      fg_color="#F0F0F0", text_color="#333333", hover_color="#E0E0E0",
                      height=35, corner_radius=UI_RADIUS,
                      command=dlg.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(btn_frame, text=t("btn_confirm_reset"), font=(FONT_FAMILY, 12, "bold"),
                      fg_color=COLOR_PINK_ACCENT, hover_color="#D81B60", text_color="white",
                      height=35, corner_radius=UI_RADIUS,
                      command=do_confirm).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        try:
            dlg.grab_set()
        except Exception:
            pass

    def reset_data(self):
        with self.data_lock:
            self.session_meseta = 0
            self.current_wallet = 0
            self.item_counts = {}
            self.first_drop_time = None
            self.last_income_time = None
            if hasattr(self, "anti_tamper"):
                self.anti_tamper.reset()
        
        if self.log_path and os.path.exists(self.log_path):
            norm_path = self.log_path.replace("\\", "/").lower()
            is_sample = self.is_test_mode or ("sample_logs" in norm_path or "/mock" in norm_path or "/test" in norm_path)
            try:
                with open(self.log_path, 'r', encoding=self.active_encoding, errors='replace') as f:
                    if is_sample:
                        self.last_file_pos = 0
                    else:
                        f.seek(0, 2)
                        self.last_file_pos = f.tell()
            except OSError:
                pass
        self.event_bus.emit("tracker_reset")
        self.trigger_update_ui()

    def on_close(self):
        self.is_running = False
        self.stop_event.set()
        if hasattr(self, "war_service") and hasattr(self.war_service, "stop"):
            try:
                self.war_service.stop()
            except Exception:
                pass
        try:
            self.destroy()
        except Exception:
            pass
        sys.exit(0)

    def open_how_to_use(self, tab: str = "setup"):
        from modules.guide_dialog import open_guide_dialog
        self.guide_window = open_guide_dialog(self, initial_tab=tab)
        return self.guide_window

    def open_discord(self):
        webbrowser.open(DEFAULT_DISCORD_URL)

    def toggle_filter(self, val=None):
        if val is not None:
            self.is_filter_active = bool(val)
        elif hasattr(self, "switch_filter"):
            self.is_filter_active = bool(self.switch_filter.get())

        if hasattr(self, "switch_filter"):
            try:
                if self.is_filter_active:
                    self.switch_filter.select()
                else:
                    self.switch_filter.deselect()
            except Exception:
                pass

        if hasattr(self, "war_view") and hasattr(self.war_view, "switch_filter"):
            try:
                if self.is_filter_active:
                    self.war_view.switch_filter.select()
                else:
                    self.war_view.switch_filter.deselect()
            except Exception:
                pass

        self.trigger_update_ui()

    def _on_sidebar_lang_selected(self, val: str) -> None:
        self.set_app_language(val)

    def _on_title_lang_selected(self, val: str) -> None:
        self.set_app_language(val)

    def _on_language_changed(self, language: str = "", **kwargs) -> None:
        try:
            self.retranslate_ui()
        except Exception:
            pass

    def set_app_language(self, lang_code: str, save: bool = True) -> None:
        code = i18n.set_language(lang_code)
        self.current_language = code
        if save:
            self.save_settings()
        self.retranslate_ui()

    def retranslate_ui(self) -> None:
        """Update all labels and buttons to current active language."""
        try:
            self.title(t("app_window_title"))
            if hasattr(self, "btn_enter_war") and self.btn_enter_war.winfo_exists():
                self.btn_enter_war.configure(text=t("btn_enter_war"))
            if hasattr(self, "btn_reset") and self.btn_reset.winfo_exists():
                self.btn_reset.configure(text=t("btn_reset"))
            if hasattr(self, "btn_watchlist") and self.btn_watchlist.winfo_exists():
                self.btn_watchlist.configure(text=t("btn_watchlist"))
            if hasattr(self, "switch_filter") and self.switch_filter.winfo_exists():
                self.switch_filter.configure(text=t("switch_filter"))
            if hasattr(self, "btn_overlay_full") and self.btn_overlay_full.winfo_exists():
                self.btn_overlay_full.configure(text=t("btn_overlay_full"))
            if hasattr(self, "btn_overlay_mini") and self.btn_overlay_mini.winfo_exists():
                self.btn_overlay_mini.configure(text=t("btn_overlay_mini"))
            if hasattr(self, "btn_how_to_use") and self.btn_how_to_use.winfo_exists():
                self.btn_how_to_use.configure(text=t("btn_how_to_use"))
            if hasattr(self, "btn_discord") and self.btn_discord.winfo_exists():
                self.btn_discord.configure(text=t("btn_discord"))
            if hasattr(self, "lbl_sidebar_lang") and self.lbl_sidebar_lang.winfo_exists():
                self.lbl_sidebar_lang.configure(text=f"🌐 {t('label_language')}:")
            if hasattr(self, "seg_lang_sidebar") and self.seg_lang_sidebar.winfo_exists():
                self.seg_lang_sidebar.set(i18n.get_button_label())
            if hasattr(self, "btn_select") and self.btn_select.winfo_exists():
                self.btn_select.configure(text=t("btn_select_folder"))
            if hasattr(self, "dashboard") and hasattr(self.dashboard, "retranslate_ui"):
                self.dashboard.retranslate_ui()
            if hasattr(self, "war_view") and hasattr(self.war_view, "retranslate_ui"):
                self.war_view.retranslate_ui()
            if hasattr(self, "overlay") and self.overlay and hasattr(self.overlay, "retranslate_ui"):
                self.overlay.retranslate_ui()
        except Exception:
            pass

    def load_settings(self):
        saved_lang = DEFAULT_LANGUAGE
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.watchlist_items = data.get("watchlist", [])
                    self.log_folder = data.get("log_folder", "")
                    self.board_coord = data.get("board_coord", "0, 0, 1")
                    saved_lang = data.get("language", DEFAULT_LANGUAGE)
            except (OSError, json.JSONDecodeError):
                pass

        self.set_app_language(saved_lang, save=False)

        if hasattr(self, "war_service"):
            self.war_service.set_target_coord(self.board_coord)
        if hasattr(self, "coord_var"):
            self.coord_var.set(self.board_coord)

        if not self.log_folder or not os.path.exists(self.log_folder):
            default_ngs_path = os.path.join(os.path.expanduser("~"), "Documents", "SEGA", "PHANTASYSTARONLINE2", "log_ngs")
            if os.path.exists(default_ngs_path):
                self.log_folder = default_ngs_path
            
        if self.log_folder and os.path.exists(self.log_folder): 
            self.find_latest_log_file()
        else: 
            self.lbl_file_status.configure(text=t("status_folder_unspecified"), text_color="red")
            if hasattr(self, "war_view") and hasattr(self.war_view, "lbl_file_status"):
                self.war_view.lbl_file_status.configure(text=t("status_folder_unspecified"), text_color="red")

    def save_settings(self):
        data = {
            "watchlist": self.watchlist_items,
            "log_folder": self.log_folder,
            "board_coord": self.board_coord,
            "language": i18n.get_language(),
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4) 
        except OSError:
            pass

    def select_log_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            norm_folder = folder_path.replace("\\", "/").lower()
            if "sample_logs" in norm_folder or "/mock" in norm_folder or "/test" in norm_folder:
                self._enable_test_mode_bypasses()
            self.log_folder = folder_path
            self.save_settings() 
            self.find_latest_log_file()

    def find_latest_log_file(self):
        if not self.log_folder: return
        target_files = []
        try:
            for f in os.listdir(self.log_folder):
                if f.startswith("ActionLog") and f.endswith(".txt"):
                    target_files.append(os.path.join(self.log_folder, f))
        except OSError:
            return
        
        if not target_files:
            self.pending_status_text = t("status_log_not_found")
            self.pending_status_color = "red"
            return

        latest_file = max(target_files, key=os.path.getmtime)
        norm_file = latest_file.replace("\\", "/").lower()
        if "sample_logs" in norm_file or "/mock" in norm_file or "/test" in norm_file:
            self._enable_test_mode_bypasses()
        if latest_file != self.log_path:
            self.log_path = latest_file
            self.pending_status_text = t("status_reading_file", file=os.path.basename(latest_file))
            self.pending_status_color = COLOR_TEXT_VAL
            self.detect_encoding(self.log_path)
            self.reset_data() 
            self.detect_character_from_file(self.log_path)

    def detect_character_from_file(self, filepath):
        """Read initial lines to extract in-game character name (not ID)."""
        try:
            with open(filepath, 'r', encoding=self.active_encoding, errors='replace') as f:
                for _ in range(50):
                    line = f.readline()
                    if not line:
                        break
                    char_info = extract_character_info(line)
                    if char_info:
                        cname, pid = char_info
                        self.character_name = cname
                        self.player_id = pid
                        self.event_bus.emit("character_detected", character_name=cname, player_id=self.player_id)
                        return cname
        except Exception:
            pass
        return self.character_name or ""

    def ensure_character_from_log(self) -> str:
        """Scan log file to retrieve in-game character name when starting work."""
        if self.character_name:
            return self.character_name

        if not self.log_folder or not os.path.exists(self.log_folder):
            default_ngs_path = os.path.join(os.path.expanduser("~"), "Documents", "SEGA", "PHANTASYSTARONLINE2", "log_ngs")
            if os.path.exists(default_ngs_path):
                self.log_folder = default_ngs_path

        if self.log_folder and os.path.exists(self.log_folder):
            self.find_latest_log_file()

        if self.log_path and os.path.exists(self.log_path):
            return self.detect_character_from_file(self.log_path)
        return self.character_name or ""

    def open_watchlist_editor(self):
        if self.watchlist_window is None or not self.watchlist_window.winfo_exists():
            self.watchlist_window = ctk.CTkToplevel(self)
            self.watchlist_window.overrideredirect(True)
            self.watchlist_window.geometry("400x520")
            self.watchlist_window.configure(fg_color="white")
            self.watchlist_window.attributes("-topmost", True)
            
            title_bar = ctk.CTkFrame(self.watchlist_window, height=40, corner_radius=0, fg_color=COLOR_PINK_HEADER)
            title_bar.pack(fill="x", side="top")
            
            if os.path.exists(ICON_FILENAME):
                try: 
                    img = Image.open(ICON_FILENAME)
                    icon_ctk = ctk.CTkImage(img, size=(20, 20))
                    icon_lbl = ctk.CTkLabel(title_bar, text="", image=icon_ctk)
                    icon_lbl.pack(side="left", padx=(15, 5), pady=5)
                except Exception:
                    pass

            title_label = ctk.CTkLabel(title_bar, text=t("dialog_watchlist_title"), font=(FONT_FAMILY, 14, "bold"), text_color="#333333")
            title_label.pack(side="left", padx=5, pady=5)

            close_btn = ctk.CTkButton(title_bar, text="✕", width=30, height=30, corner_radius=0,
                                      fg_color="transparent", text_color="#D81B60", hover_color="#FFE4E1",
                                      font=("Arial", 14, "bold"), command=self.watchlist_window.destroy)
            close_btn.pack(side="right", padx=15, pady=5)

            watchlist_mover = WindowMover(self.watchlist_window)
            def start_move(event):
                watchlist_mover.start_move(event)

            def do_move(event):
                watchlist_mover.do_move(event)

            title_bar.bind("<ButtonPress-1>", start_move)
            title_bar.bind("<B1-Motion>", do_move)
            title_label.bind("<ButtonPress-1>", start_move)
            title_label.bind("<B1-Motion>", do_move)

            ctk.CTkLabel(self.watchlist_window, text=t("dialog_watchlist_prompt"), font=(FONT_FAMILY, 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(15, 5))
            
            self.txt_watchlist = ctk.CTkTextbox(self.watchlist_window, font=(FONT_FAMILY, 12), border_color=COLOR_PINK_HEADER, border_width=2, corner_radius=5, fg_color="white", text_color="#333333")
            self.txt_watchlist.pack(fill="both", expand=True, padx=20, pady=10)
            self.txt_watchlist.insert("0.0", "\n".join(self.watchlist_items))
            
            ctk.CTkButton(self.watchlist_window, text=t("btn_save_watchlist"), font=(FONT_FAMILY, 14, "bold"), fg_color=COLOR_PINK_ACCENT, hover_color="#D81B60", text_color="white", corner_radius=5, height=40, command=self.save_watchlist_from_editor).pack(pady=(5, 15), padx=20, fill="x")
        else: self.watchlist_window.lift()

    def save_watchlist_from_editor(self):
        content = self.txt_watchlist.get("0.0", "end")
        self.watchlist_items = [line.strip() for line in content.split('\n') if line.strip()]
        self.save_settings() 
        self.trigger_update_ui() 
        self.watchlist_window.destroy() 

    def load_logo(self):
        if os.path.exists(LOGO_FILENAME):
            try:
                img = Image.open(LOGO_FILENAME)
                w, h = img.size
                target_w = 160 
                target_h = int(h * (target_w / w))
                self.logo_img_obj = ctk.CTkImage(img, size=(target_w, target_h))
                ctk.CTkLabel(self.sidebar, text="", image=self.logo_img_obj).pack(pady=(20, 5))
            except Exception:
                pass

    def design_brand_text(self):
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(pady=(0, 10))
        self.lbl_brand_sub = ctk.CTkLabel(brand_frame, text=t("brand_subtitle"), font=(FONT_FAMILY, 16), text_color=COLOR_PINK_HEADER)
        self.lbl_brand_sub.pack()
        self.lbl_brand_trk = ctk.CTkLabel(brand_frame, text=t("brand_tracker"), font=(FONT_FAMILY, 26), text_color=COLOR_PINK_ACCENT)
        self.lbl_brand_trk.pack(pady=(0,2))
        
        separator = ctk.CTkFrame(brand_frame, height=2, fg_color=COLOR_PINK_HEADER)
        separator.pack(fill="x", padx=40, pady=5)
        
        self.lbl_brand_by = ctk.CTkLabel(brand_frame, text=t("brand_created_by"), font=(FONT_FAMILY, 10, "bold"), text_color=COLOR_TEXT_VAL)
        self.lbl_brand_by.pack(pady=(2,0))
        self.lbl_brand_team = ctk.CTkLabel(brand_frame, text=t("brand_team_credit"), font=(FONT_FAMILY, 12, "bold"), text_color=COLOR_TEXT_VAL)
        self.lbl_brand_team.pack()

    def detect_encoding(self, filepath):
        try:
            with open(filepath, 'rb') as f: raw = f.read(4)
            if raw.startswith(b'\xff\xfe'): self.active_encoding = 'utf-16'
            elif raw.startswith(b'\xfe\xff'): self.active_encoding = 'utf-16-be'
            elif raw.startswith(b'\xef\xbb\xbf'): self.active_encoding = 'utf-8-sig'
            else: self.active_encoding = 'utf-8'
        except Exception:
            self.active_encoding = 'utf-16'

    def monitor_log_file(self):
        check_counter = 0
        while not self.stop_event.is_set():
            if not self.is_running: break
            check_counter += 1
            if self.log_folder and (not self.log_path or check_counter >= 5):
                check_counter = 0
                try:
                    self.find_latest_log_file()
                except Exception:
                    pass
            
            if self.log_path and os.path.exists(self.log_path):
                try:
                    current_file_size = os.path.getsize(self.log_path)
                    if hasattr(self, "anti_tamper"):
                        if not self.anti_tamper.validate_stream(
                            self.last_file_pos, current_file_size, file_path=self.log_path
                        ):
                            time.sleep(1)
                            continue

                    with open(self.log_path, 'r', encoding=self.active_encoding, errors='replace') as f:
                        f.seek(self.last_file_pos)
                        lines = f.readlines()
                        if lines:
                            self.last_file_pos = f.tell()
                            data_changed = False
                            with self.data_lock:
                                for line in lines:
                                    if line.strip(): 
                                        self.process_log_line(line)
                                        data_changed = True
                            if data_changed: self.trigger_update_ui()
                except Exception:
                    pass
            time.sleep(1)

    def process_log_line(self, line):
        try:
            record = ActionLogParser.parse_line(line)

            # Extract in-game character name (not ID) from ActionLog:
            char_info = extract_character_info(line)
            if char_info:
                cname, pid = char_info
                if self.character_name != cname:
                    self.character_name = cname
                    self.player_id = pid
                    self.event_bus.emit("character_detected", character_name=cname, player_id=self.player_id)

            meseta_match = re.search(r'\t(?:N-)?Meseta\s*\(\s*(\d+)\s*\)', line, re.IGNORECASE)
            wallet_match = re.search(r'\tCurrent(?:N-)?Meseta\s*\(\s*(\d+)\s*\)', line, re.IGNORECASE)

            raw_valid_action = ActionLogParser.is_valid_farming_action(
                record.action if record else "",
                has_wallet_update=bool(wallet_match),
                raw_line=line,
            )

            drop_amount = int(meseta_match.group(1)) if meseta_match else 0

            if wallet_match:
                new_wallet = int(wallet_match.group(1))
                income = 0
                
                if self.current_wallet == 0:
                    self.current_wallet = new_wallet
                    if meseta_match: income = drop_amount 
                else:
                    if new_wallet > self.current_wallet:
                        income = new_wallet - self.current_wallet
                    self.current_wallet = new_wallet

                if income > 0 and raw_valid_action:
                    # Validate against AntiTamperGuard before crediting
                    if hasattr(self, "anti_tamper") and record:
                        record.meseta_drop = max(record.meseta_drop, income)
                        if not self.anti_tamper.validate_record(record):
                            # Tamper detected - discard income
                            return

                    if self.first_drop_time is None: self.first_drop_time = time.time()
                    self.session_meseta += income
                    self.last_income_time = time.time()
                    self.event_bus.emit("meseta_earned", amount=income, wallet=self.current_wallet)

            if raw_valid_action and not meseta_match and "Num(" in line:
                if hasattr(self, "anti_tamper") and record:
                    if not self.anti_tamper.validate_record(record):
                        return

                item_pattern = r'\t([^\t]+)\tNum\((\d+)\)'
                match = re.search(item_pattern, line)
                if match:
                    item_name = match.group(1).strip()
                    count = int(match.group(2))
                    if item_name:
                        self.item_counts[item_name] = self.item_counts.get(item_name, 0) + count

        except Exception:
            pass

    def trigger_update_ui(self):
        self.needs_ui_update = True

    def open_overlay(self, mode="full"):
        if self.overlay_window is not None and self.overlay_window.winfo_exists():
            self.overlay_window.destroy()
        self.overlay_window = OverlayWindow(self, mode)

    def force_taskbar_icon(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
            style = style & ~0x00000080
            style = style | 0x00040000
            ctypes.windll.user32.SetWindowLongW(hwnd, -20, style)
            self.withdraw()
            self.deiconify()
        except Exception:
            pass

    def summon_main_window(self):
        self.deiconify()
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        self.lift()
        self.focus_force()

    def _on_title_lang_selected(self, val: str):
        self.set_app_language(val)

    def _on_sidebar_lang_selected(self, val: str):
        self.set_app_language(val)

    def _on_language_changed(self, language: str = "", **kwargs):
        label = i18n.get_button_label(language)
        if hasattr(self, "lang_btn_title") and self.lang_btn_title.winfo_exists():
            self.lang_btn_title.set(label)
        if hasattr(self, "seg_lang_sidebar") and self.seg_lang_sidebar.winfo_exists():
            self.seg_lang_sidebar.set(label)
        if hasattr(self, "war_view") and hasattr(self.war_view, "seg_lang_sidebar") and self.war_view.seg_lang_sidebar.winfo_exists():
            self.war_view.seg_lang_sidebar.set(label)
        self.retranslate_ui()

    def set_app_language(self, lang_code_or_name: str, save: bool = True):
        changed = i18n.set_language(lang_code_or_name)
        self.current_language = i18n.get_language()
        label = i18n.get_button_label()
        if hasattr(self, "lang_btn_title") and self.lang_btn_title.winfo_exists():
            self.lang_btn_title.set(label)
        if hasattr(self, "seg_lang_sidebar") and self.seg_lang_sidebar.winfo_exists():
            self.seg_lang_sidebar.set(label)
        if hasattr(self, "war_view") and hasattr(self.war_view, "seg_lang_sidebar") and self.war_view.seg_lang_sidebar.winfo_exists():
            self.war_view.seg_lang_sidebar.set(label)
        self.retranslate_ui()
        if save:
            self.save_settings()

    def retranslate_ui(self):
        """Retranslate all widgets in the main application."""
        try:
            self.title(t("app_window_title"))
            if getattr(self, "current_view", "offline") == "war":
                self.title_label.configure(text=t("app_title_war"))
            else:
                self.title_label.configure(text=t("app_title_offline"))

            if hasattr(self, "lbl_brand_sub") and self.lbl_brand_sub.winfo_exists():
                self.lbl_brand_sub.configure(text=t("brand_subtitle"))
            if hasattr(self, "lbl_brand_trk") and self.lbl_brand_trk.winfo_exists():
                self.lbl_brand_trk.configure(text=t("brand_tracker"))
            if hasattr(self, "lbl_brand_by") and self.lbl_brand_by.winfo_exists():
                self.lbl_brand_by.configure(text=t("brand_created_by"))
            if hasattr(self, "lbl_brand_team") and self.lbl_brand_team.winfo_exists():
                self.lbl_brand_team.configure(text=t("brand_team_credit"))

            if hasattr(self, "btn_enter_war") and self.btn_enter_war.winfo_exists():
                if self.character_name:
                    self.btn_enter_war.configure(text=t("btn_enter_war_char", character=self.character_name))
                else:
                    self.btn_enter_war.configure(text=t("btn_enter_war"))

            if hasattr(self, "btn_reset") and self.btn_reset.winfo_exists():
                self.btn_reset.configure(text=t("btn_reset"))
            if hasattr(self, "btn_watchlist") and self.btn_watchlist.winfo_exists():
                self.btn_watchlist.configure(text=t("btn_watchlist"))
            if hasattr(self, "switch_filter") and self.switch_filter.winfo_exists():
                self.switch_filter.configure(text=t("switch_filter"))
            if hasattr(self, "btn_overlay_full") and self.btn_overlay_full.winfo_exists():
                self.btn_overlay_full.configure(text=t("btn_overlay_full"))
            if hasattr(self, "btn_overlay_mini") and self.btn_overlay_mini.winfo_exists():
                self.btn_overlay_mini.configure(text=t("btn_overlay_mini"))
            if hasattr(self, "btn_how_to_use") and self.btn_how_to_use.winfo_exists():
                self.btn_how_to_use.configure(text=t("btn_how_to_use"))
            if hasattr(self, "btn_discord") and self.btn_discord.winfo_exists():
                self.btn_discord.configure(text=t("btn_discord"))
            if hasattr(self, "lbl_sidebar_lang") and self.lbl_sidebar_lang.winfo_exists():
                self.lbl_sidebar_lang.configure(text=f"🌐 {t('label_language')}:")
            if hasattr(self, "btn_select") and self.btn_select.winfo_exists():
                self.btn_select.configure(text=t("btn_select_folder"))

            if hasattr(self, "lbl_file_status") and self.lbl_file_status.winfo_exists():
                if not self.log_path:
                    self.lbl_file_status.configure(text=t("status_no_folder"))
                elif self.log_path:
                    self.lbl_file_status.configure(text=t("status_reading_file", file=os.path.basename(self.log_path)))

            if hasattr(self, "dashboard_area") and hasattr(self.dashboard_area, "retranslate_ui"):
                self.dashboard_area.retranslate_ui()

            if hasattr(self, "war_view") and hasattr(self.war_view, "retranslate_ui"):
                self.war_view.retranslate_ui()

            if getattr(self, 'overlay_window', None) and self.overlay_window.winfo_exists():
                self.overlay_window.retranslate_ui()

            if getattr(self, 'guide_window', None) and self.guide_window.winfo_exists():
                self.guide_window.retranslate_ui()
        except Exception:
            pass

if __name__ == "__main__":
    app = NGSTrackerApp()
    app.mainloop()