"""
NEKO Tracker Security & Anti-Tamper Subsystem
Provides ActionLog integrity verification, process validation, file handle inspection,
canonical path gating, and statistical cadence anomaly detection.
"""

from .tamper_violation import TamperViolation, TamperViolationType
from .process_validator import (
    IProcessValidator,
    WindowsProcessValidator,
    MockProcessValidator,
)
from .file_handle_validator import (
    IFileHandleValidator,
    WindowsRestartManagerFileValidator,
    MockFileHandleValidator,
)
from .path_validator import (
    is_canonical_sega_log_path,
    is_reparse_point_or_symlink,
)
from .cadence_analyzer import CadenceAnalyzer
from .action_log_record import ActionLogRecord, ActionLogParser
from .anti_tamper import AntiTamperGuard

__all__ = [
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
    "AntiTamperGuard",
]
