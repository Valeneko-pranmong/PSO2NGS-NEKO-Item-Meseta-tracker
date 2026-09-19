"""
ARKS War Room Mode Subsystem
Manages realtime telemetry and farming contributions.
"""
from .war_service import WarService, TEAMS_DATA
from .war_view import WarDashboardFrame

__all__ = [
    "WarService",
    "TEAMS_DATA",
    "WarDashboardFrame",
]
