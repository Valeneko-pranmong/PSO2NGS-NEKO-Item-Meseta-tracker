from collections import deque
from datetime import datetime, timedelta
import os
import time
from typing import Callable, List, Optional, Tuple

from .process_validator import IProcessValidator, WindowsProcessValidator
from .file_handle_validator import (
    IFileHandleValidator,
    WindowsRestartManagerFileValidator,
)
from .path_validator import is_canonical_sega_log_path
from .cadence_analyzer import CadenceAnalyzer
from .tamper_violation import TamperViolation, TamperViolationType
from .action_log_record import ActionLogRecord, ActionLogParser


class AntiTamperGuard:
    """
    Core Anti-Tamper and Data Integrity Guard for NEKO Tracker.
    Implements multi-layer heuristic security gating for ActionLog stream verification:
    - Gate 0: Version Security Gating (SemVer check & revocation blacklist)
    - Gate 1: Game Process Verification (pso2.exe Toolhelp32 active check)
    - Gate 2: Timestamp Verification (Clock skew < 60s, Replay < 5m, Non-reversal)
    - Gate 3: Sequence Monotonicity (seq increments, anomaly jump warning)
    - Gate 4: Identity Consistency (Locked character name match)
    - Gate 5: Drop Limits & Sliding Window Velocity (Max 300k, 250k/min limit)
    - Gate 6: Cadence Jitter Check (Statistical entropy / artificial timer detection)
    - Gate 7: File Stream & Handle Verification (File shrink/rewind, Restart Manager game lock, canonical path)
    """

    def __init__(
        self,
        process_validator: Optional[IProcessValidator] = None,
        file_handle_validator: Optional[IFileHandleValidator] = None,
        max_single_meseta_drop: int = 300_000,
        max_meseta_per_minute: int = 250_000,
        max_future_timestamp_skew: float = 60.0,
        max_past_timestamp_skew: float = 300.0,
        max_sequence_jump: int = 5000,
        active_version: str = "7.1.0",
        enforce_process_validation: bool = True,
        enforce_file_handle_validation: bool = False,
        enforce_canonical_path: bool = False,
        enforce_cadence_validation: bool = True,
        enforce_timestamp_validation: bool = True,
        enforce_sequence_validation: bool = True,
        enforce_velocity_validation: bool = True,
        enforce_ceiling_validation: bool = True,
        enforce_stream_validation: bool = True,
        enforce_version_validation: bool = True,
        min_cadence_sample_size: int = 10,
        min_cadence_stddev: float = 0.05,
    ):
        self.process_validator = process_validator or WindowsProcessValidator()
        self.file_handle_validator = (
            file_handle_validator or WindowsRestartManagerFileValidator()
        )
        self.max_single_meseta_drop = max_single_meseta_drop
        self.max_meseta_per_minute = max_meseta_per_minute
        self.max_future_timestamp_skew = max_future_timestamp_skew
        self.max_past_timestamp_skew = max_past_timestamp_skew
        self.max_sequence_jump = max_sequence_jump
        self.active_version = active_version

        self.enforce_process_validation = enforce_process_validation
        self.enforce_file_handle_validation = enforce_file_handle_validation
        self.enforce_canonical_path = enforce_canonical_path
        self.enforce_cadence_validation = enforce_cadence_validation
        self.enforce_timestamp_validation = enforce_timestamp_validation
        self.enforce_sequence_validation = enforce_sequence_validation
        self.enforce_velocity_validation = enforce_velocity_validation
        self.enforce_ceiling_validation = enforce_ceiling_validation
        self.enforce_stream_validation = enforce_stream_validation
        self.enforce_version_validation = enforce_version_validation

        self.cadence_analyzer = CadenceAnalyzer(
            min_sample_size=min_cadence_sample_size,
            min_stddev_threshold=min_cadence_stddev,
        )

        # Tracking state
        self._last_sequence: int = -1
        self._last_timestamp: Optional[datetime] = None
        self._locked_player_id: Optional[str] = None
        self._locked_character_name: Optional[str] = None
        self._last_file_size: int = 0
        self._last_file_position: int = 0

        # Sliding window for velocity check: (epoch_timestamp, amount)
        self._velocity_window: deque[Tuple[float, int]] = deque()
        self._window_meseta_total: int = 0

        # Status & Violations
        self.is_compromised: bool = False
        self.violations: List[TamperViolation] = []
        self.on_violation: Optional[Callable[[TamperViolation], None]] = None

    def reset(self) -> None:
        """Resets all tracking counters and violation state for a new session."""
        self._last_sequence = -1
        self._last_timestamp = None
        self._locked_player_id = None
        self._locked_character_name = None
        self._last_file_size = 0
        self._last_file_position = 0
        self._velocity_window.clear()
        self._window_meseta_total = 0
        self.cadence_analyzer.reset()
        self.is_compromised = False
        self.violations.clear()

    def switch_log_stream(self, new_file_path: Optional[str] = None) -> None:
        """
        Switches active log file stream (e.g. during hourly PSO2 log rollover)
        without resetting locked player identity or active session earnings.
        """
        self._last_file_size = 0
        self._last_file_position = 0
        self._last_sequence = -1
        self._last_timestamp = None
        self.cadence_analyzer.reset()

    def lock_identity(self, player_id: Optional[str], character_name: Optional[str]) -> None:
        """Locks operative identity to prevent session spoofing across characters."""
        if player_id:
            self._locked_player_id = str(player_id).strip()
        if character_name:
            self._locked_character_name = str(character_name).strip()

    def validate_stream(
        self,
        current_file_position: int,
        current_file_size: int,
        file_path: Optional[str] = None,
    ) -> bool:
        """
        Validates file stream continuity and locking handles before reading.
        Catches file shrinking, truncation, unexpected rewind, unverified paths,
        and missing game write handles.
        """
        if not self.enforce_stream_validation:
            return True

        # Idle stream guard: If position matches size and matches last recorded size,
        # no new bytes were appended. Return True without handle validation churn.
        if (
            current_file_position == current_file_size
            and current_file_size == self._last_file_size
            and self._last_file_size > 0
        ):
            return True

        if self._last_file_size > 0 and current_file_size < self._last_file_size:
            violation = TamperViolation(
                TamperViolationType.FILE_STREAM_TRUNCATED,
                f"File size shrank from {self._last_file_size} to {current_file_size}. Log file was truncated or modified externally.",
            )
            self._record_violation(violation)
            return False

        if self._last_file_position > 0 and current_file_position < self._last_file_position:
            violation = TamperViolation(
                TamperViolationType.FILE_STREAM_TAMPERED,
                f"File read position rewound from {self._last_file_position} to {current_file_position}.",
            )
            self._record_violation(violation)
            return False

        # Additional inspections when active file_path is available
        if file_path:
            # 1. Canonical SEGA Log Path Gating
            if self.enforce_canonical_path:
                is_canonical, reason = is_canonical_sega_log_path(file_path)
                if not is_canonical:
                    violation = TamperViolation(
                        TamperViolationType.NON_CANONICAL_LOG_PATH,
                        f"Non-canonical log directory detected: {reason} (Path: '{file_path}').",
                    )
                    self._record_violation(violation)
                    return False

            # 2. File Handle & Game Ownership Check
            if self.enforce_file_handle_validation:
                is_held = self.file_handle_validator.is_file_held_by_game(file_path)
                game_running = (
                    self.process_validator.is_game_process_running()
                    if self.process_validator
                    else False
                )
                if not is_held and not game_running:
                    violation = TamperViolation(
                        TamperViolationType.FILE_NOT_LOCKED_BY_GAME,
                        f"Log file '{os.path.basename(file_path)}' is not locked/opened by PSO2 game process. Suspected offline or fake log injection.",
                    )
                    self._record_violation(violation)
                    return False

                has_unauth, unauth_apps = (
                    self.file_handle_validator.has_unauthorized_concurrent_writers(file_path)
                )
                if has_unauth:
                    violation = TamperViolation(
                        TamperViolationType.UNAUTHORIZED_CONCURRENT_WRITER,
                        f"Unauthorized concurrent processes holding open handles to log file: {', '.join(unauth_apps)}.",
                    )
                    self._record_violation(violation)
                    return False

        self._last_file_size = current_file_size
        self._last_file_position = current_file_position
        return True

    def validate_record(
        self,
        record: ActionLogRecord,
        reference_time: Optional[datetime] = None,
    ) -> bool:
        """
        Validates a parsed ActionLog record across all security gates.
        """
        now = reference_time or datetime.now()

        # Gate 0. Client Version Security Gate
        if self.enforce_version_validation:
            from modules.war_mode.war_service import is_version_secure

            if not is_version_secure(self.active_version):
                self._record_violation(
                    TamperViolation(
                        TamperViolationType.INSECURE_CLIENT_VERSION,
                        f"Client version '{self.active_version}' is revoked due to security vulnerabilities. Meseta income will not be counted.",
                        log_line=record.raw_line,
                    )
                )
                return False

        # Gate 1. Game Process Verification
        if self.enforce_process_validation and (record.has_meseta_drop or record.has_item_drop):
            if not self.process_validator.is_game_process_running():
                self._record_violation(
                    TamperViolation(
                        TamperViolationType.GAME_PROCESS_NOT_RUNNING,
                        "Meseta/Item recorded while PSO2 game process is not running. Suspected fake log injection.",
                        log_line=record.raw_line,
                    )
                )
                return False

        # Gate 2. Timestamp Verification
        if self.enforce_timestamp_validation and record.timestamp is not None:
            max_future = timedelta(seconds=self.max_future_timestamp_skew)
            max_past = timedelta(seconds=self.max_past_timestamp_skew)

            if record.timestamp > (now + max_future):
                self._record_violation(
                    TamperViolation(
                        TamperViolationType.TIMESTAMP_SKEW_OUT_OF_RANGE,
                        f"Record timestamp is in the future: {record.timestamp.isoformat()} (Current: {now.isoformat()}).",
                        log_line=record.raw_line,
                    )
                )
                return False

            if (now - record.timestamp) > max_past:
                self._record_violation(
                    TamperViolation(
                        TamperViolationType.TIMESTAMP_REPLAY_OLD,
                        f"Record timestamp is too old (> {self.max_past_timestamp_skew / 60:.1f} mins): {record.timestamp.isoformat()}.",
                        log_line=record.raw_line,
                        is_fatal=False,
                    )
                )
                return False

            if self._last_timestamp is not None and record.timestamp < (
                self._last_timestamp - timedelta(seconds=2)
            ):
                self._record_violation(
                    TamperViolation(
                        TamperViolationType.TIMESTAMP_SKEW_OUT_OF_RANGE,
                        f"Record timestamp moved backward from {self._last_timestamp.isoformat()} to {record.timestamp.isoformat()}.",
                        log_line=record.raw_line,
                    )
                )
                return False

        # Gate 3. Sequence Monotonicity & Anomalous Jump
        if self.enforce_sequence_validation and record.sequence_number >= 0:
            if self._last_sequence >= 0:
                if record.sequence_number < self._last_sequence:
                    self._record_violation(
                        TamperViolation(
                            TamperViolationType.SEQUENCE_NUMBER_DECREASED,
                            f"Log sequence number decreased from {self._last_sequence} to {record.sequence_number}.",
                            log_line=record.raw_line,
                        )
                    )
                    return False

                if (record.sequence_number - self._last_sequence) > self.max_sequence_jump:
                    self._record_violation(
                        TamperViolation(
                            TamperViolationType.SEQUENCE_JUMP_ANOMALOUS,
                            f"Suspicious jump in sequence number from {self._last_sequence} to {record.sequence_number}.",
                            log_line=record.raw_line,
                            is_fatal=False,
                        )
                    )
            self._last_sequence = record.sequence_number

        # Gate 4. Character Identity Consistency
        if self._locked_character_name and record.character_name:
            if record.character_name.lower() != self._locked_character_name.lower():
                self._record_violation(
                    TamperViolation(
                        TamperViolationType.CHARACTER_IDENTITY_MISMATCH,
                        f"Character name mismatch: Expected '{self._locked_character_name}' but got '{record.character_name}'.",
                        log_line=record.raw_line,
                    )
                )
                return False

        # Gate 5. Drop Limits & Velocity Gates
        if record.has_meseta_drop:
            if self.enforce_ceiling_validation and record.meseta_drop > self.max_single_meseta_drop:
                self._record_violation(
                    TamperViolation(
                        TamperViolationType.DROP_AMOUNT_EXCEEDS_CEILING,
                        f"Single Meseta drop of {record.meseta_drop:,} exceeds maximum ceiling of {self.max_single_meseta_drop:,}.",
                        log_line=record.raw_line,
                    )
                )
                return False

            if self.enforce_velocity_validation:
                event_epoch = (
                    record.timestamp.timestamp() if record.timestamp else now.timestamp()
                )
                self._velocity_window.append((event_epoch, record.meseta_drop))
                self._window_meseta_total += record.meseta_drop

                cutoff = event_epoch - 60.0
                while self._velocity_window and self._velocity_window[0][0] < cutoff:
                    old_time, old_amt = self._velocity_window.popleft()
                    self._window_meseta_total -= old_amt

                if self._window_meseta_total > self.max_meseta_per_minute:
                    self._record_violation(
                        TamperViolation(
                            TamperViolationType.VELOCITY_EXCEEDS_PHYSICAL_LIMIT,
                            f"Meseta farming velocity {self._window_meseta_total:,}/min exceeds physical maximum ceiling of {self.max_meseta_per_minute:,}/min.",
                            log_line=record.raw_line,
                        )
                    )
                    return False

            # Gate 6. Cadence Jitter Check (Artificial Bot / Periodic Timer Detection)
            if self.enforce_cadence_validation:
                event_epoch = (
                    record.timestamp.timestamp() if record.timestamp else now.timestamp()
                )
                self.cadence_analyzer.record_event(event_epoch)
                is_robotic, stddev = self.cadence_analyzer.is_robotic_cadence()
                if is_robotic and stddev is not None:
                    self._record_violation(
                        TamperViolation(
                            TamperViolationType.ARTIFICIAL_BOT_CADENCE,
                            f"Artificial bot cadence detected: Drop interval standard deviation {stddev:.4f}s is below minimum human jitter threshold ({self.cadence_analyzer.min_stddev_threshold:.2f}s).",
                            log_line=record.raw_line,
                        )
                    )
                    return False

        if record.timestamp is not None:
            self._last_timestamp = record.timestamp

        return True

    def validate_line(
        self,
        line: str,
        reference_time: Optional[datetime] = None,
    ) -> Tuple[bool, Optional[ActionLogRecord], Optional[TamperViolation]]:
        """Parses and validates a raw ActionLog line."""
        record = ActionLogParser.parse_line(line)
        if record is None:
            return True, None, None

        prev_violations_len = len(self.violations)
        is_valid = self.validate_record(record, reference_time=reference_time)
        latest_violation = (
            self.violations[-1] if len(self.violations) > prev_violations_len else None
        )
        return is_valid, record, latest_violation

    def _record_violation(self, violation: TamperViolation) -> None:
        self.violations.append(violation)
        if violation.is_fatal:
            self.is_compromised = True
        if self.on_violation:
            try:
                self.on_violation(violation)
            except Exception as e:
                print(f"[AntiTamperGuard] Error invoking on_violation callback: {e}")
