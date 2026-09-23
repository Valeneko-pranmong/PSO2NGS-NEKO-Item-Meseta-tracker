from __future__ import annotations

import logging
import os
import sys
import time
import queue
import threading
import webbrowser
import tkinter as tk
from typing import Any, Dict, List, Optional, Tuple
import customtkinter as ctk

logger = logging.getLogger("NekoTracker.war_view")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config import (
    COLOR_BG_MAIN,
    COLOR_PINK_HEADER,
    COLOR_PINK_ACCENT,
    COLOR_PINK_SOFT,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_SUB,
    COLOR_TEXT_VAL,
    COLOR_WATCHLIST,
    COLOR_DISCORD,
    UI_RADIUS,
    FONT_FAMILY,
    FONT_HEADER,
    FONT_SUBHEADER,
    FONT_NORMAL,
    FONT_NUMBER,
    FONT_STATS,
    APP_VERSION,
    DEFAULT_WAR_ROOM_URL,
    resource_path,
)
from PIL import Image
from dashboard_ui import DashboardFrame
from modules.i18n import i18n, t, tr

try:
    from .war_service import WarService, TEAMS_DATA
except (ImportError, ValueError):
    from modules.war_mode.war_service import WarService, TEAMS_DATA


class WarDashboardFrame(ctk.CTkFrame):
    """
    Campaign Telemetry & War Farming Dashboard for ARKS War Room.
    Displays live session contribution, character primary key from log,
    user-entered board coordinates, and Firebase Realtime sync status.
    """

    def __init__(
        self,
        parent: Any,
        controller: Any,
        war_service: WarService,
        auth_service: Optional[Any] = None,
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.controller = controller
        self.war_service = war_service
        self.auth_service = auth_service
        self.lbl_war_status = None
        self.btn_sync = None
        self._ui_sync_queue = queue.Queue()
        self._sync_pending_after_id = None
        self._sync_started_time = 0.0
        self._is_sync_animating = False
        self._last_display_contrib = 0

        self._build_ui()
        self._subscribe_events()
        self._poll_ui_sync_queue()

    def _subscribe_events(self) -> None:
        try:
            from modules.event_bus import event_bus
            event_bus.subscribe("realtime_sync_started", self._on_realtime_sync_started)
            event_bus.subscribe("realtime_sync_completed", self._on_realtime_sync_completed)
            event_bus.subscribe("board_coord_changed", self._on_board_coord_changed)
            event_bus.subscribe("language_changed", self._on_language_changed)
        except Exception as exc:
            logger.debug("_subscribe_events: failed to subscribe events: %s", exc)

    def _apply_sync_started(self) -> None:
        if not hasattr(self, "lbl_sync_time") or not self.lbl_sync_time.winfo_exists():
            return
        if getattr(self, "_sync_pending_after_id", None):
            try:
                self.after_cancel(self._sync_pending_after_id)
            except Exception as exc:
                logger.debug("_apply_sync_started: failed to cancel pending after: %s", exc)
            self._sync_pending_after_id = None
        self._sync_started_time = time.time()
        self._is_sync_animating = True
        self.lbl_sync_time.configure(text=t("war_syncing"), text_color="#0284C7")

    def _apply_sync_completed(self, success: bool = True, message: str = "", timestamp: float = 0, contribution: int = 0, **kwargs) -> None:
        if not hasattr(self, "lbl_sync_time") or not self.lbl_sync_time.winfo_exists():
            return
        self._sync_pending_after_id = None
        self._is_sync_animating = False
        t_val = timestamp or time.time()
        t_str = time.strftime("%H:%M:%S", time.localtime(t_val))
        if success:
            active_val = max(getattr(self.war_service, "total_farmed", 0), getattr(self.war_service, "session_contribution", 0))
            contrib = contribution if contribution > 0 else active_val
            self._last_display_contrib = contrib
            new_text = t("war_synced", time=t_str, contrib=f"{contrib:,}")
            new_color = "#10B981"
        else:
            new_text = message if message else t("war_sync_waiting")
            new_color = "#EF4444"

        if self.lbl_sync_time.cget("text") != new_text or self.lbl_sync_time.cget("text_color") != new_color:
            self.lbl_sync_time.configure(
                text=new_text,
                text_color=new_color,
            )

    def _process_ui_sync_queue(self) -> None:
        if not hasattr(self, "_ui_sync_queue"):
            return
        while not self._ui_sync_queue.empty():
            try:
                item = self._ui_sync_queue.get_nowait()
                action, data = item
                if action == "started":
                    self._apply_sync_started()
                elif action == "completed":
                    self._apply_sync_completed(**data)
            except queue.Empty:
                break
            except Exception as exc:
                logger.debug("_process_ui_sync_queue: failed to process queue item: %s", exc)

    def _poll_ui_sync_queue(self) -> None:
        try:
            self._process_ui_sync_queue()
        except Exception as exc:
            logger.debug("_poll_ui_sync_queue: failed to process queue: %s", exc)
        try:
            if hasattr(self, "lbl_sync_time") and self.lbl_sync_time.winfo_exists():
                self.after(100, self._poll_ui_sync_queue)
        except Exception as exc:
            logger.debug("_poll_ui_sync_queue: failed to schedule next poll: %s", exc)

    def _on_realtime_sync_started(self, **kwargs) -> None:
        try:
            if threading.current_thread() is threading.main_thread():
                self._apply_sync_started()
            else:
                self._ui_sync_queue.put(("started", kwargs))
        except Exception as exc:
            logger.debug("_on_realtime_sync_started: failed to enqueue sync start: %s", exc)

    def _on_realtime_sync_completed(self, success: bool = True, message: str = "", timestamp: float = 0, contribution: int = 0, **kwargs) -> None:
        payload = {
            "success": success,
            "message": message,
            "timestamp": timestamp,
            "contribution": contribution,
        }
        try:
            if threading.current_thread() is threading.main_thread():
                self._apply_sync_completed(**payload)
            else:
                self._ui_sync_queue.put(("completed", payload))
        except Exception as exc:
            logger.debug("_on_realtime_sync_completed: failed to enqueue sync completion: %s", exc)

    def _on_board_coord_changed(self, coord: str = "", **kwargs) -> None:
        try:
            if coord and hasattr(self, "coord_var"):
                self.coord_var.set(coord)
        except Exception as exc:
            logger.debug("_on_board_coord_changed: failed to update coord_var: %s", exc)

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Top War Room Banner: Operative Info (Primary Key) + Board Coordinate Entry + Sync Status
        self.top_banner = ctk.CTkFrame(self, fg_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS, height=72)
        self.top_banner.grid(row=0, column=0, sticky="ew", padx=15, pady=(8, 6))
        self.top_banner.pack_propagate(False)

        # Top Row: Operative Info (Left) + Cloud Sync Status (Right)
        top_status_row = ctk.CTkFrame(self.top_banner, fg_color="transparent")
        top_status_row.pack(fill="x", padx=14, pady=(5, 2))

        self.lbl_op_title = ctk.CTkLabel(
            top_status_row,
            text=t("war_op_title", name="-"),
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_op_title.pack(side="left")
        self.lbl_op_name = self.lbl_op_title

        self.lbl_op_sub = ctk.CTkLabel(
            top_status_row,
            text=f"• {t('war_op_sub')}",
            font=(FONT_FAMILY, 10),
            text_color="#64748B",
        )
        self.lbl_op_sub.pack(side="left", padx=(8, 0))

        self.lbl_sync_time = ctk.CTkLabel(
            top_status_row,
            text=t("war_sync_ready"),
            font=(FONT_FAMILY, 10, "bold"),
            text_color=COLOR_TEXT_SUB,
            width=280,
            anchor="e",
        )
        self.lbl_sync_time.pack(side="right")

        # Bottom Row: Board Coordinate Input Toolbar
        self.coord_frame = ctk.CTkFrame(self.top_banner, fg_color="transparent")
        self.coord_frame.pack(fill="x", padx=14, pady=(0, 5))

        self.lbl_coord_title = ctk.CTkLabel(
            self.coord_frame,
            text=t("war_coord_label"),
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_coord_title.pack(side="left", padx=(0, 4))

        init_coord = "0, 0, 1"
        if hasattr(self.war_service, "target_coord"):
            tc = self.war_service.target_coord
            gx = getattr(tc, "x", tc[0])
            gy = getattr(tc, "y", tc[1])
            cslot = getattr(tc, "slot", tc[2] if len(tc) >= 3 else 1)
            init_coord = f"{gx}, {gy}, {cslot}"
        elif hasattr(self.controller, "board_coord"):
            init_coord = str(self.controller.board_coord)

        self.coord_var = tk.StringVar(value=init_coord)
        self.entry_coord = ctk.CTkEntry(
            self.coord_frame,
            textvariable=self.coord_var,
            width=88,
            height=28,
            font=(FONT_FAMILY, 11, "bold"),
            justify="center",
            fg_color="white",
            text_color="#1E293B",
            border_color="#D81B60",
            border_width=2,
            corner_radius=6,
        )
        self.entry_coord.pack(side="left", padx=(0, 4))
        self.entry_coord.bind("<Return>", lambda e: self._on_coord_submit())

        # 4 Quadrant Slot Buttons (NW: 1, NE: 2, SW: 3, SE: 4)
        self.slot_buttons: Dict[int, ctk.CTkButton] = {}
        slot_names = {1: "NW", 2: "NE", 3: "SW", 4: "SE"}
        for s_idx in (1, 2, 3, 4):
            btn_s = ctk.CTkButton(
                self.coord_frame,
                text=f"#{s_idx} {slot_names[s_idx]}",
                width=44,
                height=28,
                font=(FONT_FAMILY, 9, "bold"),
                fg_color="#E2E8F0",
                hover_color="#CBD5E1",
                text_color="#475569",
                corner_radius=6,
                command=lambda s=s_idx: self._on_slot_button_clicked(s),
            )
            btn_s.pack(side="left", padx=(0, 2))
            self.slot_buttons[s_idx] = btn_s

        # Preset Landmarks Dropdown
        landmark_options = i18n.get_landmarks()
        self.opt_landmark = ctk.CTkOptionMenu(
            self.coord_frame,
            values=landmark_options,
            width=100,
            height=28,
            font=(FONT_FAMILY, 10, "bold"),
            dropdown_font=(FONT_FAMILY, 10),
            fg_color="#F1F5F9",
            text_color="#334155",
            button_color="#E2E8F0",
            button_hover_color="#CBD5E1",
            corner_radius=6,
            command=self._on_landmark_selected,
        )
        self.opt_landmark.pack(side="left", padx=(0, 4))

        self.btn_paste_coord = ctk.CTkButton(
            self.coord_frame,
            text=t("war_paste_btn"),
            width=48,
            height=28,
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white",
            corner_radius=6,
            command=self._on_paste_coord_clicked,
        )
        self.btn_paste_coord.pack(side="left", padx=(0, 4))

        self.btn_save_coord = ctk.CTkButton(
            self.coord_frame,
            text=t("war_save_btn"),
            width=54,
            height=28,
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#D81B60",
            hover_color="#BE185D",
            text_color="white",
            corner_radius=6,
            command=self._on_coord_submit,
        )
        self.btn_save_coord.pack(side="left")

        self._setup_coord_entry_support()
        if hasattr(self.war_service, "target_coord"):
            self.set_active_slot_ui(getattr(self.war_service.target_coord, "slot", 1))

        # 2. Main Content Grid (Left: Sidebar Menu, Right: Full Tracker Dashboard)
        self.main_split = ctk.CTkFrame(self, fg_color="transparent")
        self.main_split.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 6))
        self.main_split.columnconfigure(0, weight=0)  # Left Column: Sidebar Menu
        self.main_split.columnconfigure(1, weight=1)  # Right Column: Tracker Dashboard
        self.main_split.rowconfigure(0, weight=1)

        # Left Column: Tracker Control Menu (Sidebar layout)
        self.card_menu = ctk.CTkFrame(
            self.main_split,
            width=270,
            fg_color="white",
            corner_radius=UI_RADIUS,
            border_width=2,
            border_color=COLOR_PINK_HEADER,
        )
        self.card_menu.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self._build_menu_panel(self.card_menu)

        # Right Column: Complete Dashboard (Session Meseta, Wallet, Time, Speed, Item Drops List)
        self.dashboard_area = DashboardFrame(self.main_split, self.controller)
        self.dashboard_area.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        # 3. Bottom Command Button Bar
        btn_bar = ctk.CTkFrame(self, fg_color="white", corner_radius=UI_RADIUS, height=46)
        btn_bar.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 8))
        btn_bar.pack_propagate(False)

        # Left Action: Open Web ARKS War Room
        self.btn_open_web = ctk.CTkButton(
            btn_bar,
            text=t("war_btn_open_web"),
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="white",
            height=32,
            corner_radius=UI_RADIUS,
            command=self._open_web_war_room,
        )
        self.btn_open_web.pack(side="left", padx=(10, 6), pady=7)

        # Right Action: Back to Main Offline View (No login / logout needed!)
        self.btn_back_offline = ctk.CTkButton(
            btn_bar,
            text=t("war_btn_back_offline"),
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLOR_PINK_HEADER,
            hover_color=COLOR_PINK_SOFT,
            text_color=COLOR_TEXT_MAIN,
            height=32,
            corner_radius=UI_RADIUS,
            command=self.controller.show_offline_view,
        )
        self.btn_back_offline.pack(side="right", padx=(0, 10), pady=7)

    def set_active_slot_ui(self, active_slot: int) -> None:
        slot_colors = {
            1: ("#2563EB", "#1D4ED8"),  # NW Blue
            2: ("#059669", "#047857"),  # NE Green
            3: ("#D97706", "#B45309"),  # SW Amber
            4: ("#7C3AED", "#6D28D9"),  # SE Purple
        }
        for slot_num, btn in getattr(self, "slot_buttons", {}).items():
            try:
                if slot_num == active_slot:
                    fg, hov = slot_colors.get(slot_num, ("#D81B60", "#BE185D"))
                    btn.configure(fg_color=fg, hover_color=hov, text_color="white")
                else:
                    btn.configure(fg_color="#E2E8F0", hover_color="#CBD5E1", text_color="#475569")
            except Exception as exc:
                logger.debug("set_active_slot_ui: failed to update slot button: %s", exc)

    def _on_slot_button_clicked(self, slot: int) -> None:
        val = self.coord_var.get().strip()
        if hasattr(self.war_service, "parse_coordinate"):
            parsed = self.war_service.parse_coordinate(val, default_slot=slot)
            new_val = f"{parsed.x}, {parsed.y}, {slot}"
        else:
            new_val = f"{val}, {slot}"
        self.coord_var.set(new_val)
        self._on_coord_submit()

    def _on_landmark_selected(self, choice: str) -> None:
        landmarks_map = {
            "Core": (0, 0),
            "NGS": (3, 3),
            "Earth": (9, -3),
            "地球": (9, -3),
            "Sun": (8, -3),
            "太陽": (8, -3),
            "Mars": (9, -4),
            "火星": (9, -4),
            "Naberius": (-2, -2),
            "ナベリウス": (-2, -2),
            "Amduskia": (-3, -3),
            "アムドゥスキア": (-3, -3),
            "Lillipa": (-1, -3),
            "リリーパ": (-1, -3),
            "Hail Mary": (20, 7),
            "ヘイルメアリー": (20, 7),
        }
        for key, (lx, ly) in landmarks_map.items():
            if key in choice:
                current_slot = getattr(self.war_service.target_coord, "slot", 1)
                self.coord_var.set(f"{lx}, {ly}, {current_slot}")
                self._on_coord_submit()
                break
        if hasattr(self, "opt_landmark"):
            self.opt_landmark.set(i18n.get_landmarks()[0])

    def _on_coord_submit(self) -> None:
        val = self.coord_var.get().strip()
        if hasattr(self.controller, "update_board_coordinate"):
            norm = self.controller.update_board_coordinate(val)
            self.coord_var.set(norm)
        elif hasattr(self.war_service, "set_target_coord"):
            parsed = self.war_service.set_target_coord(val)
            self.coord_var.set(f"{parsed.x}, {parsed.y}, {parsed.slot}")
        if hasattr(self.war_service, "target_coord"):
            self.set_active_slot_ui(getattr(self.war_service.target_coord, "slot", 1))

    def _on_paste_coord_clicked(self) -> None:
        """Paste coordinate from clipboard directly, auto-parse format, and submit."""
        try:
            clip_text = self.clipboard_get()
        except Exception:
            clip_text = ""
        if not clip_text:
            return
        if hasattr(self.war_service, "parse_coordinate"):
            parsed = self.war_service.parse_coordinate(clip_text)
            norm = f"{parsed.x}, {parsed.y}, {parsed.slot}"
        else:
            norm = clip_text.strip()
        self.coord_var.set(norm)
        self._on_coord_submit()
        try:
            if hasattr(self, "btn_paste_coord"):
                self.btn_paste_coord.configure(text=t("war_pasted_btn"), fg_color="#059669")
                self.after(1200, lambda: self.btn_paste_coord.configure(text=t("war_paste_btn"), fg_color="#2563EB"))
        except Exception as exc:
            logger.debug("_on_paste_coord_clicked: failed to update paste button feedback: %s", exc)

    def _handle_coord_paste(self, event=None) -> str:
        """Handle paste event on coordinate entry, auto-parsing coordinates and updating entry."""
        try:
            clip_text = self.clipboard_get()
        except Exception:
            clip_text = ""
        if clip_text:
            if hasattr(self.war_service, "parse_coordinate"):
                parsed = self.war_service.parse_coordinate(clip_text)
                norm = f"{parsed.x}, {parsed.y}, {parsed.slot}"
            else:
                norm = clip_text.strip()
            self.coord_var.set(norm)
            try:
                inner = getattr(self.entry_coord, "_entry", self.entry_coord)
                inner.select_range(0, tk.END)
                inner.icursor(tk.END)
            except Exception as exc:
                logger.debug("_handle_coord_paste: failed to set cursor position: %s", exc)
            if hasattr(self.war_service, "parse_coordinate"):
                parsed = self.war_service.parse_coordinate(norm)
                self.set_active_slot_ui(parsed.slot)
        return "break"

    def _setup_coord_entry_support(self) -> None:
        """Attach right-click context menu, clipboard paste handler, and Thai/EN keyboard shortcuts."""
        inner = getattr(self.entry_coord, "_entry", self.entry_coord)

        def _do_paste(event=None):
            return self._handle_coord_paste(event)

        def _show_menu(event):
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(
                label=t("war_context_cut"),
                command=lambda: inner.event_generate("<<Cut>>"),
            )
            menu.add_command(
                label=t("war_context_copy"),
                command=lambda: inner.event_generate("<<Copy>>"),
            )
            menu.add_command(
                label=t("war_context_paste"),
                command=_do_paste,
            )
            menu.add_separator()
            menu.add_command(
                label=t("war_context_select_all"),
                command=lambda: (inner.select_range(0, tk.END), inner.icursor(tk.END)),
            )
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        # Handle physical keycodes when Ctrl is pressed (works in both English and Thai keyboard layouts)
        def _on_key(event):
            if event.state & 4:  # Control modifier held
                # 86: V (Paste), 67: C (Copy), 88: X (Cut), 65: A (Select All)
                if event.keycode == 86:
                    _do_paste()
                    return "break"
                elif event.keycode == 67:
                    inner.event_generate("<<Copy>>")
                    return "break"
                elif event.keycode == 88:
                    inner.event_generate("<<Cut>>")
                    return "break"
                elif event.keycode == 65:
                    inner.select_range(0, tk.END)
                    inner.icursor(tk.END)
                    return "break"

        for target in (self.entry_coord, inner):
            target.bind("<Button-3>", _show_menu)
            target.bind("<Key>", _on_key)
            target.bind("<<Paste>>", _do_paste)

    def _build_menu_panel(self, parent: ctk.CTkFrame) -> None:
        # 1. Logo
        logo_path = resource_path("logo.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                aspect_ratio = img.height / img.width
                logo_w = 110
                self.logo_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(logo_w, int(logo_w * aspect_ratio)),
                )
                lbl_logo = ctk.CTkLabel(parent, image=self.logo_image, text="")
                lbl_logo.pack(pady=(4, 0))
            except Exception as exc:
                logger.debug("_build_menu_panel: failed to load logo: %s", exc)

        # 2. Brand text
        brand_frame = ctk.CTkFrame(parent, fg_color="transparent")
        brand_frame.pack(pady=(0, 2))
        self.lbl_brand_sub = ctk.CTkLabel(
            brand_frame,
            text=t("brand_subtitle"),
            font=(FONT_FAMILY, 11, "bold"),
            text_color="#D81B60",
        )
        self.lbl_brand_sub.pack()
        self.lbl_brand_trk = ctk.CTkLabel(
            brand_frame,
            text=t("brand_tracker"),
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLOR_PINK_ACCENT,
        )
        self.lbl_brand_trk.pack(pady=(0, 1))

        sep = ctk.CTkFrame(brand_frame, height=2, fg_color=COLOR_PINK_HEADER)
        sep.pack(fill="x", padx=30, pady=1)

        self.lbl_brand_by = ctk.CTkLabel(
            brand_frame,
            text=t("brand_created_by"),
            font=(FONT_FAMILY, 8, "bold"),
            text_color=COLOR_TEXT_VAL,
        )
        self.lbl_brand_by.pack(pady=(1, 0))
        self.lbl_brand_team = ctk.CTkLabel(
            brand_frame,
            text=t("brand_team_credit"),
            font=(FONT_FAMILY, 9, "bold"),
            text_color=COLOR_TEXT_VAL,
        )
        self.lbl_brand_team.pack()

        # 3. Status & Folder Selector at bottom - PACK FIRST to guarantee visibility
        self.status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", pady=(4, 6), padx=14)

        initial_status = t("status_no_folder")
        status_color = COLOR_TEXT_SUB
        if hasattr(self.controller, "log_path") and self.controller.log_path:
            initial_status = t("status_reading_file", file=os.path.basename(self.controller.log_path))
            status_color = COLOR_TEXT_VAL
        elif hasattr(self.controller, "lbl_file_status"):
            try:
                initial_status = self.controller.lbl_file_status.cget("text")
                status_color = self.controller.lbl_file_status.cget("text_color")
            except Exception as exc:
                logger.debug("_build_menu_panel: failed to read controller file status: %s", exc)

        self.lbl_file_status = ctk.CTkLabel(
            self.status_frame,
            text=initial_status,
            text_color=status_color,
            wraplength=240,
            font=(FONT_FAMILY, 10),
        )
        self.lbl_file_status.pack(anchor="w", pady=(0, 2))

        self.btn_select = ctk.CTkButton(
            self.status_frame,
            text=t("btn_select_folder"),
            font=(FONT_FAMILY, 11),
            fg_color="#F0F0F0",
            text_color="#333333",
            hover_color="#E0E0E0",
            height=28,
            corner_radius=UI_RADIUS,
            command=self.controller.select_log_folder,
        )
        self.btn_select.pack(fill="x")

        self.lbl_version = ctk.CTkLabel(
            self.status_frame,
            text=APP_VERSION,
            font=("Arial", 8),
            text_color="gray",
        )
        self.lbl_version.pack(pady=(1, 0))

        # 4. Action Buttons
        BTN_HEIGHT = 28
        BTN_RADIUS = UI_RADIUS

        self.btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.btn_frame.pack(fill="both", expand=True, padx=16, pady=(2, 0))

        self.btn_reset = ctk.CTkButton(
            self.btn_frame,
            text=t("btn_reset"),
            font=(FONT_FAMILY, 12),
            fg_color=COLOR_PINK_HEADER,
            text_color=COLOR_TEXT_MAIN,
            hover_color=COLOR_PINK_SOFT,
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self.controller.confirm_reset,
        )
        self.btn_reset.pack(pady=(0, 3), fill="x")

        self.btn_watchlist = ctk.CTkButton(
            self.btn_frame,
            text=t("btn_watchlist"),
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_WATCHLIST,
            hover_color="#D81B60",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self.controller.open_watchlist_editor,
        )
        self.btn_watchlist.pack(pady=(0, 3), fill="x")

        self.switch_filter = ctk.CTkSwitch(
            self.btn_frame,
            text=t("switch_filter"),
            font=(FONT_FAMILY, 11, "bold"),
            progress_color=COLOR_WATCHLIST,
            command=self._on_toggle_filter,
        )
        self.switch_filter.pack(pady=(1, 3))
        if getattr(self.controller, "is_filter_active", False):
            self.switch_filter.select()

        row_overlays = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        row_overlays.pack(fill="x", pady=(0, 3))
        row_overlays.columnconfigure((0, 1), weight=1, uniform="equal")

        self.btn_overlay_full = ctk.CTkButton(
            row_overlays,
            text=t("btn_overlay_full"),
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLOR_PINK_ACCENT,
            hover_color="#FF1493",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=lambda: self.controller.open_overlay("full"),
        )
        self.btn_overlay_full.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        self.btn_overlay_mini = ctk.CTkButton(
            row_overlays,
            text=t("btn_overlay_mini"),
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#F06292",
            hover_color="#D81B60",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=lambda: self.controller.open_overlay("mini"),
        )
        self.btn_overlay_mini.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        row_help = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        row_help.pack(fill="x", pady=(0, 3))
        row_help.columnconfigure((0, 1), weight=1, uniform="equal")

        self.btn_how_to_use = ctk.CTkButton(
            row_help,
            text=t("btn_how_to_use"),
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self.controller.open_how_to_use,
        )
        self.btn_how_to_use.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        self.btn_discord = ctk.CTkButton(
            row_help,
            text=t("btn_discord"),
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLOR_DISCORD,
            hover_color="#AB47BC",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self.controller.open_discord,
        )
        self.btn_discord.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        # Language Selector Row in War Menu
        lang_row = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        lang_row.pack(fill="x", pady=(0, 2))
        self.lbl_sidebar_lang = ctk.CTkLabel(
            lang_row,
            text=f"🌐 {t('label_language')}:",
            font=(FONT_FAMILY, 10, "bold"),
            text_color=COLOR_TEXT_SUB,
        )
        self.lbl_sidebar_lang.pack(side="left", padx=(0, 4))
        self.seg_lang_sidebar = ctk.CTkSegmentedButton(
            lang_row,
            values=["EN", "TH", "JA"],
            height=24,
            font=(FONT_FAMILY, 10, "bold"),
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

    def _on_sidebar_lang_selected(self, val: str) -> None:
        if hasattr(self.controller, "set_app_language"):
            self.controller.set_app_language(val)
        else:
            i18n.set_language(val)
            self.retranslate_ui()

    def _on_language_changed(self, language: str = "", **kwargs) -> None:
        try:
            self.retranslate_ui()
        except Exception as exc:
            logger.debug("_on_language_changed: retranslate failed: %s", exc)

    def retranslate_ui(self) -> None:
        """Update all text in War Dashboard according to current language."""
        try:
            op_name = self.war_service.operative_name or getattr(self.controller, "character_name", "") or "Operative"
            if hasattr(self, "lbl_op_title") and self.lbl_op_title.winfo_exists():
                self.lbl_op_title.configure(text=t("war_op_title", name=op_name))
            if hasattr(self, "lbl_op_sub") and self.lbl_op_sub.winfo_exists():
                self.lbl_op_sub.configure(text=f"• {t('war_op_sub')}")
            if hasattr(self, "lbl_coord_title") and self.lbl_coord_title.winfo_exists():
                self.lbl_coord_title.configure(text=t("war_coord_label"))
            if hasattr(self, "btn_paste_coord") and self.btn_paste_coord.winfo_exists():
                self.btn_paste_coord.configure(text=t("war_paste_btn"))
            if hasattr(self, "btn_save_coord") and self.btn_save_coord.winfo_exists():
                self.btn_save_coord.configure(text=t("war_save_btn"))
            if hasattr(self, "opt_landmark") and self.opt_landmark.winfo_exists():
                landmarks = i18n.get_landmarks()
                self.opt_landmark.configure(values=landmarks)
                self.opt_landmark.set(landmarks[0])
            if hasattr(self, "btn_open_web") and self.btn_open_web.winfo_exists():
                self.btn_open_web.configure(text=t("war_btn_open_web"))
            if hasattr(self, "btn_back_offline") and self.btn_back_offline.winfo_exists():
                self.btn_back_offline.configure(text=t("war_btn_back_offline"))
            if hasattr(self, "lbl_brand_sub") and self.lbl_brand_sub.winfo_exists():
                self.lbl_brand_sub.configure(text=t("brand_subtitle"))
            if hasattr(self, "lbl_brand_trk") and self.lbl_brand_trk.winfo_exists():
                self.lbl_brand_trk.configure(text=t("brand_tracker"))
            if hasattr(self, "lbl_brand_by") and self.lbl_brand_by.winfo_exists():
                self.lbl_brand_by.configure(text=t("brand_created_by"))
            if hasattr(self, "lbl_brand_team") and self.lbl_brand_team.winfo_exists():
                self.lbl_brand_team.configure(text=t("brand_team_credit"))
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
            if hasattr(self, "btn_select") and self.btn_select.winfo_exists():
                self.btn_select.configure(text=t("btn_select_folder"))
            if hasattr(self, "lbl_sidebar_lang") and self.lbl_sidebar_lang.winfo_exists():
                self.lbl_sidebar_lang.configure(text=f"🌐 {t('label_language')}:")
            if hasattr(self, "seg_lang_sidebar") and self.seg_lang_sidebar.winfo_exists():
                self.seg_lang_sidebar.set(i18n.get_button_label())
            if hasattr(self, "dashboard_area") and hasattr(self.dashboard_area, "retranslate_ui"):
                self.dashboard_area.retranslate_ui()
            self.update_view()
        except Exception as exc:
            logger.debug("retranslate_ui: failed to retranslate war dashboard: %s", exc)

    def _on_toggle_filter(self) -> None:
        if hasattr(self, "switch_filter") and hasattr(self.controller, "toggle_filter"):
            val = bool(self.switch_filter.get())
            self.controller.toggle_filter(val)

    def update_view(self) -> None:
        """Called by controller or timer to refresh war view stats."""
        try:
            self._process_ui_sync_queue()
        except Exception as exc:
            logger.debug("update_view: failed to process UI sync queue: %s", exc)

        op_name = self.war_service.operative_name or getattr(self.controller, "character_name", "") or "Operative"

        if hasattr(self, "lbl_op_title"):
            self.lbl_op_title.configure(text=t("war_op_title", name=op_name))
        elif hasattr(self, "lbl_op_name"):
            self.lbl_op_name.configure(text=t("war_op_title", name=op_name))

        if hasattr(self, "entry_coord"):
            tc = getattr(self.war_service, "target_coord", (0, 0, 1))
            gx = getattr(tc, "x", tc[0])
            gy = getattr(tc, "y", tc[1])
            cslot = getattr(tc, "slot", tc[2] if len(tc) >= 3 else 1)
            current_str = f"{gx}, {gy}, {cslot}"
            focused_w = self.focus_get()
            is_entry_focused = focused_w in (
                self.entry_coord,
                getattr(self.entry_coord, "_entry", None),
            )
            if self.coord_var.get() != current_str and not is_entry_focused:
                self.coord_var.set(current_str)
            self.set_active_slot_ui(cslot)

        if hasattr(self, "dashboard_area"):
            try:
                self.dashboard_area.update_display()
                self.dashboard_area.update_live_stats()
            except Exception as exc:
                logger.debug("update_view: failed to update dashboard area: %s", exc)

        # Sync menu controls with controller state
        if hasattr(self, "switch_filter") and hasattr(self.controller, "is_filter_active"):
            try:
                if self.controller.is_filter_active:
                    self.switch_filter.select()
                else:
                    self.switch_filter.deselect()
            except Exception as exc:
                logger.debug("update_view: failed to sync filter switch: %s", exc)

        if hasattr(self, "lbl_file_status") and hasattr(self.controller, "lbl_file_status"):
            try:
                self.lbl_file_status.configure(
                    text=self.controller.lbl_file_status.cget("text"),
                    text_color=self.controller.lbl_file_status.cget("text_color"),
                )
            except Exception as exc:
                logger.debug("update_view: failed to sync file status label: %s", exc)

        is_syncing = getattr(self.war_service, "_is_syncing", False) or getattr(self, "_is_sync_animating", False)
        last_sync_time = getattr(self.war_service, "_last_sync_time", 0)
        last_sync_status = getattr(self.war_service, "_last_sync_status", (True, ""))
        if hasattr(self, "lbl_sync_time") and not is_syncing and last_sync_time > 0 and last_sync_status[0]:
            try:
                t_str = time.strftime("%H:%M:%S", time.localtime(last_sync_time))
                if getattr(self, "_last_display_contrib", None) is not None:
                    display_contrib = self._last_display_contrib
                else:
                    display_contrib = max(getattr(self.war_service, "total_farmed", 0), getattr(self.war_service, "session_contribution", 0))
                new_text = t("war_synced", time=t_str, contrib=f"{display_contrib:,}")
                new_color = "#10B981"
                if self.lbl_sync_time.cget("text") != new_text or self.lbl_sync_time.cget("text_color") != new_color:
                    self.lbl_sync_time.configure(
                        text=new_text,
                        text_color=new_color,
                    )
            except Exception as exc:
                logger.debug("update_view: failed to update sync time label: %s", exc)

    def _open_web_war_room(self) -> None:
        try:
            webbrowser.open(DEFAULT_WAR_ROOM_URL)
        except Exception as e:
            self.lbl_sync_time.configure(text=f"Failed to open URL: {e}", text_color="#EF4444")

    def _do_sync(self) -> None:
        self.lbl_sync_time.configure(text=t("war_syncing"), text_color="#0284C7")
        self.update_idletasks()
        success, msg = self.war_service.sync_to_war_room(force_cloud=True)
        now_str = time.strftime("%H:%M:%S")
        if success:
            active_c = max(getattr(self.war_service, "total_farmed", 0), getattr(self.war_service, "session_contribution", 0))
            self.lbl_sync_time.configure(
                text=t("war_synced", time=now_str, contrib=f"{active_c:,}"),
                text_color="#10B981",
            )
        else:
            self.lbl_sync_time.configure(text=msg or t("war_sync_error"), text_color="#EF4444")
        self.update_view()


if __name__ == "__main__":
    print("=" * 60)
    print("🪐  NEKO Tracker — WarDashboardFrame Standalone Launcher")
    print("=" * 60)
    root = ctk.CTk()
    root.geometry("950x620")
    root.title("NEKO Tracker - War Mode Test")
    war_srv = WarService()

    class DummyCtrl:
        def __init__(self):
            self.character_name = "SoloHero"
            self.board_coord = "0, 0"
        def show_offline_view(self):
            print(" [✓] Back to offline clicked!")
            root.destroy()
        def update_board_coordinate(self, val):
            return val

    view = WarDashboardFrame(root, DummyCtrl(), war_srv)
    view.pack(fill="both", expand=True)
    view.update_view()
    root.mainloop()
