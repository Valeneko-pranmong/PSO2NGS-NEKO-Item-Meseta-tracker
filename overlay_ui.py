import customtkinter as ctk
import tkinter as tk
import time
import os
from config import *
from modules.utils import (
    format_compact,
    format_rate,
    format_duration,
    filter_and_sort_items,
    WindowMover,
    start_native_drag,
    calculate_live_rate,
    is_position_on_screen,
)
from modules.i18n import t
from modules.event_bus import event_bus

# Backward-compatible aliases
_format_compact = format_compact
_format_rate = format_rate
_format_duration = format_duration


class OverlayWindow(ctk.CTkToplevel):
    OPACITY_HIGH = 0.95
    OPACITY_LOW = 0.55
    MAX_NAME_CHARS = 22
    MAX_ITEMS = 30

    def __init__(self, controller, mode="full"):
        super().__init__()
        self.controller = controller
        self.mode = mode

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self._window_mover = WindowMover(self, on_move_end=self._on_overlay_moved)
        self._opacity_high = True
        self.attributes("-alpha", self.OPACITY_HIGH)
        self.configure(fg_color=COLOR_BG_MAIN)
        self.title(t("overlay_window_title"))

        try:
            event_bus.subscribe("language_changed", self._on_language_changed)
        except Exception:
            pass

        if os.path.exists(ICON_FILENAME):
            try:
                self.after(200, lambda: self.iconbitmap(ICON_FILENAME))
            except tk.TclError:
                pass

        self._position_window()

        self.item_rows = []
        self._drag_offset_x = 0
        self._drag_offset_y = 0

        self._build_outer_frame()
        self._build_header_bar()
        self._build_money_section()
        self._build_stats_section()
        if self.mode == "full":
            self._build_item_list()
        else:
            self.update_idletasks()
            needed_h = max(250, self.inner_frame.winfo_reqheight() + 4)
            if self.winfo_height() < needed_h:
                self.geometry(f"{self.winfo_width()}x{needed_h}")

        self.update_data()

    # ---------- Layout ----------

    def _on_overlay_moved(self, x: int, y: int) -> None:
        if x > -10000 and y > -10000:
            if hasattr(self.controller, "overlay_pos"):
                self.controller.overlay_pos = {"x": x, "y": y}
                if hasattr(self.controller, "save_settings"):
                    self.controller.save_settings()

    def _position_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 290
        x_pos = screen_width - window_width - 12

        if self.mode == "full":
            target_height = int(screen_height * 0.78)
            y_pos = int(screen_height * 0.10)
        else:
            target_height = 250
            y_pos = int(screen_height * 0.15)

        saved_pos = getattr(self.controller, "overlay_pos", None)
        if saved_pos and isinstance(saved_pos, dict):
            sx = saved_pos.get("x")
            sy = saved_pos.get("y")
            if sx is not None and sy is not None and is_position_on_screen(sx, sy):
                self.geometry(f"{window_width}x{target_height}+{sx}+{sy}")
                return

        self.geometry(f"{window_width}x{target_height}+{x_pos}+{y_pos}")

    def _build_outer_frame(self):
        self.inner_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_MAIN,
            corner_radius=UI_RADIUS,
            border_width=2,
            border_color=COLOR_PINK_HEADER,
        )
        self.inner_frame.pack(fill="both", expand=True, padx=2, pady=2)

    def _build_header_bar(self):
        self.header = ctk.CTkFrame(
            self.inner_frame,
            fg_color=COLOR_PINK_HEADER,
            corner_radius=UI_RADIUS - 2,
            height=30,
        )
        self.header.pack(fill="x", padx=6, pady=(6, 4))
        self.header.pack_propagate(False)

        title_text = t("overlay_title_full") if self.mode == "full" else t("overlay_title_mini")
        self.lbl_title = ctk.CTkLabel(
            self.header,
            text=title_text,
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_title.pack(side="left", padx=12)

        self.btn_close = ctk.CTkButton(
            self.header,
            text="×",
            width=24, height=24,
            font=("Arial", 16, "bold"),
            fg_color="transparent",
            text_color=COLOR_TEXT_MAIN,
            hover_color=COLOR_PINK_SOFT,
            corner_radius=6,
            command=self.destroy,
        )
        self.btn_close.pack(side="right", padx=(2, 6))

        self.btn_show_main = ctk.CTkButton(
            self.header,
            text="🏠",
            width=24, height=24,
            font=("Segoe UI Emoji", 12),
            fg_color="transparent",
            hover_color=COLOR_PINK_SOFT,
            corner_radius=6,
            command=self.controller.summon_main_window,
        )
        self.btn_show_main.pack(side="right", padx=2)

        self.btn_pin = ctk.CTkButton(
            self.header,
            text="●",
            width=24, height=24,
            font=("Arial", 12, "bold"),
            fg_color="transparent",
            hover_color=COLOR_PINK_SOFT,
            text_color=COLOR_TEXT_MAIN,
            corner_radius=6,
            command=self._toggle_opacity,
        )
        self.btn_pin.pack(side="right", padx=2)

        self._make_draggable(self.header, self.lbl_title)

    def _build_money_section(self):
        self.lbl_money = ctk.CTkLabel(
            self.inner_frame,
            text="+0",
            font=("Impact", 34),
            text_color=COLOR_TEXT_VAL,
        )
        self.lbl_money.pack(pady=(8, 0))

        self.lbl_subtitle = ctk.CTkLabel(
            self.inner_frame,
            text=t("overlay_subtitle"),
            font=(FONT_FAMILY, 11),
            text_color=COLOR_TEXT_SUB,
        )
        self.lbl_subtitle.pack(pady=(0, 4))

        self.lbl_wallet_overlay = ctk.CTkLabel(
            self.inner_frame,
            text=t("overlay_wallet", wallet="---"),
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_wallet_overlay.pack(pady=(0, 6))

        self._make_draggable(self.lbl_money, self.lbl_subtitle, self.lbl_wallet_overlay)

    def _build_stats_section(self):
        stats_frame = ctk.CTkFrame(
            self.inner_frame, fg_color=COLOR_PINK_SOFT, corner_radius=8
        )
        stats_frame.pack(fill="x", padx=14, pady=(2, 10))
        stats_frame.columnconfigure((0, 1), weight=1, uniform="s")

        time_col = ctk.CTkFrame(stats_frame, fg_color="transparent")
        time_col.grid(row=0, column=0, sticky="nsew", padx=10, pady=6)
        self.lbl_time_cap = ctk.CTkLabel(
            time_col, text=t("overlay_time_cap"),
            font=(FONT_FAMILY, 9, "bold"), text_color=COLOR_TEXT_SUB,
        )
        self.lbl_time_cap.pack(anchor="w")
        self.lbl_time_overlay = ctk.CTkLabel(
            time_col, text="00:00:00",
            font=("Impact", 17), text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_time_overlay.pack(anchor="w")

        rate_col = ctk.CTkFrame(stats_frame, fg_color="transparent")
        rate_col.grid(row=0, column=1, sticky="nsew", padx=10, pady=6)
        self.lbl_rate_cap = ctk.CTkLabel(
            rate_col, text=t("overlay_rate_cap"),
            font=(FONT_FAMILY, 9, "bold"), text_color=COLOR_TEXT_SUB,
        )
        self.lbl_rate_cap.pack(anchor="e")
        self.lbl_mhr_overlay = ctk.CTkLabel(
            rate_col, text="0 /hr",
            font=("Impact", 17), text_color=COLOR_PINK_ACCENT,
        )
        self.lbl_mhr_overlay.pack(anchor="e")

        self._make_draggable(
            stats_frame, time_col, rate_col,
            self.lbl_time_cap, self.lbl_rate_cap,
            self.lbl_time_overlay, self.lbl_mhr_overlay,
        )

    def _build_item_list(self):
        head = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(0, 2))
        self.lbl_drops = ctk.CTkLabel(
            head, text=t("overlay_drops_cap"),
            font=(FONT_FAMILY, 10, "bold"), text_color=COLOR_TEXT_SUB,
        )
        self.lbl_drops.pack(side="left")
        self.lbl_filter_badge = ctk.CTkLabel(
            head, text="",
            font=(FONT_FAMILY, 10, "bold"), text_color=COLOR_WATCHLIST,
        )
        self.lbl_filter_badge.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(
            self.inner_frame, fg_color="transparent", corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.empty_label = ctk.CTkLabel(
            self.list_frame, text=t("overlay_waiting"),
            font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SUB,
        )

        self._make_draggable(head, self.lbl_drops, self.lbl_filter_badge)

    # ---------- Behavior ----------

    def _toggle_opacity(self):
        self._opacity_high = not self._opacity_high
        self.attributes(
            "-alpha",
            self.OPACITY_HIGH if self._opacity_high else self.OPACITY_LOW,
        )
        self.btn_pin.configure(text="●" if self._opacity_high else "○")

    def update_data(self):
        try:
            session = self.controller.session_meseta
            sign = "+" if session >= 0 else "-"
            self.lbl_money.configure(text=f"{sign}{_format_compact(abs(session))}")

            wallet = self.controller.current_wallet
            if wallet > 0:
                self.lbl_wallet_overlay.configure(text=t("overlay_wallet", wallet=f"{wallet:,}"))
            else:
                self.lbl_wallet_overlay.configure(text=t("overlay_wallet", wallet="---"))

            duration = 0
            first = getattr(self.controller, "first_drop_time", None)
            if first is not None:
                duration = max(0, time.time() - first)

            self.lbl_time_overlay.configure(text=_format_duration(duration))

            rate = calculate_live_rate(session, duration, min_smoothing_seconds=30.0) if (duration >= 1 and session > 0) else 0
            self.lbl_mhr_overlay.configure(text=_format_rate(rate))

            if self.mode == "full":
                self.redraw_items()
        except tk.TclError:
            pass

    def _filtered_items(self):
        with self.controller.data_lock:
            snapshot = self.controller.item_counts.copy()

        watchlist = self.controller.watchlist_items
        keyword = self.controller.search_keyword
        filter_enabled = self.controller.is_filter_active

        items = filter_and_sort_items(
            snapshot,
            watchlist=watchlist,
            keyword=keyword,
            filter_enabled=filter_enabled,
            max_items=self.MAX_ITEMS,
        )
        return items, filter_enabled

    def redraw_items(self):
        items, filter_enabled = self._filtered_items()

        self.lbl_filter_badge.configure(text=t("overlay_focus_badge") if filter_enabled else "")

        for row in self.item_rows:
            row["frame"].pack_forget()
        self.empty_label.pack_forget()

        if not items:
            self.empty_label.configure(
                text=t("overlay_focus_empty") if filter_enabled else t("overlay_waiting")
            )
            self.empty_label.pack(pady=24)
            return

        while len(self.item_rows) < len(items):
            self._make_row()

        for i, (name, count) in enumerate(items):
            row = self.item_rows[i]
            row["idx"].configure(text=f"{i+1:>2}.")
            display_name = (
                name[: self.MAX_NAME_CHARS - 1] + "…"
                if len(name) > self.MAX_NAME_CHARS else name
            )
            row["name"].configure(text=display_name)
            row["count"].configure(text=f"×{count:,}")
            row["frame"].pack(fill="x", pady=1, padx=2)

    def _on_language_changed(self, language: str = "", **kwargs) -> None:
        try:
            self.retranslate_ui()
        except Exception:
            pass

    def retranslate_ui(self) -> None:
        """Update all text in Overlay window according to current language."""
        try:
            self.title(t("overlay_window_title"))
            title_text = t("overlay_title_full") if self.mode == "full" else t("overlay_title_mini")
            if hasattr(self, "lbl_title") and self.lbl_title.winfo_exists():
                self.lbl_title.configure(text=title_text)
            if hasattr(self, "lbl_subtitle") and self.lbl_subtitle.winfo_exists():
                self.lbl_subtitle.configure(text=t("overlay_subtitle"))
            if hasattr(self, "lbl_time_cap") and self.lbl_time_cap.winfo_exists():
                self.lbl_time_cap.configure(text=t("overlay_time_cap"))
            if hasattr(self, "lbl_rate_cap") and self.lbl_rate_cap.winfo_exists():
                self.lbl_rate_cap.configure(text=t("overlay_rate_cap"))
            if hasattr(self, "lbl_drops") and self.lbl_drops.winfo_exists():
                self.lbl_drops.configure(text=t("overlay_drops_cap"))
            self.update_data()
        except Exception:
            pass

    def destroy(self):
        try:
            ox = self.winfo_x()
            oy = self.winfo_y()
            if ox > -10000 and oy > -10000:
                if hasattr(self.controller, "overlay_pos"):
                    self.controller.overlay_pos = {"x": ox, "y": oy}
                    if hasattr(self.controller, "save_settings"):
                        self.controller.save_settings()
        except Exception:
            pass
        try:
            event_bus.unsubscribe("language_changed", self._on_language_changed)
        except Exception:
            pass
        super().destroy()

    def _make_row(self):
        frame = ctk.CTkFrame(self.list_frame, fg_color="transparent",
                             height=24, corner_radius=6)
        idx = ctk.CTkLabel(frame, text="", width=24,
                           font=(FONT_FAMILY, 10, "bold"),
                           text_color=COLOR_TEXT_SUB)
        idx.pack(side="left")
        name = ctk.CTkLabel(frame, text="", font=(FONT_FAMILY, 11),
                            anchor="w", justify="left",
                            text_color=COLOR_TEXT_MAIN)
        name.pack(side="left", padx=2, fill="x", expand=True)
        count = ctk.CTkLabel(frame, text="", font=(FONT_FAMILY, 11, "bold"),
                             text_color=COLOR_PINK_ACCENT)
        count.pack(side="right", padx=6)

        def on_enter(_e, f=frame): f.configure(fg_color=COLOR_PINK_SOFT)
        def on_leave(_e, f=frame): f.configure(fg_color="transparent")
        for w in (frame, idx, name, count):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        self.item_rows.append({"frame": frame, "idx": idx,
                               "name": name, "count": count})

    # ---------- Drag ----------

    def _make_draggable(self, *widgets):
        for w in widgets:
            w.bind("<ButtonPress-1>", self.start_move)
            w.bind("<B1-Motion>", self.do_move)
            w.bind("<ButtonRelease-1>", self.end_move)

    def start_move(self, event):
        self._window_mover.start_move(event)

    def do_move(self, event):
        self._window_mover.do_move(event)

    def end_move(self, event=None):
        self._window_mover.end_move(event)
        self._on_overlay_moved(self.winfo_x(), self.winfo_y())
