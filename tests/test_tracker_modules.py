import os
import sys
import json
import pytest

# Ensure root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from modules.event_bus import EventBus, event_bus
from modules.war_mode.war_service import WarService, TEAMS_DATA
from meseta_tracker import NGSTrackerApp


@pytest.fixture(autouse=True)
def isolate_test_environment(tmp_path, monkeypatch):
    """Ensure all tests run completely sandboxed from real app storage and mock data."""
    test_appdata = tmp_path / "appdata"
    test_appdata.mkdir(parents=True, exist_ok=True)
    test_war_room = tmp_path / "war_room"
    test_war_room.mkdir(parents=True, exist_ok=True)

    orig_ws_init = WarService.__init__
    def patched_ws_init(self, war_room_path=str(test_war_room), **kwargs):
        orig_ws_init(self, war_room_path=war_room_path, **kwargs)
        self.stats_file = str(test_appdata / "war_stats.json")
    monkeypatch.setattr(WarService, "__init__", patched_ws_init)

    yield


@pytest.fixture(scope="module")
def shared_app():
    """Shared GUI app instance for module to prevent repeated Tk re-initialization crashes."""
    app = NGSTrackerApp()
    app.update_idletasks()
    yield app
    try:
        app.destroy()
    except Exception:
        pass


def test_event_bus_pub_sub():
    bus = EventBus()
    received = []

    def handler(amount=0, **kwargs):
        received.append(amount)

    bus.subscribe("test_meseta", handler)
    bus.emit("test_meseta", amount=1000)
    assert received == [1000]

    bus.unsubscribe("test_meseta", handler)
    bus.emit("test_meseta", amount=2000)
    assert received == [1000]


def test_login_system_removed_from_app(shared_app):
    """
    Verify the login system has been completely removed:
    - No auth_service or auth_view on app
    - No login forms, usernames, or passwords required
    - War mode is accessed immediately with zero login friction
    - No logout button in war view
    """
    app = shared_app
    app.update_idletasks()

    # 1. Verify app does not have auth_service or auth_view
    assert hasattr(app, "auth_service") is False
    assert hasattr(app, "auth_view") is False

    # 2. Start in offline view
    app.show_offline_view()
    app.update_idletasks()
    assert app.current_view == "offline"
    assert bool(app.offline_container.grid_info()) is True

    # 3. Enter war mode directly without ANY login prompt
    app.enter_war_mode()
    app.update_idletasks()
    assert app.current_view == "war"
    assert bool(app.war_view.grid_info()) is True
    assert bool(app.offline_container.grid_info()) is False

    # 4. War view has NO logout button
    assert hasattr(app.war_view, "btn_logout") is False

    # 5. Return to offline view
    app.show_offline_view()
    app.update_idletasks()
    assert app.current_view == "offline"
    assert bool(app.offline_container.grid_info()) is True


def test_war_service_telemetry_and_board_coord():
    """Verify WarService tracks contributions, parses board coordinates, and produces clean payload."""
    war = WarService()
    war.set_operative("TestHero")
    assert war.operative_name == "TestHero"

    # Test coordinate parsing
    assert war.parse_coordinate("0, 0") == (0, 0)
    assert war.parse_coordinate("[15, -8]") == (15, -8)
    assert war.parse_coordinate("(4, 9)") == (4, 9)
    assert war.parse_coordinate("X: 12, Y: -5") == (12, -5)
    assert war.parse_coordinate({"x": -3, "y": 7}) == (-3, 7)
    assert war.parse_coordinate([2, 6]) == (2, 6)

    # Test setting target board coordinate
    gx, gy = war.set_target_coord("10, -4")
    assert (gx, gy) == (10, -4)
    assert war.target_coord == (10, -4)

    # Test earning Meseta
    start_contrib = war.session_contribution
    war.on_meseta_earned(amount=850000)
    assert war.session_contribution == start_contrib + 850000

    # Test sync to local war room
    ok, msg = war.sync_to_war_room()
    assert ok is True

    # Test reset
    war.on_tracker_reset()
    assert war.session_contribution == 0
    war.stop()


def test_character_name_extracted_from_log_is_primary_key(shared_app):
    """
    Verify in-game character name (and NOT the player ID) is extracted from ActionLog lines
    and serves as the Primary Key for Firebase syncing.
    Line format: Timestamp \t Seq \t [Action] \t PlayerID \t CharacterName \t ...
    """
    app = shared_app

    # Simulated line with Player ID 14743890 and In-Game Name Vale3neko
    line = "2026-09-19T20:00:11\t102\t[Pickup]\t14743890\tVale3neko\tN-Meseta(1500)\tNum(1)\n"
    app.process_log_line(line)

    assert app.character_name == "Vale3neko"
    assert app.character_name != "14743890"  # Must NOT be ID
    assert app.player_id == "14743890"

    # WarService operative must match in-game name as Primary Key
    assert app.war_service.operative_name == "Vale3neko"


def test_board_coordinate_entry_and_synchronization(shared_app):
    """
    Verify the user can enter board coordinates in the War View UI and they synchronize
    across the controller, war view, config, and database payload.
    """
    app = shared_app
    app.update_idletasks()

    # User enters a coordinate
    norm = app.update_board_coordinate("15, -6")
    assert norm == "15, -6"
    assert app.board_coord == "15, -6"
    assert app.war_service.target_coord == (15, -6)

    # Open war view and verify coordinate is displayed in banner entry
    app.show_war_view()
    app.update_idletasks()
    assert hasattr(app.war_view, "entry_coord")
    assert app.war_view.coord_var.get() == "15, -6"

    # User updates coordinate from war view
    app.war_view.coord_var.set("2, 8")
    app.war_view._on_coord_submit()
    app.update_idletasks()
    assert app.board_coord == "2, 8"
    assert app.war_service.target_coord == (2, 8)
    assert app.war_view.coord_var.get() == "2, 8"

    app.show_offline_view()


def test_database_payload_strictly_character_meseta_coord():
    """
    Verify database record payload contains strictly:
    - character_name: in-game name read from log (Primary Key, NOT ID)
    - meseta: meseta amount
    - sector_coord: board coordinate string "X, Y"
    - target_coord: board coordinate object {"x": X, "y": Y}
    - coord_key: "X,Y"
    And does NOT contain team_name or team_id.
    """
    war = WarService()
    war.set_operative("Vale3neko")
    war.set_target_coord("5, -3")
    war.session_contribution = 2500000

    payload = war.get_database_payload()

    assert payload["character_name"] == "Vale3neko"
    assert payload["character_name"] != "14743890"
    assert payload["meseta"] == 2500000
    assert payload["sector_coord"] == "5, -3"
    assert payload["target_coord"] == {"x": 5, "y": -3}
    assert payload["coord_key"] == "5,-3"
    assert "team_name" not in payload
    assert "team_id" not in payload


def test_war_view_menu_replaces_chronicle(shared_app):
    """
    Verify the offline-style sidebar menu is present on the left and full dashboard on the right.
    """
    app = shared_app
    app.update_idletasks()

    app.show_war_view()
    app.update_idletasks()

    assert app.current_view == "war"
    wv = app.war_view

    # 1. Main menu panel is present on the left (column 0)
    assert hasattr(wv, "card_menu")
    assert wv.card_menu.grid_info()["column"] == 0
    assert hasattr(wv, "btn_reset")
    assert hasattr(wv, "btn_watchlist")
    assert hasattr(wv, "switch_filter")
    assert hasattr(wv, "btn_overlay_full")
    assert hasattr(wv, "btn_overlay_mini")
    assert hasattr(wv, "btn_discord")
    assert hasattr(wv, "lbl_file_status")
    assert hasattr(wv, "btn_select")
    assert hasattr(wv, "lbl_version")

    # 2. Complete Tracker Dashboard is present on the right (column 1)
    assert hasattr(wv, "dashboard_area")
    assert wv.dashboard_area.grid_info()["column"] == 1
    assert hasattr(wv.dashboard_area, "lbl_session")
    assert hasattr(wv.dashboard_area, "lbl_wallet")
    assert hasattr(wv.dashboard_area, "lbl_time")
    assert hasattr(wv.dashboard_area, "lbl_mhr")
    assert hasattr(wv.dashboard_area, "scroll")
    assert hasattr(wv.dashboard_area, "search_var")

    # 3. Filter toggle synchronization
    wv.switch_filter.select()
    wv._on_toggle_filter()
    app.update_idletasks()
    assert app.is_filter_active is True
    assert app.switch_filter.get() == 1

    wv.switch_filter.deselect()
    wv._on_toggle_filter()
    app.update_idletasks()
    assert app.is_filter_active is False
    assert app.switch_filter.get() == 0

    app.show_offline_view()


def test_realtime_sync_event_triggers_and_db_flow():
    """Verify that earning meseta and resets automatically trigger realtime sync with board coordinate."""
    war = WarService()
    war.set_operative("RealtimeHero")
    war.set_target_coord("3, -2")

    assert war.realtime_sync_enabled is True
    war._is_dirty = False
    war._sync_event.clear()

    events_received = []
    def on_sync_started(**kwargs):
        events_received.append("started")
    def on_sync_completed(**kwargs):
        events_received.append("completed")
    def on_telemetry(payload=None, **kwargs):
        events_received.append(payload)

    event_bus.subscribe("realtime_sync_started", on_sync_started)
    event_bus.subscribe("realtime_sync_completed", on_sync_completed)
    event_bus.subscribe("war_telemetry_synced", on_telemetry)

    # 1. Earn meseta
    war.on_meseta_earned(amount=250000)
    assert war._is_dirty is True
    assert war._sync_event.is_set() is True

    ok, res_msg = war._execute_realtime_cycle()
    assert ok is True
    assert "started" in events_received
    assert "completed" in events_received

    # Verify telemetry payload contains character_name, meseta, and board coordinates
    tel_payload = next(p for p in reversed(events_received) if isinstance(p, dict) and p.get("character_name") == "RealtimeHero")
    assert tel_payload["character_name"] == "RealtimeHero"
    assert tel_payload["meseta"] == 250000
    assert tel_payload["sector_coord"] == "3, -2"
    assert tel_payload["target_coord"] == {"x": 3, "y": -2}
    assert "team_name" not in tel_payload
    assert "team_id" not in tel_payload

    # 2. Reset
    war.on_tracker_reset()
    assert war._is_dirty is True
    assert war._sync_event.is_set() is True
    assert war.session_contribution == 0

    ok, res_msg = war._execute_realtime_cycle()
    assert ok is True

    war.stop()
    event_bus.unsubscribe("realtime_sync_started", on_sync_started)
    event_bus.unsubscribe("realtime_sync_completed", on_sync_completed)
    event_bus.unsubscribe("war_telemetry_synced", on_telemetry)


def test_war_view_realtime_sync_ui_labels(shared_app):
    """Verify WarDashboardFrame UI labels and button reflect Realtime sync."""
    app = shared_app
    app.update_idletasks()

    app.show_war_view()
    app.update_idletasks()

    wv = app.war_view

    # Top right labels
    assert "REALTIME" in wv.lbl_war_status.cget("text")
    assert hasattr(wv, "lbl_sync_time")

    # Button text
    assert "เรียลไทม์" in wv.btn_sync.cget("text") or "Realtime" in wv.btn_sync.cget("text")

    # Trigger events to verify dynamic updates
    event_bus.emit("realtime_sync_started")
    app.update_idletasks()
    assert "กำลังซิงค์" in wv.lbl_sync_time.cget("text")

    event_bus.emit("realtime_sync_completed", success=True, timestamp=1789830000, contribution=150000)
    app.update_idletasks()
    assert "ล่าสุด" in wv.lbl_sync_time.cget("text")
    assert "150,000" in wv.lbl_sync_time.cget("text")

    app.show_offline_view()


def test_coordinate_paste_support_and_focus(shared_app, monkeypatch):
    """
    Verify coordinate paste support:
    - Dedicated paste button reads clipboard and auto-parses format
    - _handle_coord_paste handles dirty formats ([2, 8], web text, etc.)
    - update_view preserves in-progress coordinate input when entry is focused
    """
    app = shared_app
    app.update_idletasks()
    app.show_war_view()
    app.update_idletasks()

    wv = app.war_view
    assert hasattr(wv, "btn_paste_coord")
    assert hasattr(wv, "_on_paste_coord_clicked")
    assert hasattr(wv, "_handle_coord_paste")

    # 1. Test clicking paste button with "[3, 7]" in clipboard
    monkeypatch.setattr(wv, "clipboard_get", lambda: " [3, 7] ")
    wv._on_paste_coord_clicked()
    app.update_idletasks()
    assert wv.coord_var.get() == "3, 7"
    assert app.board_coord == "3, 7"
    assert app.war_service.target_coord == (3, 7)

    # 2. Test clicking paste button with web copy button label text
    monkeypatch.setattr(wv, "clipboard_get", lambda: "คัดลอกพิกัด [8, -2] ไปใส่ในโปรแกรม")
    wv._on_paste_coord_clicked()
    app.update_idletasks()
    assert wv.coord_var.get() == "8, -2"
    assert app.board_coord == "8, -2"
    assert app.war_service.target_coord == (8, -2)

    # 3. Test _handle_coord_paste (Ctrl+V / context menu paste)
    monkeypatch.setattr(wv, "clipboard_get", lambda: "(-4, 11)")
    res = wv._handle_coord_paste()
    assert res == "break"
    assert wv.coord_var.get() == "-4, 11"

    # 4. Test focus preservation: when entry is focused, update_view does NOT overwrite typed text
    wv.coord_var.set("typing_new_val")
    # Simulate focus on inner entry
    monkeypatch.setattr(wv, "focus_get", lambda: getattr(wv.entry_coord, "_entry", wv.entry_coord))
    wv.update_view()
    assert wv.coord_var.get() == "typing_new_val"

    # When NOT focused, update_view syncs with war_service target_coord
    monkeypatch.setattr(wv, "focus_get", lambda: None)
    wv.update_view()
    gx, gy = app.war_service.target_coord
    assert wv.coord_var.get() == f"{gx}, {gy}"

    app.show_offline_view()


def test_font_registration_and_config(shared_app):
    from config import FONT_FAMILY, FONT_HEADER, FONT_NORMAL, _sarabun_available
    import tkinter.font as tkfont

    families = tkfont.families(shared_app)

    assert FONT_FAMILY in ["Sarabun", "Kanit", "Leelawadee UI", "Segoe UI"]
    if _sarabun_available:
        assert "Sarabun" in families
        assert FONT_FAMILY == "Sarabun"
    assert FONT_HEADER[0] == FONT_FAMILY
    assert FONT_NORMAL[0] == FONT_FAMILY
