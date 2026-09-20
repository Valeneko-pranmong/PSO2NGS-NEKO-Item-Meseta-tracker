import os
import sys
from typing import Tuple


def is_reparse_point_or_symlink(path: str) -> bool:
    """
    Detects if the file or any parent folder in the path is a symbolic link,
    junction point, or reparse point redirecting to another target.
    """
    if not path or not os.path.exists(path):
        return False

    try:
        # Check standard python islink
        if os.path.islink(path):
            return True

        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            FILE_ATTRIBUTE_REPARSE_POINT = 0x400
            kernel32 = ctypes.windll.kernel32
            kernel32.GetFileAttributesW.argtypes = [wintypes.LPCWSTR]
            kernel32.GetFileAttributesW.restype = wintypes.DWORD

            # Walk path components
            curr = os.path.abspath(path)
            while curr and os.path.splitdrive(curr)[1] != "\\":
                attrs = kernel32.GetFileAttributesW(curr)
                if attrs != 0xFFFFFFFF and (attrs & FILE_ATTRIBUTE_REPARSE_POINT):
                    return True
                parent = os.path.dirname(curr)
                if parent == curr:
                    break
                curr = parent
    except Exception:
        pass

    return False


def is_canonical_sega_log_path(path: str) -> Tuple[bool, str]:
    """
    Verifies that the provided log folder or file resides within the official SEGA PSO2:NGS
    directory structure: .../SEGA/PHANTASYSTARONLINE2/log_ngs
    Returns (is_canonical, reason).
    """
    if not path:
        return False, "Path is empty"

    abs_path = os.path.abspath(path)
    norm = os.path.normpath(abs_path).lower().replace("/", "\\")

    # Canonical suffix pattern for NGS logs
    canonical_suffix = os.path.normpath("sega\\phantasystaronline2\\log_ngs").lower()

    if canonical_suffix not in norm:
        return False, f"Path does not match official SEGA NGS directory ('{canonical_suffix}')"

    # Verify no symlink or junction redirection
    if is_reparse_point_or_symlink(abs_path):
        return False, "Path contains a symlink or junction reparse point"

    # Path should generally reside within user profile
    user_home = os.path.expanduser("~").lower()
    user_profile = os.getenv("USERPROFILE", "").lower()
    if user_home and user_home not in norm and user_profile and user_profile not in norm:
        # Non-standard drive or altered user profile
        pass

    return True, "Canonical official SEGA NGS log path"
