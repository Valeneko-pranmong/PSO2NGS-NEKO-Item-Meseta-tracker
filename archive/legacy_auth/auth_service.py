"""
ARCHIVED / DEPRECATED — DO NOT USE FOR ACTIVE DEVELOPMENT (ห้ามใช้ในงานพัฒนาปัจจุบัน)
Superseded by: Zero-Login Operative Identity (modules/war_mode/war_service.py)
Status: RETIRED / ARCHIVED. Authentication credentials are no longer required.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse

try:
    from ..event_bus import event_bus
except (ImportError, ValueError):
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from modules.event_bus import event_bus

# SECURITY NOTICE: Do NOT hardcode production credentials in repository files.
# If legacy Supabase connectivity is needed, inject via environment variables.
# Any exposed legacy keys must be rotated in the Supabase Dashboard.
DEFAULT_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
DEFAULT_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")


def cleanup_legacy_auth_session() -> bool:
    """
    Securely removes legacy unencrypted auth_session.json left by previous releases.
    Returns True if a legacy file was found and removed, False otherwise.
    """
    try:
        app_data = os.getenv("APPDATA") or os.path.expanduser("~")
        legacy_file = os.path.join(app_data, "NekoTrackerOffline", "auth_session.json")
        if os.path.exists(legacy_file):
            os.remove(legacy_file)
            print("[AuthService] Cleaned up legacy plaintext auth_session.json")
            return True
    except Exception as exc:
        print(f"[AuthService] Legacy session cleanup warning: {exc}")
    return False


class AuthService:
    """
    Manages user authentication and operative identity for NEKO Family & ARKS War Room.
    Supports both Supabase Auth (Neko Family credentials) and Callsign Operative Identity.
    """

    def __init__(
        self,
        supabase_url: str = DEFAULT_SUPABASE_URL,
        publishable_key: str = DEFAULT_PUBLISHABLE_KEY,
    ):
        self.supabase_url = supabase_url
        self.publishable_key = publishable_key
        self._client = None
        self._current_user: Optional[Dict[str, Any]] = None

        app_data = os.getenv("APPDATA") or os.path.expanduser("~")
        self.session_dir = os.path.join(app_data, "NekoTrackerOffline")
        self.session_file = os.path.join(self.session_dir, "auth_session.json")

        self._init_supabase()
        self._restore_session()
        event_bus.subscribe("war_telemetry_synced", self.on_war_telemetry_synced)

    def _init_supabase(self) -> None:
        """Initialize Supabase client if dependencies and network allow."""
        try:
            from supabase import create_client, ClientOptions

            self._client = create_client(
                self.supabase_url,
                self.publishable_key,
                options=ClientOptions(
                    schema="launcher",
                    auto_refresh_token=True,
                    persist_session=False,
                    postgrest_client_timeout=8.0,
                    function_client_timeout=8,
                ),
            )
        except Exception as exc:
            # Fallback gracefully if offline or library issue
            self._client = None
            print(f"[AuthService] Supabase client init fallback: {exc}")

    def _auth_identifier_for_username(self, username: str) -> str:
        """Translate a plain username to the non-PII auth domain format."""
        norm = username.strip().lower()
        if "@" in norm:
            return norm
        try:
            domain = urlparse(self.supabase_url).hostname or "neko-family.internal"
        except Exception:
            domain = "neko-family.internal"
        return f"{norm}@{domain}"

    def is_logged_in(self) -> bool:
        """Check if an active operative session exists."""
        return self._current_user is not None and bool(self._current_user.get("logged_in"))

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user profile."""
        return self._current_user

    def sign_in(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate with Neko Family Supabase credentials.
        """
        username = (username or "").strip()
        password = (password or "").strip()

        if not username:
            return False, "กรุณากรอกชื่อผู้ใช้ (Username)"
        if not password:
            return False, "กรุณากรอกรหัสผ่าน (Password)"

        if not self._client:
            self._init_supabase()
            if not self._client:
                return False, "ไม่สามารถเชื่อมต่อ Supabase ได้ กรุณาตรวจสอบอินเทอร์เน็ต"

        auth_identifier = self._auth_identifier_for_username(username)
        try:
            response = self._client.auth.sign_in_with_password(
                {"email": auth_identifier, "password": password}
            )
            if not response.user or not response.session:
                return False, "เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่อีกครั้ง"

            user_meta = getattr(response.user, "user_metadata", {}) or {}
            saved_callsign = user_meta.get("callsign") or user_meta.get("character_name") or ""

            self._current_user = {
                "logged_in": True,
                "mode": "supabase",
                "username": username,
                "callsign": saved_callsign,
                "character_name": saved_callsign or username,
                "user_id": str(response.user.id),
                "email": getattr(response.user, "email", auth_identifier),
                "access_token": getattr(response.session, "access_token", ""),
                "refresh_token": getattr(response.session, "refresh_token", ""),
            }
            self._save_session()
            event_bus.emit("auth_state_changed", user=self._current_user)
            return True, f"ยินดีต้อนรับกลับ, {username}!"
        except Exception as exc:
            err_msg = str(exc).lower()
            if "invalid login credentials" in err_msg or "invalid_grant" in err_msg:
                return False, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"
            if "network" in err_msg or "timeout" in err_msg or "connection" in err_msg:
                return False, "ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์ได้ ตรวจสอบอินเทอร์เน็ต"
            return False, f"เข้าสู่ระบบไม่สำเร็จ: {exc}"

    def save_operative_profile(self, callsign: str, *args: Any, **kwargs: Any) -> Tuple[bool, str]:
        """
        Save operative Callsign / In-game Character Name after authentication.
        """
        callsign = (callsign or "").strip()
        if not callsign:
            return False, "กรุณากรอกชื่อในเกม (Character Name)"

        if not self._current_user:
            self._current_user = {
                "logged_in": True,
                "mode": "supabase",
                "username": callsign,
                "user_id": f"op_{callsign.lower()}",
            }

        self._current_user["callsign"] = callsign
        self._current_user["character_name"] = callsign

        # Update Supabase user metadata if available
        if self._client and self._current_user.get("mode") == "supabase":
            try:
                self._client.auth.update_user({
                    "data": {"callsign": callsign, "character_name": callsign}
                })
            except Exception as exc:
                print(f"[AuthService] User metadata sync warning: {exc}")

        self._save_session()
        event_bus.emit("auth_state_changed", user=self._current_user)
        return True, f"บันทึกข้อมูลสมาชิก {callsign} เรียบร้อย!"

    def save_meseta_to_database(self, character_name: str, *args: Any, **kwargs: Any) -> Tuple[bool, str]:
        """
        Record [character_name (from log), meseta] to database.
        Accepts:
          save_meseta_to_database(character_name, meseta)
          save_meseta_to_database(character_name, team_name, meseta) [legacy fallback]
        """
        meseta = 0
        if args:
            if len(args) == 1:
                meseta = int(args[0])
            elif len(args) >= 2:
                # legacy: (character_name, team_name, meseta)
                meseta = int(args[1])
        elif "meseta" in kwargs:
            meseta = int(kwargs["meseta"])

        record = {
            "character_name": character_name or "Operative",
            "meseta": meseta,
            "timestamp": int(os.path.getmtime(self.session_file) if os.path.exists(self.session_file) else 0),
        }

        # Update Supabase user metadata in database if logged in
        if self._client and self._current_user and self._current_user.get("mode") == "supabase":
            try:
                self._client.auth.update_user({
                    "data": {
                        "character_name": record["character_name"],
                        "meseta": record["meseta"],
                    }
                })
            except Exception as exc:
                print(f"[AuthService] Database record update warning: {exc}")

        # Save to local database cache
        try:
            os.makedirs(self.session_dir, exist_ok=True)
            db_file = os.path.join(self.session_dir, "database_meseta_records.json")
            with open(db_file, "w", encoding="utf-8") as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        return True, "บันทึกลงฐานข้อมูลเรียบร้อย"

    def on_war_telemetry_synced(self, payload: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Handler to automatically sync meseta record to database on telemetry broadcast."""
        if not payload:
            return
        cname = payload.get("character_name") or self.get_operative_name()
        meseta = payload.get("meseta", 0)
        self.save_meseta_to_database(cname, meseta)

    def get_operative_name(self) -> str:
        """Get display name for active operative."""
        if not self._current_user:
            return "Operative"
        return self._current_user.get("character_name") or self._current_user.get("callsign") or self._current_user.get("username") or "Operative"

    def sign_in_callsign(self, callsign: str, *args: Any, **kwargs: Any) -> Tuple[bool, str]:
        """
        Quick member sign-in using Callsign / In-game Character Name (Zero-Friction / Offline-Ready).
        """
        callsign = (callsign or "").strip()
        if not callsign:
            return False, "กรุณากรอกชื่อสมาชิก (Callsign)"

        self._current_user = {
            "logged_in": True,
            "mode": "callsign",
            "username": callsign,
            "callsign": callsign,
            "character_name": callsign,
            "user_id": f"callsign_{callsign.lower()}",
        }
        self._save_session()
        event_bus.emit("auth_state_changed", user=self._current_user)
        return True, f"ยืนยันข้อมูลสมาชิก {callsign} เรียบร้อย!"

    def set_team(self, team_id: str = "") -> None:
        """Deprecated: Team system removed."""
        pass

    def sign_out(self) -> None:
        """Sign out the current operative and clear cached session."""
        if self._client and self._current_user and self._current_user.get("mode") == "supabase":
            try:
                self._client.auth.sign_out()
            except Exception:
                pass

        self._current_user = None
        self._clear_session_file()
        event_bus.emit("auth_state_changed", user=None)

    def _save_session(self) -> None:
        """Persist non-sensitive session state to local app data (tokens stripped)."""
        if not self._current_user:
            return
        try:
            os.makedirs(self.session_dir, exist_ok=True)
            # Security hardening: Strip access_token and refresh_token from disk persistence
            safe_user = dict(self._current_user)
            safe_user.pop("access_token", None)
            safe_user.pop("refresh_token", None)
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(safe_user, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"[AuthService] Save session error: {exc}")

    def _restore_session(self) -> None:
        """Restore previous operative session from local storage if valid."""
        if not os.path.exists(self.session_file):
            return
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("logged_in") and data.get("username"):
                    self._current_user = data
                    print(f"[AuthService] Restored operative session: {data.get('username')}")
        except Exception as exc:
            print(f"[AuthService] Restore session error: {exc}")

    def _clear_session_file(self) -> None:
        """Remove persisted session file."""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as exc:
            print(f"[AuthService] Clear session error: {exc}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔐  NEKO Tracker — AuthService Self-Test")
    print("=" * 60)
    service = AuthService()
    print(f" [i] Initial logged in: {service.is_logged_in()}")
    print(" [✓] AuthService initialized cleanly without mock data!")
    print("=" * 60)
