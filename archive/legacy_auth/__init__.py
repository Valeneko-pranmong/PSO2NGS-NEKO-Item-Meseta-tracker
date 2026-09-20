"""
ARCHIVED / DEPRECATED — DO NOT USE FOR ACTIVE DEVELOPMENT (ห้ามใช้ในงานพัฒนาปัจจุบัน)
Superseded by: Zero-Login Operative Identity via NGS ActionLog Character Name detection
Source of Truth: modules/war_mode/war_service.py & modules/event_bus.py

NEKO Tracker Legacy Auth Subsystem
Supports Neko Family Supabase authentication and quick Callsign registration (RETIRED).
"""
from .auth_service import AuthService
from .auth_view import AuthFrame

__all__ = ["AuthService", "AuthFrame"]
