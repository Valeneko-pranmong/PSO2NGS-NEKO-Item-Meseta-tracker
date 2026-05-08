import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os
import time
import threading
import re
import json
import ctypes
import webbrowser
from PIL import Image

from config import * 
from dashboard_ui import DashboardFrame 
from overlay_ui import OverlayWindow

try:
    myappid = 'neko.family.shop.tracker.v5.7.4.offline' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

APP_VERSION = "V 6.1.0" 

app_data_dir = os.getenv('APPDATA') 
config_dir = os.path.join(app_data_dir, "NekoTrackerOffline") 
if not os.path.exists(config_dir):
    try: os.makedirs(config_dir) 
    except: pass
CONFIG_FILE = os.path.join(config_dir, "ngs_tracker_config.json")

class NGSTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.overrideredirect(True) 
        self.geometry("950x620")
        self.title("NEKO Item & Meseta Tracker (Offline)") 
        self.configure(fg_color=COLOR_BG_MAIN) 
        self.setup_icon()
        
        self.after(200, self.force_taskbar_icon)

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
        
        self.needs_ui_update = False 

        self.main_container = ctk.CTkFrame(self, fg_color=COLOR_PINK_HEADER, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        self.build_title_bar()

        self.sidebar = ctk.CTkFrame(self.main_container, width=280, corner_radius=0, fg_color=COLOR_BG_MAIN)
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=(0, 10))
        
        self.load_logo()
        self.design_brand_text()

        self.btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.btn_frame.pack(fill="both", expand=True, padx=20)

        BTN_HEIGHT = 35
        BTN_RADIUS = UI_RADIUS 

        self.btn_reset = ctk.CTkButton(self.btn_frame, text="เริ่มนับใหม่ (Reset)", font=("Kanit", 13,),
                                       fg_color=COLOR_PINK_HEADER, text_color=COLOR_TEXT_MAIN,
                                       hover_color=COLOR_PINK_SOFT, height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=self.confirm_reset)
        self.btn_reset.pack(pady=(0, 8), fill="x")

        self.btn_watchlist = ctk.CTkButton(self.btn_frame, text="Edit Watch List", font=("Kanit", 13, "bold"), 
                                           fg_color=COLOR_WATCHLIST, hover_color="#D81B60", text_color="white", 
                                           height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=self.open_watchlist_editor)
        self.btn_watchlist.pack(pady=(0, 5), fill="x")

        self.switch_filter = ctk.CTkSwitch(self.btn_frame, text="เปิดใช้ Watch List Filter", font=("Kanit", 11, "bold"),
                                           progress_color=COLOR_WATCHLIST, command=self.toggle_filter)
        self.switch_filter.pack(pady=(5, 10))

        row3 = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 8))
        row3.columnconfigure((0, 1), weight=1, uniform="equal")

        self.btn_overlay_full = ctk.CTkButton(row3, text="Item & Meseta", font=("Kanit", 12, "bold"), 
                                         fg_color=COLOR_PINK_ACCENT, hover_color="#FF1493", text_color="white", 
                                         height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=lambda: self.open_overlay("full"))
        self.btn_overlay_full.grid(row=0, column=0, sticky="ew", padx=(0, 3))

        self.btn_overlay_mini = ctk.CTkButton(row3, text="Meseta", font=("Kanit", 12, "bold"), 
                                         fg_color="#F06292", hover_color="#D81B60", text_color="white", 
                                         height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=lambda: self.open_overlay("mini"))
        self.btn_overlay_mini.grid(row=0, column=1, sticky="ew", padx=(3, 0))

        self.btn_discord = ctk.CTkButton(self.btn_frame, text="DISCORD NEKO FAMILY", font=("Kanit", 13, "bold"), 
                                         fg_color=COLOR_DISCORD, hover_color="#AB47BC", text_color="white", 
                                         height=BTN_HEIGHT, corner_radius=BTN_RADIUS, command=self.open_discord)
        self.btn_discord.pack(fill="x", pady=(0, 8))
        
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.status_frame.pack(side="bottom", fill="x", pady=(10, 5), padx=15)
        
        self.lbl_file_status = ctk.CTkLabel(self.status_frame, text="ยังไม่เลือกโฟลเดอร์ Log", text_color=COLOR_TEXT_SUB, wraplength=220, font=("Kanit", 11))
        self.lbl_file_status.pack(anchor="w", pady=(0, 3))
        
        self.btn_select = ctk.CTkButton(self.status_frame, text="📂 จิ้มเลือกโฟลเดอร์ Log", font=("Kanit", 12), 
                                        fg_color="#F0F0F0", text_color="#333333", hover_color="#E0E0E0", 
                                        height=30, corner_radius=UI_RADIUS, command=self.select_log_folder)
        self.btn_select.pack(fill="x")

        self.lbl_version = ctk.CTkLabel(self.sidebar, text=APP_VERSION, font=("Arial", 9), text_color="gray")
        self.lbl_version.pack(side="bottom", pady=(0, 5))

        self.dashboard_area = DashboardFrame(self.main_container, self)
        self.dashboard_area.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(0, 10))

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
            except: pass
            self.pending_status_text = None

        if getattr(self, 'needs_ui_update', False):
            try:
                self.dashboard_area.update_display()
                if getattr(self, 'overlay_window', None) and self.overlay_window.winfo_exists():
                    self.overlay_window.update_data()
            except: pass
            self.needs_ui_update = False 

        if self.first_drop_time is not None:
            try: 
                self.dashboard_area.update_live_stats()
                if getattr(self, 'overlay_window', None) and self.overlay_window.winfo_exists():
                    self.overlay_window.update_data()
            except: pass
            
        self.after(1000, self.update_live_clock)

    def setup_icon(self):
        try:
            if os.path.exists(ICON_FILENAME):
                self.iconbitmap(default=ICON_FILENAME)
        except: pass

    def build_title_bar(self):
        self.title_bar = ctk.CTkFrame(self.main_container, height=40, corner_radius=0, fg_color="transparent")
        self.title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        if os.path.exists(ICON_FILENAME):
            try:
                icon_image = ctk.CTkImage(Image.open(ICON_FILENAME), size=(20, 20))
                icon_lbl = ctk.CTkLabel(self.title_bar, text="", image=icon_image)
                icon_lbl.pack(side="left", padx=(15, 5), pady=5)
                icon_lbl.bind("<ButtonPress-1>", self.start_move)
                icon_lbl.bind("<B1-Motion>", self.do_move)
            except: pass

        title_text = "NEKO FAMILY TEAM SHOP - Item & Meseta tracker"
        title_label = ctk.CTkLabel(self.title_bar, text=title_text, font=("Kanit", 15, "bold"), text_color="white")
        title_label.pack(side="left", padx=5, pady=5)

        close_btn = ctk.CTkButton(self.title_bar, text="✕", width=30, height=30, corner_radius=0,
                                  fg_color="white", text_color="#D81B60", hover_color="#FFE4E1",
                                  font=("Arial", 14, "bold"), command=self.on_close)
        close_btn.pack(side="right", padx=(0, 15), pady=5)

        min_btn = ctk.CTkButton(self.title_bar, text="─", width=30, height=30, corner_radius=0,
                                fg_color="white", text_color="#D81B60", hover_color="#FFE4E1",
                                font=("Arial", 14, "bold"), command=self.minimize_window)
        min_btn.pack(side="right", padx=(0, 5), pady=5)

        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        title_label.bind("<ButtonPress-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.do_move)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = self.winfo_x() + (event.x - self.x)
        y = self.winfo_y() + (event.y - self.y)
        self.geometry(f"+{x}+{y}")

    def minimize_window(self):
        self.overrideredirect(False)
        self.iconify()
        self.bind("<Map>", self._on_restore_window)

    def _on_restore_window(self, event=None):
        self.overrideredirect(True)
        try: self.unbind("<Map>")
        except: pass
            
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
        ctk.CTkLabel(title_bar, text="ยืนยันรีเซ็ต", font=("Kanit", 13, "bold"), text_color="#333333").pack(side="left", padx=15, pady=5)

        ctk.CTkLabel(dlg, text="ต้องการรีเซ็ตข้อมูลรอบนี้?\nยอดเงิน เวลา และไอเทมทั้งหมดจะหายไป",
                     font=("Kanit", 12), text_color=COLOR_TEXT_MAIN, justify="center").pack(pady=(20, 15), padx=20)

        btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 15))
        btn_frame.columnconfigure((0, 1), weight=1, uniform="equal")

        def do_confirm():
            dlg.destroy()
            self.reset_data()

        ctk.CTkButton(btn_frame, text="ยกเลิก", font=("Kanit", 12),
                      fg_color="#F0F0F0", text_color="#333333", hover_color="#E0E0E0",
                      height=35, corner_radius=UI_RADIUS,
                      command=dlg.destroy).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        ctk.CTkButton(btn_frame, text="ยืนยันรีเซ็ต", font=("Kanit", 12, "bold"),
                      fg_color=COLOR_PINK_ACCENT, hover_color="#D81B60", text_color="white",
                      height=35, corner_radius=UI_RADIUS,
                      command=do_confirm).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        try: dlg.grab_set()
        except: pass

    def reset_data(self):
        with self.data_lock:
            self.session_meseta = 0
            self.current_wallet = 0
            self.item_counts = {}
            self.first_drop_time = None
            self.last_income_time = None
        
        if self.log_path and os.path.exists(self.log_path):
            try:
                with open(self.log_path, 'r', encoding=self.active_encoding, errors='replace') as f:
                    f.seek(0, 2)
                    self.last_file_pos = f.tell()
            except: pass
        self.trigger_update_ui()

    def on_close(self):
        self.is_running = False
        self.stop_event.set()
        try: self.destroy()
        except: pass
        os._exit(0)

    def open_discord(self):
        webbrowser.open("https://discord.gg/fkjXW9AJ6a")

    def toggle_filter(self):
        self.is_filter_active = bool(self.switch_filter.get())
        self.trigger_update_ui()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.watchlist_items = data.get("watchlist", [])
                    self.log_folder = data.get("log_folder", "")
            except: pass
            
        if self.log_folder and os.path.exists(self.log_folder): 
            self.find_latest_log_file()
        else: 
            self.lbl_file_status.configure(text="ยังไม่ได้ระบุโฟลเดอร์ Log", text_color="red")

    def save_settings(self):
        data = {
            "watchlist": self.watchlist_items,
            "log_folder": self.log_folder
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4) 
        except: pass

    def select_log_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
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
        except: return 
        
        if not target_files:
            self.pending_status_text = "หาไฟล์ Log ไม่เจออะ"
            self.pending_status_color = "red"
            return

        latest_file = max(target_files, key=os.path.getmtime)
        if latest_file != self.log_path:
            self.log_path = latest_file
            self.pending_status_text = f"กำลังอ่านไฟล์: {os.path.basename(latest_file)}"
            self.pending_status_color = COLOR_TEXT_VAL
            self.detect_encoding(self.log_path)
            self.reset_data() 

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
                except: pass

            title_label = ctk.CTkLabel(title_bar, text="Watch List Editor", font=("Kanit", 14, "bold"), text_color="#333333")
            title_label.pack(side="left", padx=5, pady=5)

            close_btn = ctk.CTkButton(title_bar, text="✕", width=30, height=30, corner_radius=0,
                                      fg_color="transparent", text_color="#D81B60", hover_color="#FFE4E1",
                                      font=("Arial", 14, "bold"), command=self.watchlist_window.destroy)
            close_btn.pack(side="right", padx=15, pady=5)

            def start_move(event):
                self.watchlist_window.x = event.x
                self.watchlist_window.y = event.y
            def do_move(event):
                x = self.watchlist_window.winfo_x() + (event.x - self.watchlist_window.x)
                y = self.watchlist_window.winfo_y() + (event.y - self.watchlist_window.y)
                self.watchlist_window.geometry(f"+{x}+{y}")

            title_bar.bind("<ButtonPress-1>", start_move)
            title_bar.bind("<B1-Motion>", do_move)
            title_label.bind("<ButtonPress-1>", start_move)
            title_label.bind("<B1-Motion>", do_move)

            ctk.CTkLabel(self.watchlist_window, text="ใส่ชื่อไอเท็มที่ต้องการโฟกัส (บรรทัดละ 1 ชื่อ)", font=("Kanit", 14, "bold"), text_color=COLOR_TEXT_MAIN).pack(pady=(15, 5))
            
            self.txt_watchlist = ctk.CTkTextbox(self.watchlist_window, font=("Kanit", 12), border_color=COLOR_PINK_HEADER, border_width=2, corner_radius=5, fg_color="white", text_color="#333333")
            self.txt_watchlist.pack(fill="both", expand=True, padx=20, pady=10)
            self.txt_watchlist.insert("0.0", "\n".join(self.watchlist_items))
            
            ctk.CTkButton(self.watchlist_window, text="บันทึก (Save Config)", font=("Kanit", 14, "bold"), fg_color=COLOR_PINK_ACCENT, hover_color="#D81B60", text_color="white", corner_radius=5, height=40, command=self.save_watchlist_from_editor).pack(pady=(5, 15), padx=20, fill="x")
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
            except: pass

    def design_brand_text(self):
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(pady=(0, 10))
        ctk.CTkLabel(brand_frame, text="ITEM & MESETA", font=("Kanit", 16), text_color=COLOR_PINK_HEADER).pack()
        ctk.CTkLabel(brand_frame, text="TRACKER", font=("Kanit", 26), text_color=COLOR_PINK_ACCENT).pack(pady=(0,2))
        
        separator = ctk.CTkFrame(brand_frame, height=2, fg_color=COLOR_PINK_HEADER)
        separator.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(brand_frame, text="CREATED BY", font=("Kanit", 10, "bold"), text_color=COLOR_TEXT_VAL).pack(pady=(2,0))
        ctk.CTkLabel(brand_frame, text="TEAM NEKO FAMILY SHIP 4 TH", font=("Kanit", 12, "bold"), text_color=COLOR_TEXT_VAL).pack()

    def detect_encoding(self, filepath):
        try:
            with open(filepath, 'rb') as f: raw = f.read(4)
            if raw.startswith(b'\xff\xfe'): self.active_encoding = 'utf-16'
            elif raw.startswith(b'\xfe\xff'): self.active_encoding = 'utf-16-be'
            elif raw.startswith(b'\xef\xbb\xbf'): self.active_encoding = 'utf-8-sig'
            else: self.active_encoding = 'utf-8'
        except: self.active_encoding = 'utf-16'

    def monitor_log_file(self):
        while not self.stop_event.is_set():
            if not self.is_running: break
            if self.log_folder: 
                try: self.find_latest_log_file()
                except: pass
            
            if self.log_path and os.path.exists(self.log_path):
                try:
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
                except: pass
            time.sleep(1)

    def process_log_line(self, line):
        try:
            meseta_match = re.search(r'\t(?:N-)?Meseta\s*\(\s*(\d+)\s*\)', line, re.IGNORECASE)
            wallet_match = re.search(r'\tCurrent(?:N-)?Meseta\s*\(\s*(\d+)\s*\)', line, re.IGNORECASE)

            raw_valid_action = ("[Pickup]" in line or "[AutoSell]" in line or "[Reward]" in line or "[Clear]" in line)
            
            if not raw_valid_action and wallet_match:
                if "[" not in line: 
                    raw_valid_action = True

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
                    if self.first_drop_time is None: self.first_drop_time = time.time()
                    self.session_meseta += income
                    self.last_income_time = time.time()

            if raw_valid_action and not meseta_match and "Num(" in line:
                item_pattern = r'\t([^\t]+)\tNum\((\d+)\)'
                match = re.search(item_pattern, line)
                if match:
                    item_name = match.group(1).strip()
                    count = int(match.group(2))
                    if item_name:
                        self.item_counts[item_name] = self.item_counts.get(item_name, 0) + count

        except: pass

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
        except: pass

    def summon_main_window(self):
        self.deiconify()
        self.attributes("-topmost", True)
        self.attributes("-topmost", False)
        self.lift()
        self.focus_force()

if __name__ == "__main__":
    app = NGSTrackerApp()
    app.mainloop()