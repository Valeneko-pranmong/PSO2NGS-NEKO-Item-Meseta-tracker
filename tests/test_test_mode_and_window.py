"""Unit tests for Test Mode bypasses, sample log replay, and window minimize behavior."""

import os
import sys
import pytest
from meseta_tracker import NGSTrackerApp
from modules.security.anti_tamper import ActionLogParser
from tools.mock_log_simulator import MockLogSimulator


def test_test_mode_anti_tamper_bypasses(tmp_path, shared_app):
    """Verify that in test mode or with sample logs, anti-tamper does not reject drops when pso2.exe is not running."""
    sim = MockLogSimulator(str(tmp_path), initial_wallet=50000000)
    sim.write_initial_seed()
    sim.emit_meseta_drop(25000)
    sim.emit_meseta_drop(50000)

    app = shared_app
    app.log_folder = ""
    app.log_path = ""
    app.reset_data()
    # Enable test mode bypasses
    app._enable_test_mode_bypasses()
    app.anti_tamper.reset()
    assert app.is_test_mode is True
    assert app.anti_tamper.enforce_process_validation is False
    assert app.anti_tamper.enforce_timestamp_validation is False
    assert app.anti_tamper.enforce_velocity_validation is False

    # Read and process all lines directly
    app.log_path = sim.log_file
    with open(app.log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            if line.strip():
                app.process_log_line(line)

    assert app.current_wallet == 50075000
    assert app.session_meseta == 76000
    assert app.war_service.session_contribution == 76000
    assert app.anti_tamper.is_compromised is False
    assert app.war_service.is_tamper_compromised is False

    # Verify cloud sync succeeds
    ok, msg = app.war_service.sync_to_cloud_database()
    assert ok is True
    assert "สำเร็จ" in msg


def test_window_minimize_behavior(shared_app):
    """Verify that minimize_window sets iconic state and ignores premature <Map> events."""
    import time
    app = shared_app
    app.update()
    assert app.state() == "normal"

    # Trigger minimize
    app.minimize_window()
    app.update()

    # The window must remain iconic (not instantly restored)
    assert app.state() == "iconic"

    # Simulate user restoring window via OS/taskbar
    app.deiconify()
    app.update()
    app._on_restore_window()
    # Allow scheduled force_taskbar_icon (50ms) to fire and complete cleanly
    time.sleep(0.1)
    app.update()

    assert app.state() == "normal"


def test_title_bar_native_framework_and_controls(shared_app):
    """Verify title bar controls: version badge, maximize/restore toggle, and native drag integration."""
    import time
    from modules.utils import start_native_drag
    from config import CLIENT_VERSION

    app = shared_app
    time.sleep(0.1)
    app.update()
    # Verify version badge
    assert hasattr(app, "version_label")
    assert app.version_label.cget("text") == f"v{CLIENT_VERSION}"

    # Verify maximize/restore button
    assert hasattr(app, "max_btn")
    assert app.max_btn.cget("text") == "□"

    # Toggle maximize
    app.toggle_maximize()
    app.update()
    assert app.max_btn.cget("text") == "❐"

    # Toggle restore
    app.toggle_maximize()
    app.update()
    assert app.state() == "normal"
    assert app.max_btn.cget("text") == "□"

    # Verify WindowMover helper exists and moves safely
    class MockEvent:
        x_root = 120
        y_root = 120
    app.start_move(MockEvent())
    assert hasattr(app, "_window_mover")
    # Verify do_move executes without crashing
    app.do_move(MockEvent())


def test_window_mover_crash_free_execution(shared_app):
    """Verify WindowMover does not crash under rapid drag events."""
    from modules.utils import WindowMover
    mover = WindowMover(shared_app)
    class Evt:
        def __init__(self, x, y):
            self.x_root = x
            self.y_root = y

    mover.start_move(Evt(100, 100))
    for i in range(50):
        mover.do_move(Evt(100 + i, 100 + i))
    shared_app.update()
    assert True


def test_start_native_drag_backwards_compatibility():
    """Verify start_native_drag safe backwards compatibility wrapper."""
    from modules.utils import start_native_drag
    assert start_native_drag(None) is False
