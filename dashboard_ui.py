import customtkinter as ctk
import tkinter as tk
import time
from config import *

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
        self.money_card.grid(row=0, column=0, sticky="ew", pady=(15, 8), padx=15)
        self.money_card.columnconfigure((0,1), weight=1)
        
        session_frame = ctk.CTkFrame(self.money_card, fg_color="transparent")
        session_frame.grid(row=0, column=0, pady=15)
        
        ctk.CTkLabel(session_frame, text="ยอดเงินรอบนี้ (Session)", font=("Kanit", 13), text_color=COLOR_TEXT_SUB).pack()
        self.lbl_session = ctk.CTkLabel(session_frame, text="+0", font=FONT_NUMBER, text_color=COLOR_TEXT_VAL)
        self.lbl_session.pack(pady=(0, 5))

        wallet_frame = ctk.CTkFrame(self.money_card, fg_color="transparent")
        wallet_frame.grid(row=0, column=1, pady=15)

        ctk.CTkLabel(wallet_frame, text="เงินที่มีในกระเป๋า", font=("Kanit", 13), text_color=COLOR_TEXT_SUB).pack()
        self.lbl_wallet = ctk.CTkLabel(wallet_frame, text="---", font=("Impact", 32), text_color=COLOR_TEXT_MAIN)
        self.lbl_wallet.pack(pady=(0, 5))

        self.stats_card = ctk.CTkFrame(self.content_container, fg_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS)
        self.stats_card.grid(row=1, column=0, sticky="ew", pady=(0, 15), padx=15)
        self.stats_card.columnconfigure((0,1), weight=1)

        time_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        time_frame.grid(row=0, column=0, pady=12)
        ctk.CTkLabel(time_frame, text="เวลาที่ใช้ฟาร์ม", font=("Kanit", 13), text_color=COLOR_TEXT_SUB).pack()
        self.lbl_time = ctk.CTkLabel(time_frame, text="00:00:00", font=FONT_STATS, text_color=COLOR_PINK_ACCENT)
        self.lbl_time.pack()

        mhr_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        mhr_frame.grid(row=0, column=1, pady=12)
        ctk.CTkLabel(mhr_frame, text="ความเร็ว (M/hr)", font=("Kanit", 13), text_color=COLOR_TEXT_SUB).pack()
        self.lbl_mhr = ctk.CTkLabel(mhr_frame, text="0 /hr", font=FONT_STATS, text_color=COLOR_TEXT_VAL)
        self.lbl_mhr.pack()

        header_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        header_frame.grid(row=2, column=0, sticky="new", padx=20, pady=(5, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change) 
        
        search_entry = ctk.CTkEntry(header_frame, placeholder_text="🔍 ค้นหาไอเท็ม...", 
                                   textvariable=self.search_var, width=200, font=("Kanit", 12), 
                                   border_color=COLOR_PINK_ACCENT, height=32, corner_radius=UI_RADIUS,
                                   fg_color="white", text_color=COLOR_TEXT_MAIN)
        search_entry.pack(side="right")

        ctk.CTkLabel(header_frame, text="📦 รายการของที่ดรอป", font=FONT_HEADER, text_color=COLOR_TEXT_MAIN).pack(side="left")

        self.scroll = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent", label_text="", corner_radius=0)
        self.scroll.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))

        
        self.item_rows = []
        self.empty_msg_lbl = ctk.CTkLabel(self.scroll, text="", font=("Kanit", 13), text_color=COLOR_TEXT_SUB)

    def on_search_change(self, *args):
        self.controller.search_keyword = self.search_var.get().strip().lower()
        self.controller.trigger_update_ui() 

    def update_live_stats(self):
        duration_secs = 0
        if hasattr(self.controller, 'first_drop_time') and self.controller.first_drop_time is not None:
            duration_secs = time.time() - self.controller.first_drop_time
            
        if duration_secs < 0: duration_secs = 0
        
        hours = int(duration_secs // 3600)
        mins = int((duration_secs % 3600) // 60)
        secs = int(duration_secs % 60)
        self.lbl_time.configure(text=f"{hours:02d}:{mins:02d}:{secs:02d}")

        if duration_secs >= 1 and self.controller.session_meseta > 0:
            m_hr = (self.controller.session_meseta / duration_secs) * 3600
            if m_hr >= 1000000: m_hr_str = f"{m_hr/1000000:.2f} M/hr"
            elif m_hr >= 1000: m_hr_str = f"{m_hr/1000:.1f} k/hr"
            else: m_hr_str = f"{int(m_hr)} /hr"
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
                    if keyword in k.lower():
                        final_items[k] = v
            else:
                final_items = filtered_items

            sorted_items = sorted(final_items.items(), key=lambda x: x[1], reverse=True)[:50] 
            
            
            if not sorted_items:
                msg = ""
                if keyword: msg = f"ไม่พบ: {keyword}"
                elif filter_enabled and watchlist: msg = "ไม่พบไอเท็มใน Watch List"
                elif filter_enabled and not watchlist: msg = "Watch List ว่างเปล่า"
                else: msg = "รอของเข้า..."
                
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
                        rank_lbl = ctk.CTkLabel(row, text="", width=30, font=("Kanit", 11, "bold"), text_color=COLOR_TEXT_SUB)
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