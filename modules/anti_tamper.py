"""
Alias module for AntiTamperGuard and security subsystems.
Allows importing directly from modules.anti_tamper.
"""

from .security import (
    AntiTamperGuard,
    TamperViolation,
    TamperViolationType,
    IProcessValidator,
    WindowsProcessValidator,
    MockProcessValidator,
    IFileHandleValidator,
    WindowsRestartManagerFileValidator,
    MockFileHandleValidator,
    is_canonical_sega_log_path,
    is_reparse_point_or_symlink,
    CadenceAnalyzer,
    ActionLogRecord,
    ActionLogParser,
)

__all__ = [
    "AntiTamperGuard",
    "TamperViolation",
    "TamperViolationType",
    "IProcessValidator",
    "WindowsProcessValidator",
    "MockProcessValidator",
    "IFileHandleValidator",
    "WindowsRestartManagerFileValidator",
    "MockFileHandleValidator",
    "is_canonical_sega_log_path",
    "is_reparse_point_or_symlink",
    "CadenceAnalyzer",
    "ActionLogRecord",
    "ActionLogParser",
]
