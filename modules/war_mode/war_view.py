from __future__ import annotations

import os
import sys
import time
import webbrowser
import tkinter as tk
from typing import Any, Dict, List, Optional, Tuple
import customtkinter as ctk

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
    resource_path,
)
from PIL import Image
from dashboard_ui import DashboardFrame

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

        self._build_ui()
        self._subscribe_events()

    def _subscribe_events(self) -> None:
        try:
            from modules.event_bus import event_bus
            event_bus.subscribe("realtime_sync_started", self._on_realtime_sync_started)
            event_bus.subscribe("realtime_sync_completed", self._on_realtime_sync_completed)
            event_bus.subscribe("board_coord_changed", self._on_board_coord_changed)
        except Exception:
            pass

    def _on_realtime_sync_started(self, **kwargs) -> None:
        try:
            if hasattr(self, "lbl_sync_time") and self.lbl_sync_time.winfo_exists():
                self.lbl_sync_time.configure(text="⚡ กำลังซิงค์ขึ้น Firebase...", text_color="#0284C7")
        except Exception:
            pass

    def _on_realtime_sync_completed(self, success: bool = True, message: str = "", timestamp: float = 0, contribution: int = 0, **kwargs) -> None:
        try:
            if hasattr(self, "lbl_sync_time") and self.lbl_sync_time.winfo_exists():
                t_val = timestamp or time.time()
                t_str = time.strftime("%H:%M:%S", time.localtime(t_val))
                if success:
                    contrib = contribution if contribution > 0 else getattr(self.war_service, "session_contribution", 0)
                    self.lbl_sync_time.configure(
                        text=f"⚡ Firebase ซิงค์: ล่าสุด {t_str} (+{contrib:,} ℳ)",
                        text_color="#10B981",
                    )
                else:
                    self.lbl_sync_time.configure(
                        text=f"⚡ ซิงค์เรียลไทม์ (รอการเชื่อมต่อ)",
                        text_color="#F59E0B",
                    )
        except Exception:
            pass

    def _on_board_coord_changed(self, coord: str = "", **kwargs) -> None:
        try:
            if coord and hasattr(self, "coord_var"):
                self.coord_var.set(coord)
        except Exception:
            pass

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Top War Room Banner: Operative Info (Primary Key) + Board Coordinate Entry + Sync Status
        self.top_banner = ctk.CTkFrame(self, fg_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS, height=52)
        self.top_banner.grid(row=0, column=0, sticky="ew", padx=15, pady=(8, 6))
        self.top_banner.pack_propagate(False)

        top_left = ctk.CTkFrame(self.top_banner, fg_color="transparent")
        top_left.pack(side="left", padx=(15, 10), pady=4)

        self.lbl_op_title = ctk.CTkLabel(
            top_left,
            text="👤 ชื่อในเกม: -",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_op_title.pack(anchor="w")
        self.lbl_op_name = self.lbl_op_title

        self.lbl_op_sub = ctk.CTkLabel(
            top_left,
            text="Primary Key จาก Log ไฟล์เกม",
            font=(FONT_FAMILY, 10),
            text_color="#64748B",
        )
        self.lbl_op_sub.pack(anchor="w")

        # Top Center: Board Coordinate Input (พิกัดบนกระดานที่ user เป็นคนกรอก)
        self.coord_frame = ctk.CTkFrame(self.top_banner, fg_color="transparent")
        self.coord_frame.pack(side="left", padx=(15, 0), pady=4)

        ctk.CTkLabel(
            self.coord_frame,
            text="🎯 พิกัด [X, Y]:",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLOR_TEXT_MAIN,
        ).pack(side="left", padx=(0, 4))

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
        landmark_options = [
            "🪐 พิกัดสำคัญ...",
            "🌌 Core [0, 0]",
            "🏙️ NGS [3, 3]",
            "🌍 Earth [9, -3]",
            "☀️ Sun [8, -3]",
            "🔴 Mars [9, -4]",
            "🌲 Naberius [-2, -2]",
            "🌋 Amduskia [-3, -3]",
            "🏜️ Lillipa [-1, -3]",
            "🚀 Hail Mary [20, 7]",
        ]
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
            text="📋 วาง",
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
            text="💾 บันทึก",
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

        # Top Right: Realtime Status & Sync Status
        top_right = ctk.CTkFrame(self.top_banner, fg_color="transparent")
        top_right.pack(side="right", padx=15, pady=4)

        self.lbl_war_status = ctk.CTkLabel(
            top_right,
            text="🟢 ประจำการรบ (REALTIME ONLINE)",
            font=(FONT_FAMILY, 11, "bold"),
            text_color="#10B981",
        )
        self.lbl_war_status.pack(anchor="e")

        self.lbl_sync_time = ctk.CTkLabel(
            top_right,
            text="⚡ ระบบซิงค์เรียลไทม์พร้อมทำงาน",
            font=(FONT_FAMILY, 10),
            text_color=COLOR_TEXT_SUB,
        )
        self.lbl_sync_time.pack(anchor="e")

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
            text="🪐 ARKS War Room (Web)",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#0284C7",
            hover_color="#0369A1",
            text_color="white",
            height=32,
            corner_radius=UI_RADIUS,
            command=self._open_web_war_room,
        )
        self.btn_open_web.pack(side="left", padx=(10, 6), pady=7)

        # Sync Button
        self.btn_sync = ctk.CTkButton(
            btn_bar,
            text="⚡ ซิงค์เรียลไทม์ (ซิงค์ทันที)",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            height=32,
            corner_radius=UI_RADIUS,
            command=self._do_sync,
        )
        self.btn_sync.pack(side="left", padx=(0, 6), pady=7)

        # Right Action: Back to Main Offline View (No login / logout needed!)
        self.btn_back_offline = ctk.CTkButton(
            btn_bar,
            text="🔙 กลับสู่โหมดออฟไลน์",
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
            except Exception:
                pass

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
            "Sun": (8, -3),
            "Mars": (9, -4),
            "Naberius": (-2, -2),
            "Amduskia": (-3, -3),
            "Lillipa": (-1, -3),
            "Hail Mary": (20, 7),
        }
        for key, (lx, ly) in landmarks_map.items():
            if key in choice:
                current_slot = getattr(self.war_service.target_coord, "slot", 1)
                self.coord_var.set(f"{lx}, {ly}, {current_slot}")
                self._on_coord_submit()
                break
        if hasattr(self, "opt_landmark"):
            self.opt_landmark.set("🪐 พิกัดสำคัญ...")

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
                self.btn_paste_coord.configure(text="✓ วางแล้ว", fg_color="#059669")
                self.after(1200, lambda: self.btn_paste_coord.configure(text="📋 วาง", fg_color="#2563EB"))
        except Exception:
            pass

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
            except Exception:
                pass
            if hasattr(self.war_service, "parse_coordinate"):
                parsed = self.war_service.parse_coordinate(norm)
                self.set_active_slot_ui(parsed.slot)
        return "break"

    def _setup_coord_entry_support(self) -> None:
        """Attach right-click context menu, clipboard paste handler, and Thai keyboard shortcuts."""
        inner = getattr(self.entry_coord, "_entry", self.entry_coord)

        def _do_paste(event=None):
            return self._handle_coord_paste(event)

        def _show_menu(event):
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(
                label="✂️ ตัด (Cut)",
                command=lambda: inner.event_generate("<<Cut>>"),
            )
            menu.add_command(
                label="📄 คัดลอก (Copy)",
                command=lambda: inner.event_generate("<<Copy>>"),
            )
            menu.add_command(
                label="📋 วางพิกัด (Paste)",
                command=_do_paste,
            )
            menu.add_separator()
            menu.add_command(
                label="🔘 เลือกทั้งหมด (Select All)",
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
                logo_w = 140
                self.logo_image = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(logo_w, int(logo_w * aspect_ratio)),
                )
                lbl_logo = ctk.CTkLabel(parent, image=self.logo_image, text="")
                lbl_logo.pack(pady=(6, 0))
            except Exception:
                pass

        # 2. Brand text
        brand_frame = ctk.CTkFrame(parent, fg_color="transparent")
        brand_frame.pack(pady=(0, 2))
        ctk.CTkLabel(
            brand_frame,
            text="ITEM & MESETA",
            font=(FONT_FAMILY, 13, "bold"),
            text_color="#D81B60",
        ).pack()
        ctk.CTkLabel(
            brand_frame,
            text="TRACKER",
            font=(FONT_FAMILY, 20, "bold"),
            text_color=COLOR_PINK_ACCENT,
        ).pack(pady=(0, 1))

        sep = ctk.CTkFrame(brand_frame, height=2, fg_color=COLOR_PINK_HEADER)
        sep.pack(fill="x", padx=30, pady=2)

        ctk.CTkLabel(
            brand_frame,
            text="CREATED BY",
            font=(FONT_FAMILY, 9, "bold"),
            text_color=COLOR_TEXT_VAL,
        ).pack(pady=(1, 0))
        ctk.CTkLabel(
            brand_frame,
            text="TEAM NEKO FAMILY SHIP 4 TH",
            font=(FONT_FAMILY, 10, "bold"),
            text_color=COLOR_TEXT_VAL,
        ).pack()

        # 3. Action Buttons
        BTN_HEIGHT = 30
        BTN_RADIUS = UI_RADIUS

        self.btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=20, pady=(2, 0))

        self.btn_reset = ctk.CTkButton(
            self.btn_frame,
            text="เริ่มนับใหม่ (Reset)",
            font=(FONT_FAMILY, 12),
            fg_color=COLOR_PINK_HEADER,
            text_color=COLOR_TEXT_MAIN,
            hover_color=COLOR_PINK_SOFT,
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self.controller.confirm_reset,
        )
        self.btn_reset.pack(pady=(0, 4), fill="x")

        self.btn_watchlist = ctk.CTkButton(
            self.btn_frame,
            text="Edit Watch List",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_WATCHLIST,
            hover_color="#D81B60",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self.controller.open_watchlist_editor,
        )
        self.btn_watchlist.pack(pady=(0, 4), fill="x")

        self.switch_filter = ctk.CTkSwitch(
            self.btn_frame,
            text="เปิดใช้ Watch List Filter",
            font=(FONT_FAMILY, 11, "bold"),
            progress_color=COLOR_WATCHLIST,
            command=self._on_toggle_filter,
        )
        self.switch_filter.pack(pady=(2, 4))
        if getattr(self.controller, "is_filter_active", False):
            self.switch_filter.select()

        row_overlays = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        row_overlays.pack(fill="x", pady=(0, 4))
        row_overlays.columnconfigure((0, 1), weight=1, uniform="equal")

        self.btn_overlay_full = ctk.CTkButton(
            row_overlays,
            text="Item & Meseta",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color=COLOR_PINK_ACCENT,
            hover_color="#FF1493",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=lambda: self.controller.open_overlay("full"),
        )
        self.btn_overlay_full.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.btn_overlay_mini = ctk.CTkButton(
            row_overlays,
            text="Meseta",
            font=(FONT_FAMILY, 11, "bold"),
            fg_color="#F06292",
            hover_color="#D81B60",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=lambda: self.controller.open_overlay("mini"),
        )
        self.btn_overlay_mini.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        self.btn_discord = ctk.CTkButton(
            self.btn_frame,
            text="DISCORD NEKO FAMILY",
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLOR_DISCORD,
            hover_color="#AB47BC",
            text_color="white",
            height=BTN_HEIGHT,
            corner_radius=BTN_RADIUS,
            command=self.controller.open_discord,
        )
        self.btn_discord.pack(fill="x", pady=(0, 4))

        # 4. Status & Folder Selector at bottom
        self.status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", pady=(2, 4), padx=15)

        initial_status = "ยังไม่เลือกโฟลเดอร์ Log"
        status_color = COLOR_TEXT_SUB
        if hasattr(self.controller, "lbl_file_status"):
            try:
                initial_status = self.controller.lbl_file_status.cget("text")
                status_color = self.controller.lbl_file_status.cget("text_color")
            except Exception:
                pass

        self.lbl_file_status = ctk.CTkLabel(
            self.status_frame,
            text=initial_status,
            text_color=status_color,
            wraplength=260,
            font=(FONT_FAMILY, 10),
        )
        self.lbl_file_status.pack(anchor="w", pady=(0, 2))

        self.btn_select = ctk.CTkButton(
            self.status_frame,
            text="📂 จิ้มเลือกโฟลเดอร์ Log",
            font=(FONT_FAMILY, 11),
            fg_color="#F0F0F0",
            text_color="#333333",
            hover_color="#E0E0E0",
            height=26,
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

    def _on_toggle_filter(self) -> None:
        if hasattr(self, "switch_filter") and hasattr(self.controller, "toggle_filter"):
            val = bool(self.switch_filter.get())
            self.controller.toggle_filter(val)

    def update_view(self) -> None:
        """Called by controller or timer to refresh war view stats."""
        op_name = self.war_service.operative_name or getattr(self.controller, "character_name", "") or "Operative"

        if hasattr(self, "lbl_op_title"):
            self.lbl_op_title.configure(text=f"👤 ชื่อในเกม: {op_name}")
        elif hasattr(self, "lbl_op_name"):
            self.lbl_op_name.configure(text=f"👤 ชื่อในเกม: {op_name}")

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
            except Exception:
                pass

        # Sync menu controls with controller state
        if hasattr(self, "switch_filter") and hasattr(self.controller, "is_filter_active"):
            try:
                if self.controller.is_filter_active:
                    self.switch_filter.select()
                else:
                    self.switch_filter.deselect()
            except Exception:
                pass

        if hasattr(self, "lbl_file_status") and hasattr(self.controller, "lbl_file_status"):
            try:
                self.lbl_file_status.configure(
                    text=self.controller.lbl_file_status.cget("text"),
                    text_color=self.controller.lbl_file_status.cget("text_color"),
                )
            except Exception:
                pass

        if hasattr(self, "lbl_sync_time") and not getattr(self.war_service, "_is_syncing", False) and getattr(self.war_service, "_last_sync_time", 0) > 0:
            try:
                t_str = time.strftime("%H:%M:%S", time.localtime(self.war_service._last_sync_time))
                self.lbl_sync_time.configure(
                    text=f"⚡ Firebase ซิงค์: ล่าสุด {t_str} (+{self.war_service.session_contribution:,} ℳ)",
                    text_color="#10B981",
                )
            except Exception:
                pass

    def _open_web_war_room(self) -> None:
        index_path = os.path.abspath("E:/ARKS War Room/index.html")
        if os.path.exists(index_path):
            webbrowser.open(f"file:///{index_path}")
        else:
            self.lbl_sync_time.configure(text="ไม่พบไฟล์ E:/ARKS War Room/index.html", text_color="#EF4444")

    def _do_sync(self) -> None:
        self.lbl_sync_time.configure(text="⚡ กำลังซิงค์ข้อมูล Realtime...", text_color="#0284C7")
        self.update_idletasks()
        success, msg = self.war_service.sync_to_war_room()
        color = "#10B981" if success else "#EF4444"
        now_str = time.strftime("%H:%M:%S")
        if success:
            self.lbl_sync_time.configure(
                text=f"⚡ Firebase ซิงค์: ล่าสุด {now_str} (+{self.war_service.session_contribution:,} ℳ)",
                text_color=color,
            )
        else:
            self.lbl_sync_time.configure(text=msg, text_color=color)
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
