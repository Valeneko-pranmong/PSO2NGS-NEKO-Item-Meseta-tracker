import logging
import os
import sys
import time
from typing import List, Optional, Tuple

logger = logging.getLogger("NekoTracker.security.file_handle")


class IFileHandleValidator:
    """Interface for inspecting active process file handles on log files."""

    def get_file_locking_processes(self, file_path: str) -> List[Tuple[int, str]]:
        raise NotImplementedError

    def is_file_held_by_game(self, file_path: str) -> bool:
        raise NotImplementedError

    def has_unauthorized_concurrent_writers(
        self, file_path: str
    ) -> Tuple[bool, List[str]]:
        raise NotImplementedError


class WindowsRestartManagerFileValidator(IFileHandleValidator):
    """
    Inspects Windows file locking handles using the official Windows Restart Manager API (rstrtmgr.dll).
    Identifies which processes currently hold an open handle on the log file.
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
        "phantasy star online 2",
        "phantasystaronline2",
        "phantasy star online",
    )

    def __init__(self, cache_ttl_seconds: float = 3.0):
        self.cache_ttl = cache_ttl_seconds
        self._cache: dict[str, Tuple[float, List[Tuple[int, str]]]] = {}

    def get_file_locking_processes(
        self, file_path: str, force_refresh: bool = False
    ) -> List[Tuple[int, str]]:
        """
        Returns list of (pid, app_name) holding an open handle to file_path.
        """
        if not file_path or not os.path.exists(file_path):
            return []

        norm_path = os.path.normcase(os.path.abspath(file_path))
        now = time.time()

        if not force_refresh and norm_path in self._cache:
            cache_time, procs = self._cache[norm_path]
            if now - cache_time < self.cache_ttl:
                return procs

        if sys.platform != "win32":
            # Non-Windows permissive fallback
            return [(0, "pso2.exe")]

        procs = self._query_restart_manager(norm_path)
        self._cache[norm_path] = (now, procs)
        return procs

    def is_file_held_by_game(self, file_path: str) -> bool:
        """
        Checks whether the game process (pso2.exe) currently has an open handle to this file.
        Returns False if no game process holds the file (indicating a fake or spoofed file).
        """
        procs = self.get_file_locking_processes(file_path)
        for _, app_name in procs:
            app_lower = app_name.lower().strip()
            for known in self.KNOWN_PSO2_PROCESS_NAMES:
                if known in app_lower or app_lower.startswith(known + "."):
                    return True
        return False

    def has_unauthorized_concurrent_writers(
        self, file_path: str
    ) -> Tuple[bool, List[str]]:
        """
        Detects if another unauthorized application (e.g. injector, script, bot) is also holding
        the log file concurrently alongside or instead of the game.
        """
        procs = self.get_file_locking_processes(file_path)
        my_pid = os.getpid()
        unauthorized = []

        for pid, app_name in procs:
            if pid == my_pid:
                continue
            app_lower = app_name.lower().strip()
            is_game = any(
                known in app_lower or app_lower.startswith(known + ".")
                for known in self.KNOWN_PSO2_PROCESS_NAMES
            )
            if not is_game:
                unauthorized.append(f"{app_name} (PID: {pid})")

        return (len(unauthorized) > 0, unauthorized)

    def _query_restart_manager(self, file_path: str) -> List[Tuple[int, str]]:
        import ctypes
        from ctypes import wintypes

        rstrtmgr = ctypes.windll.rstrtmgr

        class RM_UNIQUE_PROCESS(ctypes.Structure):
            _fields_ = [
                ("dwProcessId", wintypes.DWORD),
                ("ProcessStartTime", wintypes.FILETIME),
            ]

        CCH_RM_MAX_APP_NAME = 255
        CCH_RM_MAX_SVC_NAME = 63

        class RM_PROCESS_INFO(ctypes.Structure):
            _fields_ = [
                ("Process", RM_UNIQUE_PROCESS),
                ("strAppName", wintypes.WCHAR * (CCH_RM_MAX_APP_NAME + 1)),
                ("strServiceShortName", wintypes.WCHAR * (CCH_RM_MAX_SVC_NAME + 1)),
                ("ApplicationType", wintypes.DWORD),
                ("AppStatus", wintypes.DWORD),
                ("TSSessionId", wintypes.DWORD),
                ("bRestartable", wintypes.BOOL),
            ]

        session_handle = wintypes.DWORD()
        key = (wintypes.WCHAR * 33)()
        res = rstrtmgr.RmStartSession(ctypes.byref(session_handle), 0, key)
        if res != 0:
            return []

        results: List[Tuple[int, str]] = []
        try:
            file_path_w = wintypes.LPCWSTR(file_path)
            res = rstrtmgr.RmRegisterResources(
                session_handle, 1, ctypes.byref(file_path_w), 0, None, 0, None
            )
            if res != 0:
                return []

            proc_needed = wintypes.DWORD(0)
            proc_count = wintypes.DWORD(0)
            reboot_reasons = wintypes.DWORD(0)
            res = rstrtmgr.RmGetList(
                session_handle,
                ctypes.byref(proc_needed),
                ctypes.byref(proc_count),
                None,
                ctypes.byref(reboot_reasons),
            )

            # ERROR_MORE_DATA = 234
            if proc_needed.value > 0:
                arr = (RM_PROCESS_INFO * proc_needed.value)()
                proc_count.value = proc_needed.value
                res = rstrtmgr.RmGetList(
                    session_handle,
                    ctypes.byref(proc_needed),
                    ctypes.byref(proc_count),
                    arr,
                    ctypes.byref(reboot_reasons),
                )
                if res == 0:
                    for i in range(proc_count.value):
                        results.append(
                            (arr[i].Process.dwProcessId, arr[i].strAppName)
                        )
        except Exception as exc:
            logger.debug("_query_restart_manager: failed to query file handles: %s", exc)
        finally:
            rstrtmgr.RmEndSession(session_handle)

        return results


class MockFileHandleValidator(IFileHandleValidator):
    """Configurable file handle validator for tests."""

    def __init__(
        self,
        held_by_game: bool = True,
        unauthorized_processes: Optional[List[str]] = None,
    ):
        self._held_by_game = held_by_game
        self._unauthorized = unauthorized_processes or []

    def get_file_locking_processes(self, file_path: str) -> List[Tuple[int, str]]:
        res = []
        if self._held_by_game:
            res.append((1234, "pso2.exe"))
        for i, name in enumerate(self._unauthorized):
            res.append((5000 + i, name))
        return res

    def is_file_held_by_game(self, file_path: str) -> bool:
        return self._held_by_game

    def has_unauthorized_concurrent_writers(
        self, file_path: str
    ) -> Tuple[bool, List[str]]:
        return (len(self._unauthorized) > 0, list(self._unauthorized))
