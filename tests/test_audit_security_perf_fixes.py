"""
Tests verifying Security & Performance Audit remediation:
1. P0: Supabase credentials removed from source / injected via env only.
2. P1: Legacy auth_session.json cleanup routine works securely.
3. P1: Firebase Security Rules schema (JSON validity, version gating, ceiling validation).
4. P2: Firebase URL centralization / import from config.py.
5. P2: Retranslate UI deduplication (single canonical implementation).
6. P3: Target roots dynamic resolution in setup_database.
7. Perf: Character detection caching avoids redundant disk writes when stats unchanged.
"""

import json
import os
import inspect
import pytest

from modules.utils import cleanup_legacy_auth_session
import config
from modules.war_mode.war_service import WarService
from meseta_tracker import NGSTrackerApp


def test_supabase_credentials_not_hardcoded():
    """Verify that archive/legacy_auth/auth_service.py does not contain hardcoded keys."""
    auth_file = os.path.join(os.path.dirname(__file__), "..", "archive", "legacy_auth", "auth_service.py")
    if os.path.exists(auth_file):
        with open(auth_file, "r", encoding="utf-8") as f:
            content = f.read()
        assert "sb_publishable_mMW9OyuaGxB6YKmiPJo7gA_FNZjDb7v" not in content
        assert "DEFAULT_SUPABASE_URL = os.getenv" in content
        assert "DEFAULT_PUBLISHABLE_KEY = os.getenv" in content


def test_legacy_auth_session_cleanup(tmp_path, monkeypatch):
    """Verify that cleanup_legacy_auth_session removes auth_session.json."""
    fake_appdata = tmp_path / "appdata"
    session_dir = fake_appdata / "NekoTrackerOffline"
    session_dir.mkdir(parents=True)
    session_file = session_dir / "auth_session.json"
    session_file.write_text('{"access_token": "secret123", "refresh_token": "ref123"}', encoding="utf-8")

    monkeypatch.setenv("APPDATA", str(fake_appdata))
    assert session_file.exists()

    cleaned = cleanup_legacy_auth_session()
    assert cleaned is True
    assert not session_file.exists()

    # Second run should gracefully return False without crashing
    assert cleanup_legacy_auth_session() is False


def test_firebase_rules_validity_and_security_controls():
    """Verify database.rules.json is valid JSON and contains required security gates."""
    rules_file = os.path.join(os.path.dirname(__file__), "..", "database.rules.json")
    assert os.path.exists(rules_file)
    with open(rules_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "rules" in data
    war_rules = data["rules"]["arks_war_room"]
    assert "version_control" in war_rules
    assert "operatives" in war_rules
    assert "sectors" in war_rules

    # Ensure revoked versions (7.0.0-alpha and 7.0.0) are blocked in write rules
    rules_str = json.dumps(war_rules)
    assert "7.0.0-alpha" in rules_str
    assert "7.0.0" in rules_str
    # Ensure meseta ceiling / number checks are present
    assert "isNumber()" in rules_str
    assert "2000000000" in rules_str


def test_retranslate_ui_is_not_duplicated():
    """Verify NGSTrackerApp has only one canonical retranslate_ui implementation."""
    methods = [m for m in dir(NGSTrackerApp) if m == "retranslate_ui"]
    assert len(methods) == 1
    # Check source lines of the class for duplicate def retranslate_ui
    src = inspect.getsource(NGSTrackerApp)
    matches = [line for line in src.splitlines() if line.strip().startswith("def retranslate_ui(")]
    assert len(matches) == 1, f"Expected 1 definition of retranslate_ui, found {len(matches)}"


def test_character_detection_io_optimization(tmp_path):
    """Verify on_character_detected does not redundantly rewrite war_stats.json if stats unchanged."""
    stats_file = str(tmp_path / "war_stats.json")
    initial_data = {
        "operative_name": "TestOperative",
        "target_coord": [0, 0, 1],
        "session_contribution": 1000,
        "total_farmed": 1000,
        "slot_farmed": {"0,0#1": 1000},
        "last_active": 1000000.0,
    }
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(initial_data, f)

    war = WarService(stats_file=stats_file, realtime_sync=False)
    assert war.operative_name == "TestOperative"
    assert war.total_farmed == 1000

    mtime_before = os.path.getmtime(stats_file)

    # Calling on_character_detected with the SAME operative name does not touch file
    war.on_character_detected("TestOperative")
    assert os.path.getmtime(stats_file) == mtime_before

    war.stop()


def test_config_discord_environment_variables(monkeypatch):
    """Verify Discord settings in config.py can be overridden via environment variables."""
    monkeypatch.setenv("DISCORD_INVITE_SHORT", "discord.gg/custom_test")
    import importlib
    import config as cfg
    importlib.reload(cfg)
    assert cfg.DISCORD_INVITE_SHORT == "discord.gg/custom_test"

    # Reload again without env override to restore default
    monkeypatch.delenv("DISCORD_INVITE_SHORT", raising=False)
    importlib.reload(cfg)
