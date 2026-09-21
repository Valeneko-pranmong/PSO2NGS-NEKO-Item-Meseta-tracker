from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple, Union


def format_compact(value: Union[int, float]) -> str:
    """
    Format numeric value into compact readable string (e.g. 1.25M, 15.0k, 500).
    """
    av = abs(value)
    sign = "-" if value < 0 else ""
    if av >= 1_000_000:
        return f"{sign}{av / 1_000_000:.2f}M"
    if av >= 10_000:
        return f"{sign}{av / 1_000:.1f}k"
    return f"{sign}{int(av):,}"


def format_rate(meseta_per_hour: float) -> str:
    """
    Format hourly rate in Meseta/hr.
    """
    if meseta_per_hour <= 0:
        return "0 /hr"
    if meseta_per_hour >= 1_000_000:
        return f"{meseta_per_hour / 1_000_000:.2f} M/hr"
    if meseta_per_hour >= 1_000:
        return f"{meseta_per_hour / 1_000:.1f} k/hr"
    return f"{int(meseta_per_hour)} /hr"


def format_duration(seconds: float) -> str:
    """
    Format elapsed seconds into HH:MM:SS string.
    """
    if seconds < 0:
        seconds = 0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def filter_and_sort_items(
    item_counts: Dict[str, int],
    watchlist: Optional[List[str]] = None,
    keyword: Optional[str] = None,
    filter_enabled: bool = False,
    max_items: int = 50,
) -> List[Tuple[str, int]]:
    """
    Filter item counts by watchlist and keyword, then return top items sorted by count descending.
    """
    if filter_enabled:
        if watchlist:
            wl_lower = [w.strip().lower() for w in watchlist if w.strip()]
            if wl_lower:
                filtered = {
                    k: v for k, v in item_counts.items()
                    if any(w in k.lower() for w in wl_lower)
                }
            else:
                filtered = {}
        else:
            filtered = {}
    else:
        filtered = item_counts

    if keyword:
        kw = keyword.strip().lower()
        filtered = {k: v for k, v in filtered.items() if kw in k.lower()}

    return sorted(filtered.items(), key=lambda kv: kv[1], reverse=True)[:max_items]


def extract_character_info(line: str) -> Optional[Tuple[str, str]]:
    """
    Extract (character_name, player_id) from PSO2:NGS ActionLog line.
    Format: Timestamp \t Seq \t [Action] \t PlayerID \t CharacterName \t ...
    """
    parts = line.strip().split('\t')
    if len(parts) >= 5 and parts[3].strip().isdigit():
        cname = parts[4].strip()
        if cname and not cname.startswith('[') and 'Num(' not in cname:
            return cname, parts[3].strip()
    return None


class WindowMover:
    """
    High-performance, crash-free Windows native window mover.
    Uses direct Win32 SetWindowPos (SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE)
    to bypass Tk geometry formatting and Tcl overhead while avoiding
    modal message loop GIL corruption (PyEval_RestoreThread crash).
    """
    def __init__(self, window: Any):
        self.window = window
        self.start_x = 0
        self.start_y = 0
        self.win_x = 0
        self.win_y = 0
        self.last_x: Optional[int] = None
        self.last_y: Optional[int] = None
        self._hwnd: Optional[int] = None
        self._is_win32 = False
        try:
            import sys
            if sys.platform == "win32":
                self._is_win32 = True
        except Exception:
            pass

    def _get_hwnd(self) -> Optional[int]:
        if not self._is_win32:
            return None
        if self._hwnd is None:
            try:
                import ctypes
                child_id = self.window.winfo_id()
                parent_id = ctypes.windll.user32.GetParent(child_id)
                self._hwnd = parent_id if (parent_id and ctypes.windll.user32.IsWindow(parent_id)) else child_id
            except Exception:
                self._hwnd = None
        return self._hwnd

    def start_move(self, event: Any) -> None:
        self.start_x = getattr(event, "x_root", 0)
        self.start_y = getattr(event, "y_root", 0)
        try:
            self.win_x = self.window.winfo_x()
            self.win_y = self.window.winfo_y()
        except Exception:
            self.win_x = 0
            self.win_y = 0
        self.last_x = self.win_x
        self.last_y = self.win_y

    def do_move(self, event: Any) -> None:
        new_x = self.win_x + (getattr(event, "x_root", 0) - self.start_x)
        new_y = self.win_y + (getattr(event, "y_root", 0) - self.start_y)
        if new_x == self.last_x and new_y == self.last_y:
            return
        self.last_x = new_x
        self.last_y = new_y

        hwnd = self._get_hwnd()
        if hwnd:
            try:
                import ctypes
                # SWP_NOSIZE (1) | SWP_NOZORDER (4) | SWP_NOACTIVATE (16) = 0x0015
                if ctypes.windll.user32.SetWindowPos(hwnd, 0, new_x, new_y, 0, 0, 0x0015):
                    return
            except Exception:
                pass

        try:
            self.window.geometry(f"+{new_x}+{new_y}")
        except Exception:
            pass


def start_native_drag(window: Any, event: Any = None) -> bool:
    """Safe wrapper for backwards compatibility."""
    return False
