"""
Unit Tests for NEKO Tracker AntiTamperGuard and Data Integrity Subsystem.
Covers:
- Layer 1: Process Validation (game process active check)
- Layer 2: Timestamp Verification (future skew, replay old, backward drift)
- Layer 3: Sequence Monotonicity & Anomalous Jump
- Layer 4: Identity Locking & Mismatch Detection
- Layer 5: Single Drop Ceiling (300k) & Velocity Sliding Window (250k/min)
- Layer 6: Stream Continuity (file shrink & seek rewind)
- Layer 7: Client Version Revocation & Security Gating
- Integration: ActionLog parsing, EventBus, and WarService telemetry gating
"""

import os
import sys
from datetime import datetime, timedelta
import pytest

# Ensure root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from modules.security import (
    AntiTamperGuard,
    TamperViolation,
    TamperViolationType,
    MockProcessValidator,
    MockFileHandleValidator,
    is_canonical_sega_log_path,
    CadenceAnalyzer,
    ActionLogRecord,
    ActionLogParser,
)
from modules.war_mode.war_service import WarService
from modules.event_bus import event_bus


class TestAntiTamperGuard:
    def test_layer1_process_validator_rejects_drops_when_game_not_running(self):
        mock_proc = MockProcessValidator(is_running=False)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_timestamp_validation=False,
            enforce_version_validation=False,
        )

        record = ActionLogRecord(
            action="[Pickup]",
            meseta_drop=1500,
            raw_line="dummy line",
        )

        assert guard.validate_record(record) is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.GAME_PROCESS_NOT_RUNNING for v in guard.violations)

        # When game is running, record should pass
        guard.reset()
        mock_proc.is_running = True
        assert guard.validate_record(record) is True
        assert guard.is_compromised is False

    def test_layer2_timestamp_validation_rejects_future_and_old_records(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_version_validation=False,
            max_future_timestamp_skew=60.0,
            max_past_timestamp_skew=300.0,
        )

        now = datetime(2026, 9, 20, 12, 0, 0)

        # 1. Future timestamp (+5 minutes)
        future_rec = ActionLogRecord(
            timestamp=now + timedelta(minutes=5),
            meseta_drop=500,
            action="[Pickup]",
        )
        assert guard.validate_record(future_rec, reference_time=now) is False
        assert any(v.type == TamperViolationType.TIMESTAMP_SKEW_OUT_OF_RANGE for v in guard.violations)

        guard.reset()

        # 2. Too old timestamp (-10 minutes)
        old_rec = ActionLogRecord(
            timestamp=now - timedelta(minutes=10),
            meseta_drop=500,
            action="[Pickup]",
        )
        assert guard.validate_record(old_rec, reference_time=now) is False
        assert any(v.type == TamperViolationType.TIMESTAMP_REPLAY_OLD for v in guard.violations)

        guard.reset()

        # 3. Valid timestamp within skew range
        valid_rec = ActionLogRecord(
            timestamp=now - timedelta(seconds=30),
            meseta_drop=500,
            action="[Pickup]",
        )
        assert guard.validate_record(valid_rec, reference_time=now) is True

    def test_layer2_timestamp_backward_drift_rejected(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_version_validation=False,
        )

        t0 = datetime(2026, 9, 20, 12, 0, 0)
        rec1 = ActionLogRecord(timestamp=t0, meseta_drop=100)
        assert guard.validate_record(rec1, reference_time=t0) is True

        # Timestamp jumps backward by 10 seconds
        rec2 = ActionLogRecord(timestamp=t0 - timedelta(seconds=10), meseta_drop=100)
        assert guard.validate_record(rec2, reference_time=t0) is False
        assert any(v.type == TamperViolationType.TIMESTAMP_SKEW_OUT_OF_RANGE for v in guard.violations)

    def test_layer3_sequence_monotonicity_and_jump_detection(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_timestamp_validation=False,
            enforce_version_validation=False,
            max_sequence_jump=5000,
        )

        rec1 = ActionLogRecord(sequence_number=100, meseta_drop=100)
        rec2 = ActionLogRecord(sequence_number=101, meseta_drop=100)
        rec_decreased = ActionLogRecord(sequence_number=95, meseta_drop=100)

        assert guard.validate_record(rec1) is True
        assert guard.validate_record(rec2) is True
        # Decreasing sequence must be fatal violation
        assert guard.validate_record(rec_decreased) is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.SEQUENCE_NUMBER_DECREASED for v in guard.violations)

        guard.reset()

        # Anomalous jump (> 5000) should log non-fatal warning
        rec_start = ActionLogRecord(sequence_number=100, meseta_drop=100)
        rec_jump = ActionLogRecord(sequence_number=10_000, meseta_drop=100)
        assert guard.validate_record(rec_start) is True
        assert guard.validate_record(rec_jump) is True  # Non-fatal warning
        assert guard.is_compromised is False
        assert any(v.type == TamperViolationType.SEQUENCE_JUMP_ANOMALOUS and not v.is_fatal for v in guard.violations)

    def test_layer4_character_identity_consistency(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_timestamp_validation=False,
            enforce_version_validation=False,
        )

        guard.lock_identity("14743890", "Vale3neko")

        rec_valid = ActionLogRecord(
            sequence_number=1,
            character_name="Vale3neko",
            meseta_drop=100,
        )
        rec_spoofed = ActionLogRecord(
            sequence_number=2,
            character_name="SpoofedPlayer",
            meseta_drop=100,
        )

        assert guard.validate_record(rec_valid) is True
        assert guard.validate_record(rec_spoofed) is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.CHARACTER_IDENTITY_MISMATCH for v in guard.violations)

    def test_layer5_drop_ceiling_and_velocity_sliding_window(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_timestamp_validation=False,
            enforce_version_validation=False,
            max_single_meseta_drop=300_000,
            max_meseta_per_minute=250_000,
        )

        # 1. Single drop exceeding ceiling (e.g. 500,000)
        giant_drop = ActionLogRecord(meseta_drop=500_000)
        assert guard.validate_record(giant_drop) is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.DROP_AMOUNT_EXCEEDS_CEILING for v in guard.violations)

        guard.reset()

        # 2. Velocity flood within 1 minute
        t0 = datetime(2026, 9, 20, 12, 0, 0)
        rec1 = ActionLogRecord(timestamp=t0, meseta_drop=100_000)
        rec2 = ActionLogRecord(timestamp=t0 + timedelta(seconds=15), meseta_drop=100_000)
        rec3 = ActionLogRecord(timestamp=t0 + timedelta(seconds=30), meseta_drop=100_000)
        # 100k + 100k + 100k = 300k > 250k limit!
        assert guard.validate_record(rec1, reference_time=t0) is True
        assert guard.validate_record(rec2, reference_time=t0 + timedelta(seconds=15)) is True
        assert guard.validate_record(rec3, reference_time=t0 + timedelta(seconds=30)) is False
        assert any(v.type == TamperViolationType.VELOCITY_EXCEEDS_PHYSICAL_LIMIT for v in guard.violations)

    def test_layer6_stream_continuity_validation(self):
        guard = AntiTamperGuard(enforce_process_validation=False)

        # Initial reads progressing monotonically
        assert guard.validate_stream(1000, 2000) is True
        assert guard.validate_stream(2000, 3000) is True

        # File shrank (truncated or edited externally)
        assert guard.validate_stream(1500, 1500) is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.FILE_STREAM_TRUNCATED for v in guard.violations)

        guard.reset()
        assert guard.validate_stream(1000, 2000) is True
        # Position rewound without file resize
        assert guard.validate_stream(500, 2000) is False
        assert any(v.type == TamperViolationType.FILE_STREAM_TAMPERED for v in guard.violations)

    def test_layer7_version_security_revocation(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_timestamp_validation=False,
            active_version="7.0.0-alpha",  # Insecure revoked version
        )

        record = ActionLogRecord(
            action="[Pickup]",
            meseta_drop=5000,
            raw_line="2026-09-20T12:00:00\t100\t[Pickup]\t14743890\tVale3neko\tN-Meseta(5000)",
        )

        assert guard.validate_record(record) is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.INSECURE_CLIENT_VERSION for v in guard.violations)

        # Upgrading to secure 7.1.0 passes
        guard.reset()
        guard.active_version = "7.1.0"
        assert guard.validate_record(record) is True
        assert guard.is_compromised is False

    def test_layer8_file_handle_locking_rejects_spoofed_file_without_game_handle(self):
        mock_fh = MockFileHandleValidator(held_by_game=False)
        guard = AntiTamperGuard(
            file_handle_validator=mock_fh,
            enforce_process_validation=False,
            enforce_file_handle_validation=True,
            enforce_stream_validation=True,
        )

        # File is not held by game -> Rejected!
        assert guard.validate_stream(100, 200, file_path="C:/FakeLogs/ActionLog.txt") is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.FILE_NOT_LOCKED_BY_GAME for v in guard.violations)

        # Once game holds the handle, passes
        guard.reset()
        mock_fh._held_by_game = True
        assert guard.validate_stream(100, 200, file_path="C:/FakeLogs/ActionLog.txt") is True
        assert guard.is_compromised is False

    def test_layer8_file_handle_rejects_unauthorized_concurrent_writers(self):
        mock_fh = MockFileHandleValidator(
            held_by_game=True,
            unauthorized_processes=["fake_bot.exe", "injector.exe"],
        )
        guard = AntiTamperGuard(
            file_handle_validator=mock_fh,
            enforce_process_validation=False,
            enforce_file_handle_validation=True,
            enforce_stream_validation=True,
        )

        assert guard.validate_stream(100, 200, file_path="C:/FakeLogs/ActionLog.txt") is False
        assert guard.is_compromised is True
        assert any(v.type == TamperViolationType.UNAUTHORIZED_CONCURRENT_WRITER for v in guard.violations)

    def test_layer9_canonical_path_gating(self):
        guard = AntiTamperGuard(
            enforce_process_validation=False,
            enforce_canonical_path=True,
            enforce_stream_validation=True,
        )

        # 1. Reject rogue directory
        assert guard.validate_stream(100, 200, file_path="C:/Rogue/CheatLogs/ActionLog.txt") is False
        assert any(v.type == TamperViolationType.NON_CANONICAL_LOG_PATH for v in guard.violations)

        guard.reset()

        # 2. Accept official NGS directory structure
        canonical_path = "C:/Users/Player/Documents/SEGA/PHANTASYSTARONLINE2/log_ngs/ActionLog.txt"
        assert is_canonical_sega_log_path(canonical_path)[0] is True

    def test_layer10_cadence_analyzer_detects_robotic_periodic_timers(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_timestamp_validation=False,
            enforce_version_validation=False,
            enforce_cadence_validation=True,
            min_cadence_sample_size=10,
            min_cadence_stddev=0.05,
        )

        # Simulate robot loop dropping meseta at EXACTLY 3.000s intervals (zero jitter)
        t_base = datetime(2026, 9, 20, 12, 0, 0)
        for i in range(10):
            t = t_base + timedelta(seconds=i * 3.0)
            rec = ActionLogRecord(timestamp=t, meseta_drop=5000, sequence_number=i)
            guard.validate_record(rec, reference_time=t)

        # The 11th drop with exact 3.000s cadence will exceed min_sample_size and trigger robotic cadence
        t_robotic = t_base + timedelta(seconds=10 * 3.0)
        rec_robotic = ActionLogRecord(timestamp=t_robotic, meseta_drop=5000, sequence_number=10)
        assert guard.validate_record(rec_robotic, reference_time=t_robotic) is False
        assert any(v.type == TamperViolationType.ARTIFICIAL_BOT_CADENCE for v in guard.violations)

    def test_cadence_analyzer_passes_human_variance(self):
        mock_proc = MockProcessValidator(is_running=True)
        guard = AntiTamperGuard(
            process_validator=mock_proc,
            enforce_timestamp_validation=False,
            enforce_version_validation=False,
            enforce_cadence_validation=True,
            min_cadence_sample_size=10,
            min_cadence_stddev=0.05,
        )

        # Simulate natural human intervals with jitter: 1.2s, 4.5s, 0.8s, 3.1s, 2.7s...
        t_curr = datetime(2026, 9, 20, 12, 0, 0)
        intervals = [1.2, 4.5, 0.8, 3.1, 2.7, 5.0, 1.9, 3.8, 2.1, 4.2, 1.5, 3.3]
        for i, delta in enumerate(intervals):
            t_curr += timedelta(seconds=delta)
            rec = ActionLogRecord(timestamp=t_curr, meseta_drop=5000, sequence_number=i)
            assert guard.validate_record(rec, reference_time=t_curr) is True

        assert guard.is_compromised is False


class TestActionLogParser:
    def test_parse_valid_pickup_line(self):
        line = "2026-09-20T15:40:40\t104\t[Pickup]\t14743890\tVale3neko\tN-Meseta(12000)\tCurrentN-Meseta(50013500)"
        record = ActionLogParser.parse_line(line)
        assert record is not None
        assert record.sequence_number == 104
        assert record.action == "[Pickup]"
        assert record.player_id == "14743890"
        assert record.character_name == "Vale3neko"
        assert record.meseta_drop == 12000
        assert record.current_wallet == 50013500
        assert record.has_meseta_drop is True
        assert record.has_item_drop is False

    def test_parse_valid_item_drop_line(self):
        line = "2026-09-20T15:40:40\t110\t[Pickup]\t14743890\tVale3neko\tC/Astraea II\tNum(2)"
        record = ActionLogParser.parse_line(line)
        assert record is not None
        assert record.sequence_number == 110
        assert record.item_name == "C/Astraea II"
        assert record.item_count == 2
        assert record.has_item_drop is True
        assert record.has_meseta_drop is False


class TestAntiTamperIntegrationWithWarService:
    def test_tamper_violation_compromises_war_service_payload(self):
        war = WarService(client_version="7.1.0")
        war.set_operative("CompromisedPlayer")
        war.set_target_coord("0, 0, 1")
        war.session_contribution = 15_000_000

        # Initially clean
        payload_clean = war.get_database_payload()
        assert payload_clean["security_status"] == "SECURE"
        assert payload_clean["meseta"] == 15_000_000

        # Simulate tamper violation event via EventBus
        violation = TamperViolation(
            TamperViolationType.DROP_AMOUNT_EXCEEDS_CEILING,
            "Drop of 999,999 exceeds ceiling of 300,000",
            is_fatal=True,
        )
        event_bus.emit("tamper_violation", violation=violation)

        assert war.is_tamper_compromised is True
        assert war.tamper_violations_count >= 1

        # Database payload must nullify meseta and flag security status!
        payload_bad = war.get_database_payload()
        assert payload_bad["meseta"] == 0
        assert payload_bad["security_status"] == "TAMPER_COMPROMISED"
        assert payload_bad["version_security_valid"] is False

        # Cloud database sync must refuse compromised client
        ok, msg = war.sync_to_cloud_database()
        assert ok is False
        assert "Anti-Tamper Compromised" in msg or "แทรกแซง" in msg

        # Reset clears compromised state
        war.on_tracker_reset()
        assert war.is_tamper_compromised is False
        assert war.tamper_violations_count == 0
        war.stop()
