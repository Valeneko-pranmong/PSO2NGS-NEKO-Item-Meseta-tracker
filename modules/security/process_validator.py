import sys
import time
from typing import Optional


class IProcessValidator:
    """Interface for checking if the PSO2:NGS game process is active."""

    def is_game_process_running(self) -> bool:
        raise NotImplementedError


class WindowsProcessValidator(IProcessValidator):
    """
    Checks for active PSO2:NGS game client processes using Windows Toolhelp32Snapshot.
    Zero external dependencies (ctypes stdlib) with TTL-based caching.
    """

    KNOWN_PSO2_PROCESS_NAMES = (
        "pso2.exe",
        "pso2ngs.exe",
        "pso2bin.exe",
        "pso2_bin.exe",
        "pso2",
        "pso2ngs",
        "pso2bin",
        "pso2_bin",
    )

    def __init__(self, cache_ttl_seconds: float = 2.0):
        self.cache_ttl = cache_ttl_seconds
        self._last_check_time: float = 0.0
        self._cached_result: bool = False

    def is_game_process_running(self, force_refresh: bool = False) -> bool:
        now = time.time()
        if not force_refresh and (now - self._last_check_time) < self.cache_ttl:
            return self._cached_result

        self._last_check_time = now
        if sys.platform != "win32":
            # Permissive on non-Windows platforms (e.g. Linux CI)
            self._cached_result = True
            return True

        try:
            self._cached_result = self._check_windows_toolhelp()
        except Exception:
            # Fallback to permissive to avoid false positives if process query is restricted
            self._cached_result = True

        return self._cached_result

    def _check_windows_toolhelp(self) -> bool:
        import ctypes
        from ctypes import wintypes

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", wintypes.WCHAR * 260),
            ]

        kernel32 = ctypes.windll.kernel32
        hSnapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
        if hSnapshot == -1 or hSnapshot == 0xFFFFFFFFFFFFFFFF:
            return True

        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
        found = False
        try:
            if kernel32.Process32FirstW(hSnapshot, ctypes.byref(entry)):
                while True:
                    exe_name = entry.szExeFile.lower()
                    for target in self.KNOWN_PSO2_PROCESS_NAMES:
                        if exe_name == target or exe_name.startswith(target + "."):
                            found = True
                            break
                    if found or not kernel32.Process32NextW(hSnapshot, ctypes.byref(entry)):
                        break
        finally:
            kernel32.CloseHandle(hSnapshot)

        return found


class MockProcessValidator(IProcessValidator):
    """Configurable process validator for unit tests and simulation."""

    def __init__(self, is_running: bool = True):
        self.is_running = is_running

    def is_game_process_running(self) -> bool:
        return self.is_running
