"""
NEKO Tracker Auth Subsystem
Supports Neko Family Supabase authentication and quick Callsign registration.
"""
from .auth_service import AuthService
from .auth_view import AuthFrame

__all__ = ["AuthService", "AuthFrame"]
