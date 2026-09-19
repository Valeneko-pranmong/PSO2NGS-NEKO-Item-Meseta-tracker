from __future__ import annotations

import os
import sys
import tkinter as tk
from typing import Any, Callable, Optional
import customtkinter as ctk
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config import (
    COLOR_BG_MAIN,
    COLOR_PINK_HEADER,
    COLOR_PINK_ACCENT,
    COLOR_PINK_SOFT,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_SUB,
    COLOR_TEXT_VAL,
    UI_RADIUS,
    FONT_FAMILY,
    FONT_TITLE,
    FONT_HEADER,
    FONT_SUBHEADER,
    FONT_NORMAL,
    FONT_SMALL,
    LOGO_FILENAME,
    ICON_FILENAME,
)

try:
    from .auth_service import AuthService
except (ImportError, ValueError):
    from modules.auth.auth_service import AuthService

TEAM_OPTIONS = []


class AuthFrame(ctk.CTkFrame):
    """
    Authentication & Operative Identity Screen for ARKS War Room.
    - Pre-login mode: Neko Family Supabase Account authentication only.
    - Post-login mode ("หลัง login"): ARKS Operative Identity & Callsign/Faction selection.
    """

    def __init__(
        self,
        parent: Any,
        controller: Any,
        auth_service: AuthService,
        initial_mode: str = "auto",
    ) -> None:
        super().__init__(parent, fg_color=COLOR_BG_MAIN, corner_radius=0)
        self.controller = controller
        self.auth_service = auth_service
        self.mode = "login"

        self._build_ui()
        self.set_mode(initial_mode)

    def set_mode(self, mode: str) -> None:
        """Switch view mode between 'login' and 'identity' (post-login)."""
        if mode == "auto":
            mode = "identity" if self.auth_service.is_logged_in() else "login"
        elif mode == "identity" and not self.auth_service.is_logged_in():
            mode = "login"

        self.mode = mode
        self.lbl_status.configure(text="")
        self._render()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.center_card = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=UI_RADIUS + 4,
            border_width=2,
            border_color=COLOR_PINK_HEADER,
            width=520,
        )
        self.center_card.grid(row=0, column=0, padx=40, pady=30, sticky="n")

        # Top Badge / Header inside card
        self.header_frame = ctk.CTkFrame(self.center_card, fg_color=COLOR_PINK_SOFT, corner_radius=UI_RADIUS, height=80)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 10))
        self.header_frame.pack_propagate(False)

        top_inner = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        top_inner.pack(expand=True)

        self.lbl_badge = ctk.CTkLabel(
            top_inner,
            text="",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLOR_TEXT_VAL,
        )
        self.lbl_badge.pack()

        self.lbl_title = ctk.CTkLabel(
            top_inner,
            text="",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLOR_TEXT_MAIN,
        )
        self.lbl_title.pack(pady=(2, 0))

        # Dynamic Content Frame
        self.content_frame = ctk.CTkFrame(self.center_card, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=25, pady=(5, 10))

        # Status Message Label
        self.lbl_status = ctk.CTkLabel(
            self.center_card,
            text="",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_VAL,
            wraplength=450,
        )
        self.lbl_status.pack(pady=(0, 8))

        # Bottom Action Bar
        self.bottom_frame = ctk.CTkFrame(self.center_card, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=25, pady=(0, 20))

    def _render(self) -> None:
        if hasattr(self, "opt_team"):
            try:
                delattr(self, "opt_team")
            except Exception:
                pass
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        if self.mode == "login":
            self._render_login_view()
        else:
            self._render_identity_view()

    def _render_login_view(self) -> None:
        self.lbl_badge.configure(text="🔐 NEKO FAMILY — ARKS WAR ROOM")
        self.lbl_title.configure(text="เข้าสู่ระบบสมาชิก Neko Family")

        ctk.CTkLabel(
            self.content_frame,
            text="กรุณาเข้าสู่ระบบด้วยบัญชี Neko เพื่อยืนยันสิทธิ์สมาชิกทีมและเชื่อมต่อระบบสงคราม",
            font=(FONT_FAMILY, 12),
            text_color="#666666",
            wraplength=450,
        ).pack(anchor="w", pady=(0, 12))

        ctk.CTkLabel(
            self.content_frame,
            text="ชื่อผู้ใช้ (Username):",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXT_MAIN,
        ).pack(anchor="w")

        self.entry_username = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="กรอกชื่อผู้ใช้ Neko Launcher",
            height=38,
            font=(FONT_FAMILY, 13),
            border_color=COLOR_PINK_HEADER,
            fg_color="#FAFAFA",
            text_color=COLOR_TEXT_MAIN,
        )
        self.entry_username.pack(fill="x", pady=(4, 10))
        self.entry_username.bind("<Return>", lambda e: self._handle_account_login())

        ctk.CTkLabel(
            self.content_frame,
            text="รหัสผ่าน (Password):",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLOR_TEXT_MAIN,
        ).pack(anchor="w")

        self.entry_password = ctk.CTkEntry(
            self.content_frame,
            placeholder_text="●●●●●●●●",
            show="●",
            height=38,
            font=(FONT_FAMILY, 13),
            border_color=COLOR_PINK_HEADER,
            fg_color="#FAFAFA",
            text_color=COLOR_TEXT_MAIN,
        )
        self.entry_password.pack(fill="x", pady=(4, 15))
        self.entry_password.bind("<Return>", lambda e: self._handle_account_login())

        self.btn_submit_login = ctk.CTkButton(
            self.content_frame,
            text="🔑 เข้าสู่ระบบ & ดำเนินการต่อ",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLOR_PINK_ACCENT,
            hover_color="#D81B60",
            text_color="white",
            height=40,
            corner_radius=UI_RADIUS,
            command=self._handle_account_login,
        )
        self.btn_submit_login.pack(fill="x", pady=(5, 5))

        # Bottom
        btn_back = ctk.CTkButton(
            self.bottom_frame,
            text="🔙 กลับสู่โหมดออฟไลน์ (Offline Mode)",
            font=(FONT_FAMILY, 12),
            fg_color="#F3F4F6",
            text_color="#4B5563",
            hover_color="#E5E7EB",
            height=36,
            corner_radius=UI_RADIUS,
            command=self.controller.show_offline_view,
        )
        btn_back.pack(fill="x")

    def _refresh_team_options(self, selected_team_id: Optional[str] = None) -> None:
        self.all_team_options = []
        self.current_team_options = []

    def _apply_team_filter(self, selected_team_id: Optional[str] = None) -> None:
        pass

    def _on_team_search_changed(self, *args) -> None:
        pass

    def _clear_team_search(self) -> None:
        pass

    def _handle_open_create_team_dialog(self) -> None:
        pass

    def _render_identity_view(self) -> None:
        user = self.auth_service.get_current_user() or {}
        username = user.get("username", "Member")
        char_name = ""
        if hasattr(self.controller, "ensure_character_from_log"):
            char_name = self.controller.ensure_character_from_log()
        if not char_name:
            char_name = getattr(self.controller, "character_name", "") or user.get("character_name") or user.get("callsign") or username

        self.lbl_badge.configure(text="⚡ ARKS WAR ROOM — ข้อมูลสมาชิก")
        self.lbl_title.configure(text="เข้าสู่ระบบสมาชิกสำเร็จ")

        # Account status card
        acc_box = ctk.CTkFrame(self.content_frame, fg_color="#F0FDF4", corner_radius=UI_RADIUS - 2, border_width=1, border_color="#BBF7D0")
        acc_box.pack(fill="x", pady=(0, 12), ipady=6)
        ctk.CTkLabel(
            acc_box,
            text=f"👤 เข้าสู่ระบบในชื่อ: {username}\n🎮 ชื่อในเกม (จาก Log): {char_name}",
            font=(FONT_FAMILY, 12, "bold"),
            text_color="#166534",
            justify="left",
        ).pack(padx=12, pady=4, anchor="w")

        # Database notice badge
        notice_box = ctk.CTkFrame(self.content_frame, fg_color="#F8FAFC", corner_radius=UI_RADIUS - 2, border_width=1, border_color="#E2E8F0")
        notice_box.pack(fill="x", pady=(0, 16), ipady=6)
        ctk.CTkLabel(
            notice_box,
            text="ℹ️ ข้อมูลที่ส่งขึ้นฐานข้อมูล: [ชื่อในเกม (จาก Log)] • [ยอด Meseta แบบเรียลไทม์]\n(ตัดระบบทีมออกแล้ว ส่งเฉพาะชื่อในเกมและเงินที่ทำได้แบบเรียลไทม์)",
            font=(FONT_FAMILY, 11),
            text_color=COLOR_TEXT_SUB,
            justify="left",
        ).pack(padx=12, pady=4, anchor="w")

        self.btn_submit_callsign = ctk.CTkButton(
            self.content_frame,
            text="⚡ เข้าสู่ระบบ Realtime & เริ่มต้นทำงาน",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            text_color="white",
            height=42,
            corner_radius=UI_RADIUS,
            command=self._handle_identity_save,
        )
        self.btn_submit_callsign.pack(fill="x", pady=(0, 5))

        # Bottom
        btn_back = ctk.CTkButton(
            self.bottom_frame,
            text="🔙 กลับสู่โหมดออฟไลน์ (Offline Mode)",
            font=(FONT_FAMILY, 12),
            fg_color="#F3F4F6",
            text_color="#4B5563",
            hover_color="#E5E7EB",
            height=36,
            corner_radius=UI_RADIUS,
            command=self.controller.show_offline_view,
        )
        btn_back.pack(fill="x", pady=(0, 6))

        btn_logout = ctk.CTkButton(
            self.bottom_frame,
            text="🚪 ออกจากระบบ / สลับบัญชี (Sign Out)",
            font=(FONT_FAMILY, 11),
            fg_color="transparent",
            text_color="#DC2626",
            hover_color="#FEE2E2",
            height=28,
            corner_radius=UI_RADIUS,
            command=self._handle_logout,
        )
        btn_logout.pack()

    def _handle_account_login(self) -> None:
        user = self.entry_username.get().strip()
        pwd = self.entry_password.get().strip()

        self.lbl_status.configure(text="กำลังตรวจสอบข้อมูลกับเซิร์ฟเวอร์...", text_color=COLOR_TEXT_SUB)
        self.update_idletasks()

        success, msg = self.auth_service.sign_in(user, pwd)
        if success:
            self.lbl_status.configure(text=f"✓ {msg}", text_color="#10B981")
            char_name = ""
            if hasattr(self.controller, "ensure_character_from_log"):
                char_name = self.controller.ensure_character_from_log()
            if not char_name:
                char_name = getattr(self.controller, "character_name", "") or user

            self.auth_service.save_operative_profile(char_name)
            meseta = getattr(self.controller, "session_meseta", 0)
            self.auth_service.save_meseta_to_database(char_name, meseta)

            if hasattr(self.controller, "war_service"):
                self.controller.war_service.set_operative(char_name)
                self.controller.war_service.sync_to_war_room()

            self.after(350, self.controller.on_auth_success)
        else:
            self.lbl_status.configure(text=f"❌ {msg}", text_color="#EF4444")

    def _handle_identity_save(self) -> None:
        char_name = ""
        if hasattr(self.controller, "ensure_character_from_log"):
            char_name = self.controller.ensure_character_from_log()
        if not char_name:
            char_name = getattr(self.controller, "character_name", "")

        user = self.auth_service.get_current_user() or {}
        if not char_name:
            char_name = user.get("character_name") or user.get("callsign") or user.get("username") or "Operative"

        success, msg = self.auth_service.save_operative_profile(char_name)
        if success:
            meseta = getattr(self.controller, "session_meseta", 0)
            self.auth_service.save_meseta_to_database(char_name, meseta)

            if hasattr(self.controller, "war_service"):
                self.controller.war_service.set_operative(char_name)
                self.controller.war_service.sync_to_war_room()

            self.lbl_status.configure(text=f"✓ บันทึกข้อมูล {char_name} เรียบร้อย!", text_color="#10B981")
            self.after(350, self.controller.on_auth_success)
        else:
            self.lbl_status.configure(text=f"❌ {msg}", text_color="#EF4444")

    def _handle_logout(self) -> None:
        self.auth_service.sign_out()
        self.set_mode("login")


if __name__ == "__main__":
    print("=" * 60)
    print("🔐  NEKO Tracker — AuthView Standalone Launcher")
    print("=" * 60)
    root = ctk.CTk()
    root.geometry("620x580")
    root.title("NEKO Tracker - Auth Test")
    auth_srv = AuthService()

    class DummyCtrl:
        def on_auth_success(self):
            print(" [✓] Auth success callback received!")
        def show_offline_view(self):
            print(" [✓] Back to offline clicked!")
            root.destroy()

    view = AuthFrame(root, DummyCtrl(), auth_srv)
    view.pack(fill="both", expand=True)
    root.mainloop()
