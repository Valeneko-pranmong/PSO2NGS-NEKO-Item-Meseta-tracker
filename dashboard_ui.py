import customtkinter as ctk
import tkinter as tk
import time
from config import *
from modules.utils import format_duration, format_rate, filter_and_sort_items, calculate_live_rate
from modules.i18n import t
from modules.event_bus import event_bus

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG_MAIN, corner_radius=0) 
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.content_container.grid_rowconfigure(3, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        self.money_card = ctk.CTkFrame(self.content_container, fg_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS)
        self.money_card.grid(row=0, column=0, sticky="ew", pady=(8, 5), padx=15)
        self.money_card.columnconfigure((0,1), weight=1)
        
        session_frame = ctk.CTkFrame(self.money_card, fg_color="transparent")
        session_frame.grid(row=0, column=0, pady=8)
        
        self.lbl_session_title = ctk.CTkLabel(session_frame, text=t("lbl_session"), font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SUB)
        self.lbl_session_title.pack()
        self.lbl_session = ctk.CTkLabel(session_frame, text="+0", font=FONT_NUMBER, text_color=COLOR_TEXT_VAL)
        self.lbl_session.pack(pady=(0, 3))

        wallet_frame = ctk.CTkFrame(self.money_card, fg_color="transparent")
        wallet_frame.grid(row=0, column=1, pady=8)

        self.lbl_wallet_title = ctk.CTkLabel(wallet_frame, text=t("lbl_wallet"), font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SUB)
        self.lbl_wallet_title.pack()
        self.lbl_wallet = ctk.CTkLabel(wallet_frame, text="---", font=("Impact", 30), text_color=COLOR_TEXT_MAIN)
        self.lbl_wallet.pack(pady=(0, 3))

        self.stats_card = ctk.CTkFrame(self.content_container, fg_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS)
        self.stats_card.grid(row=1, column=0, sticky="ew", pady=(0, 8), padx=15)
        self.stats_card.columnconfigure((0,1), weight=1)

        time_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        time_frame.grid(row=0, column=0, pady=6)
        self.lbl_time_title = ctk.CTkLabel(time_frame, text=t("lbl_farming_time"), font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SUB)
        self.lbl_time_title.pack()
        self.lbl_time = ctk.CTkLabel(time_frame, text="00:00:00", font=FONT_STATS, text_color=COLOR_PINK_ACCENT)
        self.lbl_time.pack()

        mhr_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        mhr_frame.grid(row=0, column=1, pady=6)
        self.lbl_mhr_title = ctk.CTkLabel(mhr_frame, text=t("lbl_speed"), font=(FONT_FAMILY, 12), text_color=COLOR_TEXT_SUB)
        self.lbl_mhr_title.pack()
        self.lbl_mhr = ctk.CTkLabel(mhr_frame, text="0 /hr", font=FONT_STATS, text_color=COLOR_TEXT_VAL)
        self.lbl_mhr.pack()

        header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header_frame.grid(row=2, column=0, sticky="new", padx=20, pady=(4, 4))
        
        self.search_var = tk.StringVar(value=getattr(self.controller, "search_keyword", ""))
        self.search_var.trace_add("write", self.on_search_change)
        
        self.search_entry = ctk.CTkEntry(header_frame, placeholder_text=t("search_placeholder"), 
                                        textvariable=self.search_var, width=200, font=(FONT_FAMILY, 12), 
                                        border_color=COLOR_PINK_ACCENT, height=32, corner_radius=UI_RADIUS,
                                        fg_color="white", text_color=COLOR_TEXT_MAIN)
        self.search_entry.pack(side="right")

        self.lbl_drops_title = ctk.CTkLabel(header_frame, text=t("header_drops"), font=FONT_HEADER, text_color=COLOR_TEXT_MAIN)
        self.lbl_drops_title.pack(side="left")

        self.scroll = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent", label_text="", corner_radius=0)
        self.scroll.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.item_rows = []
        self.empty_msg_lbl = ctk.CTkLabel(self.scroll, text="", font=(FONT_FAMILY, 13), text_color=COLOR_TEXT_SUB)

        try:
            event_bus.subscribe("language_changed", self._on_language_changed)
        except Exception:
            pass

    def _on_language_changed(self, language: str = "", **kwargs) -> None:
        try:
            self.retranslate_ui()
        except Exception:
            pass

    def retranslate_ui(self) -> None:
        """Update all displayed text to current active language."""
        try:
            if hasattr(self, "lbl_session_title") and self.lbl_session_title.winfo_exists():
                self.lbl_session_title.configure(text=t("lbl_session"))
            if hasattr(self, "lbl_wallet_title") and self.lbl_wallet_title.winfo_exists():
                self.lbl_wallet_title.configure(text=t("lbl_wallet"))
            if hasattr(self, "lbl_time_title") and self.lbl_time_title.winfo_exists():
                self.lbl_time_title.configure(text=t("lbl_farming_time"))
            if hasattr(self, "lbl_mhr_title") and self.lbl_mhr_title.winfo_exists():
                self.lbl_mhr_title.configure(text=t("lbl_speed"))
            if hasattr(self, "search_entry") and self.search_entry.winfo_exists():
                self.search_entry.configure(placeholder_text=t("search_placeholder"))
            if hasattr(self, "lbl_drops_title") and self.lbl_drops_title.winfo_exists():
                self.lbl_drops_title.configure(text=t("header_drops"))
            self.update_display()
        except Exception:
            pass

    def on_search_change(self, *args):
        self.controller.search_keyword = self.search_var.get().strip().lower()
        self.controller.trigger_update_ui() 

    def update_live_stats(self):
        duration_secs = 0
        if hasattr(self.controller, 'first_drop_time') and self.controller.first_drop_time is not None:
            duration_secs = max(0, time.time() - self.controller.first_drop_time)

        self.lbl_time.configure(text=format_duration(duration_secs))

        if duration_secs >= 1 and self.controller.session_meseta > 0:
            m_hr = calculate_live_rate(self.controller.session_meseta, duration_secs, min_smoothing_seconds=30.0)
            m_hr_str = format_rate(m_hr)
        else:
            m_hr_str = "0 /hr"
        self.lbl_mhr.configure(text=m_hr_str)

    def update_display(self):
        self.lbl_session.configure(text=f"+{self.controller.session_meseta:,}")
        if self.controller.current_wallet > 0:
            self.lbl_wallet.configure(text=f"{self.controller.current_wallet:,}")
        else:
            self.lbl_wallet.configure(text="---")

        self.update_live_stats()

        try:
            with self.controller.data_lock:
                items_snapshot = self.controller.item_counts.copy()
            
            watchlist = self.controller.watchlist_items
            keyword = self.controller.search_keyword
            filter_enabled = self.controller.is_filter_active 

            sorted_items = filter_and_sort_items(
                items_snapshot,
                watchlist=watchlist,
                keyword=keyword,
                filter_enabled=filter_enabled,
                max_items=50,
            )
            
            
            if not sorted_items:
                msg = ""
                if keyword:
                    msg = t("empty_not_found", keyword=keyword)
                elif filter_enabled and watchlist:
                    msg = t("empty_watchlist_no_match")
                elif filter_enabled and not watchlist:
                    msg = t("empty_watchlist_empty")
                else:
                    msg = t("empty_waiting")
                
                self.empty_msg_lbl.configure(text=msg)
                self.empty_msg_lbl.pack(pady=20)
                
                
                for row_data in self.item_rows:
                    row_data[0].pack_forget()
            else:
                self.empty_msg_lbl.pack_forget() 
                
                for i, (n, c) in enumerate(sorted_items):
                    
                    if i >= len(self.item_rows):
                        bg_color = COLOR_BG_MAIN if i % 2 == 0 else COLOR_PINK_SOFT
                        row = ctk.CTkFrame(self.scroll, fg_color=bg_color, corner_radius=6, height=32)
                        rank_lbl = ctk.CTkLabel(row, text="", width=30, font=(FONT_FAMILY, 11, "bold"), text_color=COLOR_TEXT_SUB)
                        rank_lbl.pack(side="left", padx=5)
                        name_lbl = ctk.CTkLabel(row, text="", anchor="w", font=FONT_NORMAL, text_color=COLOR_TEXT_MAIN)
                        name_lbl.pack(side="left", fill="x", expand=True, padx=5)
                        count_lbl = ctk.CTkLabel(row, text="", font=FONT_SUBHEADER, text_color=COLOR_TEXT_VAL)
                        count_lbl.pack(side="right", padx=15)
                        
                        self.item_rows.append((row, rank_lbl, name_lbl, count_lbl))

                    
                    row, rank_lbl, name_lbl, count_lbl = self.item_rows[i]
                    rank_lbl.configure(text=f"{i+1}")
                    name_lbl.configure(text=n)
                    count_lbl.configure(text=f"x {c:,}")
                    
                    row.pack(fill="x", pady=2, padx=5) 

                
                for i in range(len(sorted_items), len(self.item_rows)):
                    self.item_rows[i][0].pack_forget()
        except tk.TclError:
            pass