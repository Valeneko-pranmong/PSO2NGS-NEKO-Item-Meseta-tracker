import customtkinter as ctk
from tkinter import ttk
import time
import os
from config import *

class OverlayWindow(ctk.CTkToplevel):
    def __init__(self, controller, mode="full"):
        super().__init__()
        self.controller = controller
        self.mode = mode 
        
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.90) 
        self.configure(fg_color=COLOR_BG_MAIN) 
        self.title("Gadget Mode - NEKO Tracker")

        if os.path.exists(ICON_FILENAME):
            try: 
                self.after(200, lambda: self.iconbitmap(ICON_FILENAME))
            except: pass

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight() 
        
        window_width = 280
        x_pos = screen_width - window_width - 10 
        
        target_height = int(screen_height * 0.80)
        y_pos = int(screen_height * 0.10)

        if self.mode == "full":
            self.geometry(f"{window_width}x{target_height}+{x_pos}+{y_pos}")
        else:
            self.geometry(f"{window_width}x200+{x_pos}+{y_pos}")

        self.last_item_update_time = 0
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<B1-Motion>", self.do_move)

        
        self.inner_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN, corner_radius=UI_RADIUS, border_width=2, border_color=COLOR_PINK_HEADER)
        self.inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        
        self.btn_close = ctk.CTkButton(self.inner_frame, text="×", width=25, height=25, font=("Arial", 16),
                                      fg_color="transparent", text_color=COLOR_TEXT_SUB, hover_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS, command=self.destroy)
        self.btn_close.place(relx=1.0, rely=0.0, anchor="ne", x=-5, y=5)

        self.btn_show_main = ctk.CTkButton(self.inner_frame, text="🏠", width=25, height=25, font=("Segoe UI Emoji", 12),
                                           fg_color="transparent", hover_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS, command=self.controller.summon_main_window)
        self.btn_show_main.place(relx=1.0, rely=0.0, anchor="ne", x=-35, y=5)

        
        self.lbl_money = ctk.CTkLabel(self.inner_frame, text="+0", font=("Impact", 32), text_color=COLOR_TEXT_VAL)
        self.lbl_money.pack(pady=(25, 0))
        ctk.CTkLabel(self.inner_frame, text="เงินรอบนี้ (Session)", font=("Kanit", 11), text_color=COLOR_TEXT_SUB).pack(pady=(0,5))

        self.lbl_wallet_overlay = ctk.CTkLabel(self.inner_frame, text="กระเป๋า: ---", font=("Kanit", 13, "bold"), text_color=COLOR_TEXT_MAIN)
        self.lbl_wallet_overlay.pack(pady=(0, 5))

        
        stats_frame = ctk.CTkFrame(self.inner_frame, fg_color=COLOR_PINK_SOFT, corner_radius=6)
        stats_frame.pack(fill="x", padx=15, pady=(5, 10))
        stats_frame.columnconfigure((0,1), weight=1)

        self.lbl_time_overlay = ctk.CTkLabel(stats_frame, text="00:00:00", font=("Impact", 16), text_color=COLOR_TEXT_SUB)
        self.lbl_time_overlay.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.lbl_mhr_overlay = ctk.CTkLabel(stats_frame, text="0 /hr", font=("Impact", 16), text_color=COLOR_PINK_ACCENT)
        self.lbl_mhr_overlay.grid(row=0, column=1, sticky="e", padx=10, pady=5)

        if self.mode == "full":
            self.list_frame = ctk.CTkScrollableFrame(self.inner_frame, fg_color="transparent", corner_radius=0)
            self.list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_data()

    def update_data(self):
        try:
            self.lbl_money.configure(text=f"+{self.controller.session_meseta:,}")
            w_val = self.controller.current_wallet
            if w_val > 0: self.lbl_wallet_overlay.configure(text=f"กระเป๋า: {w_val:,}")
            else: self.lbl_wallet_overlay.configure(text=f"กระเป๋า: {w_val:,}")

            duration_secs = 0
            if hasattr(self.controller, 'first_drop_time') and self.controller.first_drop_time is not None:
                duration_secs = time.time() - self.controller.first_drop_time
                
            if duration_secs < 0: duration_secs = 0
            
            hours = int(duration_secs // 3600)
            mins = int((duration_secs % 3600) // 60)
            secs = int(duration_secs % 60)
            self.lbl_time_overlay.configure(text=f"{hours:02d}:{mins:02d}:{secs:02d}")

            if duration_secs >= 1 and self.controller.session_meseta > 0:
                m_hr = (self.controller.session_meseta / duration_secs) * 3600
                if m_hr >= 1000000: m_hr_str = f"{m_hr/1000000:.2f} M/hr"
                elif m_hr >= 1000: m_hr_str = f"{m_hr/1000:.1f} k/hr"
                else: m_hr_str = f"{int(m_hr)} /hr"
            else:
                m_hr_str = "0 /hr"
            
            self.lbl_mhr_overlay.configure(text=m_hr_str)

            if self.mode == "full":
                current_time = time.time()
                if current_time - self.last_item_update_time >= 2:
                    self.last_item_update_time = current_time
                    self.redraw_items()
        except: pass

    def redraw_items(self):
        for w in self.list_frame.winfo_children(): w.destroy()
        with self.controller.data_lock:
            items_snapshot = self.controller.item_counts.copy()
        
        watchlist = self.controller.watchlist_items
        keyword = self.controller.search_keyword
        filter_enabled = self.controller.is_filter_active

        filtered_items = {}
        if filter_enabled and watchlist:
            for k, v in items_snapshot.items():
                for watch_item in watchlist:
                    if watch_item.lower() in k.lower():
                        filtered_items[k] = v
                        break
        else:
            filtered_items = items_snapshot

        final_items = {}
        if keyword:
            for k, v in filtered_items.items():
                if keyword in k:
                    final_items[k] = v
        else:
            final_items = filtered_items

        items = sorted(final_items.items(), key=lambda x: x[1], reverse=True)[:30]
        
        if not items:
            msg = "Focus Mode" if filter_enabled else "รอของเข้า..."
            ctk.CTkLabel(self.list_frame, text=msg, font=("Kanit", 12), text_color=COLOR_TEXT_SUB).pack(pady=20)
        else:
            for i, (name, count) in enumerate(items):
                row = ctk.CTkFrame(self.list_frame, fg_color="transparent", height=26, corner_radius=0)
                row.pack(fill="x", pady=1)
                ctk.CTkLabel(row, text=f"{i+1}.", width=20, font=("Kanit", 10, "bold"), text_color=COLOR_TEXT_SUB).pack(side="left")
                display_name = (name[:20] + '..') if len(name) > 20 else name
                ctk.CTkLabel(row, text=display_name, font=("Kanit", 11), anchor="w", text_color=COLOR_TEXT_MAIN).pack(side="left", padx=2)
                ctk.CTkLabel(row, text=f"x{count:,}", font=("Kanit", 11, "bold"), text_color=COLOR_PINK_ACCENT).pack(side="right", padx=5)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")