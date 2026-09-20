from enum import Enum
import time
from typing import Optional, Dict, Any


class TamperViolationType(str, Enum):
    """Enumeration of anti-tamper and data integrity violation categories."""
    NONE = "NONE"
    GAME_PROCESS_NOT_RUNNING = "GAME_PROCESS_NOT_RUNNING"
    TIMESTAMP_SKEW_OUT_OF_RANGE = "TIMESTAMP_SKEW_OUT_OF_RANGE"
    TIMESTAMP_REPLAY_OLD = "TIMESTAMP_REPLAY_OLD"
    SEQUENCE_NUMBER_DECREASED = "SEQUENCE_NUMBER_DECREASED"
    SEQUENCE_JUMP_ANOMALOUS = "SEQUENCE_JUMP_ANOMALOUS"
    CHARACTER_IDENTITY_MISMATCH = "CHARACTER_IDENTITY_MISMATCH"
    DROP_AMOUNT_EXCEEDS_CEILING = "DROP_AMOUNT_EXCEEDS_CEILING"
    VELOCITY_EXCEEDS_PHYSICAL_LIMIT = "VELOCITY_EXCEEDS_PHYSICAL_LIMIT"
    FILE_STREAM_TRUNCATED = "FILE_STREAM_TRUNCATED"
    FILE_STREAM_TAMPERED = "FILE_STREAM_TAMPERED"
    INSECURE_CLIENT_VERSION = "INSECURE_CLIENT_VERSION"
    FILE_NOT_LOCKED_BY_GAME = "FILE_NOT_LOCKED_BY_GAME"
    UNAUTHORIZED_CONCURRENT_WRITER = "UNAUTHORIZED_CONCURRENT_WRITER"
    NON_CANONICAL_LOG_PATH = "NON_CANONICAL_LOG_PATH"
    SYMLINK_REPARSE_POINT_DETECTED = "SYMLINK_REPARSE_POINT_DETECTED"
    ARTIFICIAL_BOT_CADENCE = "ARTIFICIAL_BOT_CADENCE"


class TamperViolation:
    """Represents an identified security or data integrity violation."""

    def __init__(
        self,
        violation_type: TamperViolationType,
        message: str,
        log_line: Optional[str] = None,
        is_fatal: bool = True,
        timestamp: Optional[float] = None,
    ):
        self.type = violation_type
        self.message = message
        self.log_line = log_line
        self.is_fatal = is_fatal
        self.timestamp = timestamp if timestamp is not None else time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value if hasattr(self.type, "value") else str(self.type),
            "message": self.message,
            "log_line": self.log_line,
            "is_fatal": self.is_fatal,
            "timestamp": self.timestamp,
        }

    def __str__(self) -> str:
        type_str = self.type.value if hasattr(self.type, "value") else str(self.type)
        return f"[TamperViolation:{type_str}] {self.message} (Fatal: {self.is_fatal})"

    def __repr__(self) -> str:
        return f"TamperViolation(type={self.type}, message='{self.message}', is_fatal={self.is_fatal})"
