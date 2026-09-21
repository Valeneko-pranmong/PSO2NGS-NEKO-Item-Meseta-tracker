"""End-to-End (E2E) Comprehensive Lifecycle Test Suite for NEKO Tracker V7.1.0.

Tests the full user lifecycle:
1. App initialization in Test Mode
2. Mock log streaming & continuous live tailing via background monitor
3. Live Meseta & Item drop ingestion & dashboard metrics update
4. Watchlist filtering toggle
5. Overlay window (Mini & Full) dynamic telemetry updates
6. ARKS War Room coordinate selection & secure cloud sync
7. Dynamic multi-language in-flight switching (EN -> TH -> JA -> EN)
8. Guide dialog lifecycle & tab navigation
9. Session data reset & clean teardown
"""

import os
import sys
import time
import pytest
from unittest.mock import patch, MagicMock

from meseta_tracker import NGSTrackerApp
from overlay_ui import OverlayWindow
from modules.guide_dialog import GuideWindow, open_guide_dialog
from modules.i18n import i18n
from modules.security.anti_tamper import AntiTamperGuard, ActionLogRecord, TamperViolationType
from tools.mock_log_simulator import MockLogSimulator


@pytest.fixture
def e2e_environment(tmp_path):
    """Sets up an isolated mock log environment for E2E testing."""
    log_dir = tmp_path / "mock_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    sim = MockLogSimulator(str(log_dir), initial_wallet=25000000)
    sim.write_initial_seed()
    return {
        "dir": str(log_dir),
        "sim": sim,
        "log_file": sim.log_file,
    }


def test_e2e_full_application_lifecycle(e2e_environment, shared_app):
    """
    E2E Test 1: Complete end-to-end live log streaming & tailing, metric calculation,
    overlay rendering, war sync, i18n dynamic updates, and data reset.
    """
    app = shared_app
    sim = e2e_environment["sim"]
    log_dir = e2e_environment["dir"]

    # 1. Initialize App in Test Mode
    app._enable_test_mode_bypasses()
    app.set_app_language("en")
    app.update_idletasks()

    # 2. Select Log Folder & Trigger Initial Parse
    app.log_folder = log_dir
    app.find_latest_log_file()
    assert app.log_path is not None
    assert os.path.exists(app.log_path)

    app.reset_data()
    app._enable_test_mode_bypasses()
    app.anti_tamper.reset()

    assert app.is_test_mode is True
    assert app.session_meseta == 0
    assert len(app.item_counts) == 0

    # 3. Simulate Live Streaming Ingestion
    sim.emit_meseta_drop(50000)
    sim.emit_item_drop("Arms Refiner II", 2)
    sim.emit_meseta_drop(100000)
    sim.emit_item_drop("Gold Primm Sword II +90", 1)
    sim.emit_meseta_drop(25000)

    # Allow live background monitor thread to tail the file
    deadline = time.time() + 5.0
    while time.time() < deadline:
        app.update()
        if app.session_meseta >= 176000:
            break
        time.sleep(0.1)

    app.update_idletasks()

    # 4. Verify Dashboard Telemetry & Live Streaming Metrics
    assert app.session_meseta == 176000
    assert app.current_wallet == 25175000
    assert app.character_name == "Vale3neko"
    assert app.anti_tamper.is_compromised is False

    # Check Dropped Items in dictionary
    assert "Arms Refiner II" in app.item_counts
    assert app.item_counts["Arms Refiner II"] == 2
    assert "Gold Primm Sword II +90" in app.item_counts
    assert app.item_counts["Gold Primm Sword II +90"] == 1

    # 5. Watchlist Filter Toggle
    app.watchlist_items = ["Arms Refiner II"]
    app.toggle_filter(True)
    assert app.is_filter_active is True

    app.toggle_filter(False)
    assert app.is_filter_active is False

    # 6. Overlay Window Lifecycle (Mini and Full)
    # Test Mini Overlay
    overlay_mini = OverlayWindow(app, mode="mini")
    overlay_mini.update()
    assert overlay_mini.winfo_exists()
    assert "25,175,000" in overlay_mini.lbl_wallet_overlay.cget("text")
    overlay_mini.destroy()

    # Test Full Overlay
    overlay_full = OverlayWindow(app, mode="full")
    overlay_full.update()
    assert overlay_full.winfo_exists()
    assert "25,175,000" in overlay_full.lbl_wallet_overlay.cget("text")
    overlay_full.destroy()

    # 7. ARKS War Room View & Cloud Sync
    app.show_war_view()
    app.update_idletasks()
    wv = app.war_view

    # Verify Operative Header
    assert "Vale3neko" in wv.lbl_op_title.cget("text")

    # Select Landmark "Core" [0, 0]
    expected_slot = getattr(wv.war_service.target_coord, "slot", 1)
    wv._on_landmark_selected("🌌 Core [0, 0]")
    assert wv.entry_coord.get() == f"0, 0, {expected_slot}"
    assert app.board_coord == f"0, 0, {expected_slot}"
    assert app.war_service.target_coord == (0, 0, expected_slot)

    # Also test manual coordinate entry submission via save button
    wv.coord_var.set("1, 2, 4")
    wv._on_coord_submit()
    assert app.board_coord == "1, 2, 4"
    assert app.war_service.target_coord == (1, 2, 4)

    # Execute Cloud Sync
    ok, sync_msg = app.war_service.sync_to_cloud_database()
    assert ok is True
    assert "สำเร็จ" in sync_msg or "OK" in sync_msg

    # 8. Dynamic Multi-language In-flight Switching
    for lang in ["th", "ja", "en"]:
        app.set_app_language(lang)
        app.update_idletasks()
        assert i18n.current_language == lang
        # War Room controls retranslate
        assert wv.btn_paste_coord.cget("text") != ""
        assert wv.btn_save_coord.cget("text") != ""

    app.show_offline_view()
    app.update_idletasks()

    # 9. Guide System (How to Use) Lifecycle
    guide = open_guide_dialog(app, initial_tab="setup")
    try:
        guide.update()
        assert guide.winfo_exists()

        # Navigate through tabs
        for tab_id in ["setup", "tracking", "overlay", "war", "community"]:
            tab_label = guide.tab_map[tab_id]
            guide._on_tab_selected(tab_label)
            guide.update_idletasks()
            assert guide.current_tab == tab_id

        # Verify Community Discord Link
        assert "discord.gg" in guide.lbl_credit_footer.cget("text")
    finally:
        guide.destroy()

    # 10. Session Data Reset Lifecycle
    app.reset_data()
    app.update_idletasks()
    assert app.session_meseta == 0
    assert len(app.item_counts) == 0
    assert app.war_service.session_contribution == 0


def test_e2e_tamper_defense_and_recovery():
    """
    E2E Test 2: Verify Anti-Tamper defenses reject injected log spoofing
    when not in test mode, and flag compromise state properly.
    """
    guard = AntiTamperGuard(enforce_process_validation=False)
    guard.reset()
    assert guard.is_compromised is False

    # Simulate giant drop exceeding ceiling (500,000 > 300,000)
    giant_drop = ActionLogRecord(meseta_drop=500_000)
    assert guard.validate_record(giant_drop) is False
    assert guard.is_compromised is True
    assert any(v.type == TamperViolationType.DROP_AMOUNT_EXCEEDS_CEILING for v in guard.violations)
