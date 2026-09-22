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


def calculate_live_rate(
    session_meseta: Union[int, float],
    duration_seconds: float,
    min_smoothing_seconds: float = 30.0,
) -> float:
    """
    Calculate live Meseta/hr with cold-start smoothing.
    Prevents erratic spikes (e.g. 90M/hr) during the first few seconds of farming
    by using a minimum duration floor (default 30.0 seconds).
    """
    if session_meseta <= 0:
        return 0.0
    effective_duration = max(min_smoothing_seconds, max(0.0, float(duration_seconds)))
    return (float(session_meseta) / effective_duration) * 3600.0


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
    def __init__(self, window: Any, on_move_end: Optional[Any] = None):
        self.window = window
        self.on_move_end = on_move_end
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

    def end_move(self, event: Any = None) -> None:
        """Invoked on mouse release to finalize window placement and trigger callbacks."""
        if self.on_move_end and callable(self.on_move_end):
            try:
                wx = self.window.winfo_x()
                wy = self.window.winfo_y()
                self.on_move_end(wx, wy)
            except Exception:
                pass


def is_position_on_screen(x: int, y: int, width: int = 100, height: int = 100) -> bool:
    """Verifies that the window coordinates intersect with at least one active display monitor."""
    try:
        import sys
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes
            # Sample point inside window title/client area
            pt = wintypes.POINT(x + 50, y + 20)
            # MONITOR_DEFAULTTONULL = 0
            hmon = ctypes.windll.user32.MonitorFromPoint(pt, 0)
            return bool(hmon)
    except Exception:
        pass
    return True


def get_secondary_monitor_origin() -> Optional[Tuple[int, int]]:
    """Returns top-left (x, y) coordinates of a secondary monitor if present, or None."""
    try:
        import sys
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes
            monitors: List[Tuple[int, int, int, int]] = []

            def cb(hmon, hdc, rect, lparam):
                r = rect.contents
                monitors.append((r.left, r.top, r.right, r.bottom))
                return True

            CB_TYPE = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
            ctypes.windll.user32.EnumDisplayMonitors(0, 0, CB_TYPE(cb), 0)
            if len(monitors) > 1:
                # Find the first monitor that is not the primary origin (0, 0)
                for left, top, right, bottom in monitors:
                    if left != 0 or top != 0:
                        return (left + 60, top + 60)
    except Exception:
        pass
    return None


def start_native_drag(window: Any, event: Any = None) -> bool:
    """Safe wrapper for backwards compatibility."""
    return False


class SingleInstanceGuard:
    """
    Ensures only a single instance of NekoTracker runs concurrently on the system.
    Uses a Win32 Named Mutex and window restoration to bring the existing
    instance to the foreground if a second launch is attempted.
    """

    def __init__(self, mutex_name: str = "Local\\NekoNGSTrackerSingleInstanceMutex"):
        import os
        import sys

        self.mutex_name = mutex_name
        self.mutex = None
        self.already_running = False
        self._is_win32 = (sys.platform == "win32")

        # Bypass in test environments
        if (
            os.getenv("NEKO_TEST_MODE") == "1"
            or "pytest" in sys.modules
            or os.getenv("PYTEST_CURRENT_TEST")
        ):
            return

        if self._is_win32:
            try:
                import ctypes
                self.kernel32 = ctypes.windll.kernel32
                self.mutex = self.kernel32.CreateMutexW(None, False, self.mutex_name)
                # ERROR_ALREADY_EXISTS = 183
                if self.kernel32.GetLastError() == 183:
                    self.already_running = True
            except Exception:
                self.already_running = False

    def is_already_running(self) -> bool:
        return self.already_running

    def activate_existing_window(self, window_title_keyword: str = "NEKO") -> bool:
        """Brings the existing NekoTracker window to foreground and restores it if minimized."""
        if not self._is_win32:
            return False
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32

            found_hwnd = None

            def enum_proc(hwnd, lparam):
                nonlocal found_hwnd
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        if window_title_keyword.lower() in buff.value.lower():
                            found_hwnd = hwnd
                            return False
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(WNDENUMPROC(enum_proc), 0)

            if found_hwnd:
                # SW_RESTORE = 9
                user32.ShowWindow(found_hwnd, 9)
                user32.SetForegroundWindow(found_hwnd)
                return True
        except Exception:
            pass
        return False

    def release(self) -> None:
        if self._is_win32 and self.mutex:
            try:
                self.kernel32.CloseHandle(self.mutex)
            except Exception:
                pass
            self.mutex = None

