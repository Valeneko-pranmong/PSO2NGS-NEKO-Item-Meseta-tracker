import customtkinter as ctk
import tkinter as tk
import time
import os
from config import *


def _format_compact(value):
    av = abs(value)
    sign = "-" if value < 0 else ""
    if av >= 1_000_000:
        return f"{sign}{av/1_000_000:.2f}M"
    if av >= 10_000:
        return f"{sign}{av/1_000:.1f}k"
    return f"{sign}{av:,}"


def _format_rate(meseta_per_hour):
    if meseta_per_hour <= 0:
        return "0 /hr"
    if meseta_per_hour >= 1_000_000:
        return f"{meseta_per_hour/1_000_000:.2f} M/hr"
    if meseta_per_hour >= 1_000:
        return f"{meseta_per_hour/1_000:.1f} k/hr"
    return f"{int(meseta_per_hour)} /hr"


def _format_duration(seconds):
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


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
        self._opacity_high = True
        self.attributes("-alpha", self.OPACITY_HIGH)
        self.configure(fg_color=COLOR_BG_MAIN)
        self.title("Gadget Mode - NEKO Tracker")

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

        self.update_data()

    # ---------- Layout ----------

    def _position_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = 290
        x_pos = screen_width - window_width - 12

        if self.mode == "full":
            target_height = int(screen_height * 0.78)
            y_pos = int(screen_height * 0.10)
        else:
            target_height = 200
            y_pos = int(screen_height * 0.15)

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

        title_text = "ITEM • MESETA" if self.mode == "full" else "MESETA"
        self.lbl_title = ctk.CTkLabel(
            self.header,
            text=title_text,
            font=("Kanit", 11, "bold"),
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
            text="เงินรอบนี้ (Session)",
            font=("Kanit", 11),
            text_color=COLOR_TEXT_SUB,
        )
        self.lbl_subtitle.pack(pady=(0, 4))

        self.lbl_wallet_overlay = ctk.CTkLabel(
            self.inner_frame,
            text="กระเป๋า: ---",
            font=("Kanit", 12, "bold"),
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
        lbl_time_cap = ctk.CTkLabel(
            time_col, text="TIME",
            font=("Kanit", 9, "bold"), text_color=COLOR_TEXT_SUB,
        )
        lbl_time_cap.pack(anchor="w")
        self.lbl_time_overlay = ctk.CTkLabel(
            time_col, text="00:00:00",
            font=("Impact", 17), text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_time_overlay.pack(anchor="w")

        rate_col = ctk.CTkFrame(stats_frame, fg_color="transparent")
        rate_col.grid(row=0, column=1, sticky="nsew", padx=10, pady=6)
        lbl_rate_cap = ctk.CTkLabel(
            rate_col, text="RATE",
            font=("Kanit", 9, "bold"), text_color=COLOR_TEXT_SUB,
        )
        lbl_rate_cap.pack(anchor="e")
        self.lbl_mhr_overlay = ctk.CTkLabel(
            rate_col, text="0 /hr",
            font=("Impact", 17), text_color=COLOR_PINK_ACCENT,
        )
        self.lbl_mhr_overlay.pack(anchor="e")

        self._make_draggable(
            stats_frame, time_col, rate_col,
            lbl_time_cap, lbl_rate_cap,
            self.lbl_time_overlay, self.lbl_mhr_overlay,
        )

    def _build_item_list(self):
        head = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(0, 2))
        lbl_drops = ctk.CTkLabel(
            head, text="DROPS",
            font=("Kanit", 10, "bold"), text_color=COLOR_TEXT_SUB,
        )
        lbl_drops.pack(side="left")
        self.lbl_filter_badge = ctk.CTkLabel(
            head, text="",
            font=("Kanit", 10, "bold"), text_color=COLOR_WATCHLIST,
        )
        self.lbl_filter_badge.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(
            self.inner_frame, fg_color="transparent", corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.empty_label = ctk.CTkLabel(
            self.list_frame, text="รอของเข้า…",
            font=("Kanit", 12), text_color=COLOR_TEXT_SUB,
        )

        self._make_draggable(head, lbl_drops, self.lbl_filter_badge)

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
                self.lbl_wallet_overlay.configure(text=f"กระเป๋า: {wallet:,}")
            else:
                self.lbl_wallet_overlay.configure(text="กระเป๋า: ---")

            duration = 0
            first = getattr(self.controller, "first_drop_time", None)
            if first is not None:
                duration = max(0, time.time() - first)

            self.lbl_time_overlay.configure(text=_format_duration(duration))

            rate = (session / duration) * 3600 if (duration >= 1 and session > 0) else 0
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

        if filter_enabled and watchlist:
            wl_lower = [w.lower() for w in watchlist]
            filtered = {
                k: v for k, v in snapshot.items()
                if any(w in k.lower() for w in wl_lower)
            }
        else:
            filtered = snapshot

        if keyword:
            filtered = {k: v for k, v in filtered.items() if keyword in k.lower()}

        items = sorted(filtered.items(), key=lambda kv: kv[1], reverse=True)[: self.MAX_ITEMS]
        return items, filter_enabled

    def redraw_items(self):
        items, filter_enabled = self._filtered_items()

        self.lbl_filter_badge.configure(text="● FOCUS" if filter_enabled else "")

        for row in self.item_rows:
            row["frame"].pack_forget()
        self.empty_label.pack_forget()

        if not items:
            self.empty_label.configure(
                text="🔎 Focus Mode" if filter_enabled else "รอของเข้า…"
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

    def _make_row(self):
        frame = ctk.CTkFrame(self.list_frame, fg_color="transparent",
                             height=24, corner_radius=6)
        idx = ctk.CTkLabel(frame, text="", width=24,
                           font=("Kanit", 10, "bold"),
                           text_color=COLOR_TEXT_SUB)
        idx.pack(side="left")
        name = ctk.CTkLabel(frame, text="", font=("Kanit", 11),
                            anchor="w", justify="left",
                            text_color=COLOR_TEXT_MAIN)
        name.pack(side="left", padx=2, fill="x", expand=True)
        count = ctk.CTkLabel(frame, text="", font=("Kanit", 11, "bold"),
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

    def start_move(self, event):
        self._drag_offset_x = event.x_root - self.winfo_x()
        self._drag_offset_y = event.y_root - self.winfo_y()

    def do_move(self, event):
        x = event.x_root - self._drag_offset_x
        y = event.y_root - self._drag_offset_y
        self.geometry(f"+{x}+{y}")
