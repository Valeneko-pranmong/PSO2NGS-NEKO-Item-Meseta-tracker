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
        kwargs["stats_file"] = str(test_appdata / "war_stats.json")
        orig_ws_init(self, war_room_path=war_room_path, **kwargs)
    monkeypatch.setattr(WarService, "__init__", patched_ws_init)

    yield


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
    assert war.parse_coordinate("0, 0") == (0, 0, 1)
    assert war.parse_coordinate("0, 0, 1") == (0, 0, 1)
    assert war.parse_coordinate("0,0#1") == (0, 0, 1)
    assert war.parse_coordinate("3, 3, 4") == (3, 3, 4)
    assert war.parse_coordinate("[0, 0, 1]") == (0, 0, 1)
    assert war.parse_coordinate('{"x": 0, "y": 0, "slot": 1}') == (0, 0, 1)
    assert war.parse_coordinate("[15, -8]") == (15, -8, 1)
    assert war.parse_coordinate("(4, 9)") == (4, 9, 1)
    assert war.parse_coordinate("X: 12, Y: -5") == (12, -5, 1)
    assert war.parse_coordinate({"x": -3, "y": 7}) == (-3, 7, 1)
    assert war.parse_coordinate([2, 6]) == (2, 6, 1)
    assert war.parse_coordinate("0, 0 NW") == (0, 0, 1)
    assert war.parse_coordinate("0, 0 SE") == (0, 0, 4)
    assert war.parse_coordinate("คัดลอกพิกัด [8, -2] ช่อง #3 ไปใส่ในโปรแกรม") == (8, -2, 3)

    # Test clamping bounds (-12..25, -11..9, 1..4)
    clamped = war.parse_coordinate("[-99, 99, 9]")
    assert (clamped.x, clamped.y, clamped.slot) == (-12, 9, 4)

    # Test setting target board coordinate
    parsed = war.set_target_coord("10, -4, 2")
    assert (parsed.x, parsed.y, parsed.slot) == (10, -4, 2)
    assert war.target_coord == (10, -4, 2)
    assert war.target_coord.slot == 2

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

    # User enters a coordinate with slot
    norm = app.update_board_coordinate("15, -6, 2")
    assert norm == "15, -6, 2"
    assert app.board_coord == "15, -6, 2"
    assert app.war_service.target_coord == (15, -6, 2)
    assert app.war_service.target_coord.slot == 2

    # Open war view and verify coordinate is displayed in banner entry
    app.show_war_view()
    app.update_idletasks()
    assert hasattr(app.war_view, "entry_coord")
    assert app.war_view.coord_var.get() == "15, -6, 2"

    # User clicks slot button #4
    app.war_view._on_slot_button_clicked(4)
    app.update_idletasks()
    assert app.board_coord == "15, -6, 4"
    assert app.war_service.target_coord == (15, -6, 4)
    assert app.war_view.coord_var.get() == "15, -6, 4"

    # User updates coordinate from war view
    app.war_view.coord_var.set("2, 8, 3")
    app.war_view._on_coord_submit()
    app.update_idletasks()
    assert app.board_coord == "2, 8, 3"
    assert app.war_service.target_coord == (2, 8, 3)
    assert app.war_view.coord_var.get() == "2, 8, 3"

    app.show_offline_view()


def test_database_payload_strictly_character_meseta_coord():
    """
    Verify database record payload contains strictly:
    - character_name: in-game name read from log (Primary Key, NOT ID)
    - meseta: meseta amount
    - sector_coord: board coordinate object {"x": X, "y": Y, "slot": Slot}
    - target_coord: board coordinate object {"x": X, "y": Y, "slot": Slot}
    - coord_key: "X,Y"
    - slot: 1-4
    - lastUpdated: integer timestamp in ms
    And does NOT contain team_name or team_id.
    """
    war = WarService()
    war.set_operative("Vale3neko")
    war.set_target_coord("5, -3, 2")
    war.session_contribution = 25000000

    payload = war.get_database_payload()

    assert payload["character_name"] == "Vale3neko"
    assert payload["character_name"] != "14743890"
    assert payload["meseta"] == 25000000
    assert payload["sector_coord"] == {"x": 5, "y": -3, "slot": 2}
    assert payload["target_coord"] == {"x": 5, "y": -3, "slot": 2}
    assert payload["coord_key"] == "5,-3"
    assert payload["slot"] == 2
    assert isinstance(payload["lastUpdated"], int)
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
    assert hasattr(wv, "btn_how_to_use")
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
    war.set_target_coord("3, -2, 1")

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
    assert tel_payload["sector_coord"] == {"x": 3, "y": -2, "slot": 1}
    assert tel_payload["target_coord"] == {"x": 3, "y": -2, "slot": 1}
    assert tel_payload["coord_key"] == "3,-2"
    assert tel_payload["slot"] == 1
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

    # Top right labels: lbl_war_status removed, lbl_sync_time remains
    assert getattr(wv, "lbl_war_status", None) is None
    assert hasattr(wv, "lbl_sync_time")

    # Button: btn_sync removed (sync is handled automatically in background)
    assert getattr(wv, "btn_sync", None) is None

    # Trigger events to verify dynamic updates
    event_bus.emit("realtime_sync_started")
    app.update_idletasks()
    txt_syncing = wv.lbl_sync_time.cget("text")
    assert ("กำลังซิงค์" in txt_syncing or "Syncing" in txt_syncing)

    event_bus.emit("realtime_sync_completed", success=True, timestamp=1789830000, contribution=150000)
    app.update_idletasks()
    txt_completed = wv.lbl_sync_time.cget("text")
    assert ("ล่าสุด" in txt_completed or "synced" in txt_completed.lower() or "last" in txt_completed.lower())
    assert "150,000" in txt_completed

    # Regression: Ensure sync label and save button are in distinct vertical rows
    app.update()
    assert wv.lbl_sync_time.master != wv.btn_save_coord.master
    sync_row_y = wv.lbl_sync_time.master.winfo_y()
    coord_row_y = wv.btn_save_coord.master.winfo_y()
    assert sync_row_y < coord_row_y

    app.show_offline_view()


def test_coordinate_paste_support_and_focus(shared_app, monkeypatch):
    """
    Verify coordinate paste support:
    - Dedicated paste button reads clipboard and auto-parses format
    - _handle_coord_paste handles dirty formats ([2, 8, 3], web text, etc.)
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

    # 1. Test clicking paste button with "[3, 7, 2]" in clipboard
    monkeypatch.setattr(wv, "clipboard_get", lambda: " [3, 7, 2] ")
    wv._on_paste_coord_clicked()
    app.update_idletasks()
    assert wv.coord_var.get() == "3, 7, 2"
    assert app.board_coord == "3, 7, 2"
    assert app.war_service.target_coord == (3, 7, 2)
    assert app.war_service.target_coord.slot == 2

    # 2. Test clicking paste button with web copy button label text with slot
    monkeypatch.setattr(wv, "clipboard_get", lambda: "คัดลอกพิกัด [8, -2] ช่อง #3 ไปใส่ในโปรแกรม")
    wv._on_paste_coord_clicked()
    app.update_idletasks()
    assert wv.coord_var.get() == "8, -2, 3"
    assert app.board_coord == "8, -2, 3"
    assert app.war_service.target_coord == (8, -2, 3)
    assert app.war_service.target_coord.slot == 3

    # 3. Test _handle_coord_paste (Ctrl+V / context menu paste)
    monkeypatch.setattr(wv, "clipboard_get", lambda: "(-4, 9, 4)")
    res = wv._handle_coord_paste()
    assert res == "break"
    assert wv.coord_var.get() == "-4, 9, 4"

    # 4. Test focus preservation: when entry is focused, update_view does NOT overwrite typed text
    wv.coord_var.set("typing_new_val")
    # Simulate focus on inner entry
    monkeypatch.setattr(wv, "focus_get", lambda: getattr(wv.entry_coord, "_entry", wv.entry_coord))
    wv.update_view()
    assert wv.coord_var.get() == "typing_new_val"

    # When NOT focused, update_view syncs with war_service target_coord
    monkeypatch.setattr(wv, "focus_get", lambda: None)
    wv.update_view()
    tc = app.war_service.target_coord
    assert wv.coord_var.get() == f"{tc.x}, {tc.y}, {tc.slot}"

    app.show_offline_view()


def test_open_web_war_room_opens_configured_url(shared_app, monkeypatch):
    """Verify that ARKS War Room (Web) action opens the configured URL."""
    import webbrowser
    from config import DEFAULT_WAR_ROOM_URL

    app = shared_app
    app.show_war_view()
    app.update_idletasks()
    wv = app.war_view

    opened_urls = []
    monkeypatch.setattr(webbrowser, "open", lambda url: opened_urls.append(url))

    wv._open_web_war_room()
    assert len(opened_urls) == 1
    assert opened_urls[0] == "https://arks-war-room.vercel.app/"
    assert opened_urls[0] == DEFAULT_WAR_ROOM_URL

    app.show_offline_view()


def test_firebase_war_sync_broadcaster():
    """Verify ARKSFirebaseBroadcaster in tools.firebase_war_sync can be imported and executed."""
    from tools.firebase_war_sync import ARKSFirebaseBroadcaster

    # Test initialization with None key (REST mode)
    broadcaster = ARKSFirebaseBroadcaster(
        service_account_key_path=None,
        database_url="https://mock-test-default-rtdb.firebaseio.com",
    )
    # Test method call signature
    broadcaster.sync_operative_sector(
        character_name="Vale3neko",
        meseta=25000000,
        sector_x=0,
        sector_y=0,
        slot=1,
    )

    # Test file not found error if bad path is passed
    with pytest.raises(FileNotFoundError):
        ARKSFirebaseBroadcaster(service_account_key_path="non_existent_key_12345.json")


def test_canonical_landmarks():
    """Verify landmark presets from Section 6 exist and match coordinates."""
    from modules.war_mode.war_service import LANDMARK_COORDINATES

    assert LANDMARK_COORDINATES["oracle_fleet"]["x"] == 0
    assert LANDMARK_COORDINATES["oracle_fleet"]["y"] == 0

    assert LANDMARK_COORDINATES["central_city"]["x"] == 3
    assert LANDMARK_COORDINATES["central_city"]["y"] == 3

    assert LANDMARK_COORDINATES["earth"]["x"] == 9
    assert LANDMARK_COORDINATES["earth"]["y"] == -3

    assert LANDMARK_COORDINATES["sun"]["x"] == 8
    assert LANDMARK_COORDINATES["sun"]["y"] == -3

    assert LANDMARK_COORDINATES["mars"]["x"] == 9
    assert LANDMARK_COORDINATES["mars"]["y"] == -4

    assert LANDMARK_COORDINATES["naberius"]["x"] == -2
    assert LANDMARK_COORDINATES["naberius"]["y"] == -2

    assert LANDMARK_COORDINATES["amduskia"]["x"] == -3
    assert LANDMARK_COORDINATES["amduskia"]["y"] == -3

    assert LANDMARK_COORDINATES["lillipa"]["x"] == -1
    assert LANDMARK_COORDINATES["lillipa"]["y"] == -3

    assert LANDMARK_COORDINATES["project_hail_mary"]["x"] == 20
    assert LANDMARK_COORDINATES["project_hail_mary"]["y"] == 7


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


def test_utils_formatting():
    """Verify shared formatting functions in modules.utils."""
    from modules.utils import format_compact, format_rate, format_duration

    assert format_compact(500) == "500"
    assert format_compact(15000) == "15.0k"
    assert format_compact(25000000) == "25.00M"
    assert format_compact(-1200000) == "-1.20M"

    assert format_rate(0) == "0 /hr"
    assert format_rate(-100) == "0 /hr"
    assert format_rate(500) == "500 /hr"
    assert format_rate(50000) == "50.0 k/hr"
    assert format_rate(2500000) == "2.50 M/hr"

    assert format_duration(-5) == "00:00:00"
    assert format_duration(65) == "00:01:05"
    assert format_duration(3665) == "01:01:05"


def test_utils_item_filtering():
    """Verify shared item filtering and sorting in modules.utils."""
    from modules.utils import filter_and_sort_items

    items = {
        "N-Grinder": 150,
        "Alpha Reactor": 14,
        "Photon Chunk": 80,
        "Arms Refiner": 5,
    }

    # All items sorted descending
    all_sorted = filter_and_sort_items(items)
    assert [name for name, _ in all_sorted] == [
        "N-Grinder",
        "Photon Chunk",
        "Alpha Reactor",
        "Arms Refiner",
    ]

    # Watchlist filtering
    wl_filtered = filter_and_sort_items(
        items, watchlist=["Reactor", "Refiner"], filter_enabled=True
    )
    assert set(name for name, _ in wl_filtered) == {"Alpha Reactor", "Arms Refiner"}

    # Empty watchlist when filter enabled returns empty list
    empty_wl = filter_and_sort_items(items, watchlist=[], filter_enabled=True)
    assert empty_wl == []

    # Keyword search
    kw_filtered = filter_and_sort_items(items, keyword="photon")
    assert [name for name, _ in kw_filtered] == ["Photon Chunk"]

    # Max items limit
    capped = filter_and_sort_items(items, max_items=2)
    assert len(capped) == 2


def test_utils_character_extraction():
    """Verify ActionLog character extraction helper in modules.utils."""
    from modules.utils import extract_character_info

    valid_line = "2026-09-20T12:00:00\t001\t[Pickup]\t10023456\tNekoHero\tMeseta(1000)"
    assert extract_character_info(valid_line) == ("NekoHero", "10023456")

    invalid_line = "2026-09-20T12:00:00\t001\t[Notice]\tSystem"
    assert extract_character_info(invalid_line) is None

    no_digit_id = "2026-09-20T12:00:00\t001\t[Pickup]\tABCDEF\tNekoHero"
    assert extract_character_info(no_digit_id) is None


def test_target_coord_hash_and_dict_consistency():
    """Verify TargetCoord hash consistency and correct dict/set lookup behavior."""
    from modules.war_mode.war_service import TargetCoord

    tc = TargetCoord(3, -2, 1)
    # TargetCoord equals identical 3-part tuple
    assert tc == (3, -2, 1)
    # Does NOT equal 2-part tuple, avoiding hash divergence
    assert tc != (3, -2)
    assert hash(tc) == hash((3, -2, 1))

    # Dict lookup works with both TargetCoord and equivalent tuple
    d = {tc: "active_mission"}
    assert d[(3, -2, 1)] == "active_mission"
    assert (3, -2, 1) in {tc}


def test_war_logs_thread_safety_and_limit():
    """Verify war_logs thread safety lock and bounding to 50 items."""
    from modules.war_mode.war_service import WarService

    war = WarService()
    for i in range(60):
        war.add_log(f"Test log entry {i}", "info")

    assert len(war.war_logs) == 50
    recent = war.get_recent_logs(5)
    assert len(recent) == 5
    assert recent[0]["text"] == "Test log entry 59"
    war.stop()


def test_version_security_semver_helpers():
    """Verify semantic version parsing, comparison, and security verification."""
    from modules.war_mode.war_service import parse_semver, compare_semver, is_version_secure

    # 1. Parsing
    assert parse_semver("7.1.0") == (7, 1, 0, "")
    assert parse_semver("V 7.1.0") == (7, 1, 0, "")
    assert parse_semver("7.0.0-alpha") == (7, 0, 0, "alpha")

    # 2. Comparisons
    assert compare_semver("7.1.0", "7.0.0") == 1
    assert compare_semver("7.0.0-alpha", "7.0.0") == -1
    assert compare_semver("7.0.0-alpha", "7.1.0") == -1
    assert compare_semver("7.1.0", "7.1.0") == 0
    assert compare_semver("7.2.0", "7.1.0") == 1

    # 3. Security verification
    assert is_version_secure("7.1.0") is True
    assert is_version_secure("7.2.0") is True
    # Insecure / revoked versions: 7.0.0-alpha, 7.0.0, 6.1.0
    assert is_version_secure("7.0.0-alpha") is False
    assert is_version_secure("7.0.0") is False
    assert is_version_secure("6.1.0") is False
    assert is_version_secure("") is False


def test_database_payload_contains_version_and_security_status():
    """Verify that database payload sends client_version, version, and security_status."""
    from modules.war_mode.war_service import WarService

    war = WarService(client_version="7.1.0")
    war.set_operative("SecurityTester")
    war.set_target_coord("3, 3, 1")
    war.session_contribution = 10_000_000

    payload = war.get_database_payload()
    assert payload["client_version"] == "7.1.0"
    assert payload["version"] == "7.1.0"
    assert payload["security_status"] == "SECURE"
    assert payload["version_security_valid"] is True
    assert payload["meseta"] == 10_000_000
    war.stop()


def test_insecure_version_7_0_0_alpha_uncounted_in_database():
    """
    Verify that if a client uses 7.0.0-alpha (which was revoked due to security bugs),
    the meseta sent to database records is NOT counted (meseta=0), security_status is flagged,
    and cloud sync refuses to credit the sector.
    """
    from modules.war_mode.war_service import WarService

    war = WarService(client_version="7.0.0-alpha")
    war.set_operative("VulnerablePlayer")
    war.set_target_coord("0, 0, 1")
    war.session_contribution = 25_000_000

    assert war.is_version_secure() is False

    payload = war.get_database_payload()
    assert payload["client_version"] == "7.0.0-alpha"
    assert payload["version_security_valid"] is False
    assert payload["security_status"] == "REVOKED_VERSION_INSECURE"
    # CRITICAL: Money must NOT be counted into database records!
    assert payload["meseta"] == 0
    assert payload["raw_meseta"] == 25_000_000
    assert payload["farming_rate_mhr"] == 0

    # Sync to cloud database must reject unsecure client
    ok, msg = war.sync_to_cloud_database()
    assert ok is False
    assert "7.0.0-alpha" in msg
    assert ("ความปลอดภัย" in msg or "security" in msg.lower())
    war.stop()


def test_firebase_war_sync_broadcaster_version_security():
    """Verify ARKSFirebaseBroadcaster validates client_version and rejects insecure versions."""
    from tools.firebase_war_sync import ARKSFirebaseBroadcaster

    broadcaster = ARKSFirebaseBroadcaster(
        database_url="https://mock-test-default-rtdb.firebaseio.com"
    )

    assert broadcaster.is_version_secure("7.1.0") is True
    assert broadcaster.is_version_secure("7.0.0-alpha") is False
    assert broadcaster.is_version_secure("6.1.0") is False


def test_remote_version_control_policy_and_check():
    """Verify fetching and evaluating dynamic version control policy."""
    from modules.war_mode.war_service import WarService

    # 1. Test evaluation with mocked policy (Latest secure version)
    war = WarService(client_version="7.1.0")
    war.remote_policy = {
        "latest_version": "7.2.0",
        "min_secure_version": "7.1.0",
        "revoked_versions": {"7_0_0-alpha": True, "7_0_0": True},
        "announcement": "New update 7.2.0 available",
        "download_url": "https://example.com/dl",
    }
    war.latest_version = "7.2.0"
    war.min_secure_version = "7.1.0"
    war.revoked_versions = ["7.0.0-alpha", "7.0.0"]
    war.remote_policy_fetched = True

    status = war.check_version_status()
    assert status["current_version"] == "7.1.0"
    assert status["latest_version"] == "7.2.0"
    assert status["is_secure"] is True
    assert status["is_latest"] is False
    assert status["status"] == "UPDATE_AVAILABLE"
    assert "7.2.0" in status["message"]

    # 2. Test when client is latest
    war.client_version = "7.2.0"
    status_latest = war.check_version_status()
    assert status_latest["is_secure"] is True
    assert status_latest["is_latest"] is True
    assert status_latest["status"] == "SECURE_LATEST"

    # 3. Test when client is revoked
    war.client_version = "7.0.0-alpha"
    status_revoked = war.check_version_status()
    assert status_revoked["is_secure"] is False
    assert status_revoked["status"] == "REVOKED_INSECURE"
    assert "เพิกถอน" in status_revoked["message"]

    # 4. Test when client is outdated below min_secure_version
    war.client_version = "6.1.0"
    status_outdated = war.check_version_status()
    assert status_outdated["is_secure"] is False
    assert status_outdated["status"] == "OUTDATED_INSECURE"

    war.stop()


def test_broadcaster_version_control_policy_methods(monkeypatch):
    """Verify ARKSFirebaseBroadcaster fetch and update version policy methods."""
    from tools.firebase_war_sync import ARKSFirebaseBroadcaster

    broadcaster = ARKSFirebaseBroadcaster(
        database_url="https://mock-rtdb.firebaseio.com"
    )

    fake_json = json.dumps({
        "latest_version": "7.1.0",
        "min_secure_version": "7.1.0",
        "revoked_versions": {"7_0_0-alpha": True},
    }).encode("utf-8")

    class FakeResponse:
        def __init__(self, data):
            self.data = data
        def read(self):
            return self.data
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda req, timeout=5.0: FakeResponse(fake_json),
    )

    policy = broadcaster.fetch_version_control_policy()
    assert policy["latest_version"] == "7.1.0"
    assert policy["min_secure_version"] == "7.1.0"

    ok = broadcaster.update_version_control_policy(
        latest_version="7.1.0",
        min_secure_version="7.1.0",
        announcement="System OK",
    )
    assert ok is True


def test_overlay_mini_layout_not_clipped(shared_app):
    """
    Verify OverlayWindow in mini mode:
    - Has sufficient window height so that lbl_time_overlay and lbl_mhr_overlay are not clipped.
    - Accurately renders TIME and RATE statistics when updated.
    """
    from unittest.mock import MagicMock
    import time
    from overlay_ui import OverlayWindow

    controller = MagicMock()
    controller.session_meseta = 117952
    controller.current_wallet = 169072
    controller.first_drop_time = time.time() - 473
    controller.item_counts = {}
    controller.watchlist_items = set()
    controller.search_keyword = ""
    controller.is_filter_active = False

    overlay = OverlayWindow(controller, mode="mini")
    try:
        overlay.update()
        win_h = overlay.winfo_height()
        assert win_h >= 240

        time_bottom = (overlay.lbl_time_overlay.winfo_rooty() - overlay.winfo_rooty()) + overlay.lbl_time_overlay.winfo_height()
        rate_bottom = (overlay.lbl_mhr_overlay.winfo_rooty() - overlay.winfo_rooty()) + overlay.lbl_mhr_overlay.winfo_height()

        assert time_bottom <= win_h
        assert rate_bottom <= win_h

        assert overlay.lbl_time_overlay.cget("text") == "00:07:53"
        assert "k/hr" in overlay.lbl_mhr_overlay.cget("text")
        assert overlay.lbl_money.cget("text") == "+118.0k"
        assert "169,072" in overlay.lbl_wallet_overlay.cget("text")
    finally:
        overlay.destroy()


def test_sidebar_and_war_view_status_frame_not_clipped(shared_app):
    """
    Verify both Offline View sidebar and War View card_menu:
    - Status frame is mapped and has height >= 40px.
    - btn_select ("Select Log Folder") is mapped, visible, and has height >= 24px.
    - lbl_file_status is mapped and visible.
    - btn_how_to_use and btn_discord are both mapped and visible.
    """
    app = shared_app
    app.update()

    # 1. Offline View Sidebar Checks
    assert hasattr(app, "status_frame")
    assert app.status_frame.winfo_ismapped()
    assert app.status_frame.winfo_height() >= 40
    assert hasattr(app, "btn_select")
    assert app.btn_select.winfo_ismapped()
    assert app.btn_select.winfo_height() >= 24
    assert hasattr(app, "lbl_file_status")
    assert app.lbl_file_status.winfo_ismapped()

    # 2. War View Menu Checks
    app.show_war_view()
    app.update()
    wv = app.war_view

    assert hasattr(wv, "status_frame")
    assert wv.status_frame.winfo_ismapped()
    assert wv.status_frame.winfo_height() >= 40
    assert hasattr(wv, "btn_select")
    assert wv.btn_select.winfo_ismapped()
    assert wv.btn_select.winfo_height() >= 24
    assert hasattr(wv, "lbl_file_status")
    assert wv.lbl_file_status.winfo_ismapped()
    assert hasattr(wv, "btn_how_to_use")
    assert wv.btn_how_to_use.winfo_ismapped()
    assert hasattr(wv, "btn_discord")
    assert wv.btn_discord.winfo_ismapped()


def test_calculate_live_rate_and_cold_start_smoothing():
    """Verify live Meseta/hr calculation with cold-start smoothing."""
    from modules.utils import calculate_live_rate

    # Zero or negative income
    assert calculate_live_rate(0, 100) == 0.0
    assert calculate_live_rate(-500, 100) == 0.0

    # Cold start (duration < 30s): smoothed with 30s floor even at duration=0s
    # 50,000 meseta in 2 seconds would naively be 90,000,000/hr (spike)
    # With smoothing: (50000 / 30) * 3600 = 6,000,000/hr
    rate_0s = calculate_live_rate(50000, 0.0, min_smoothing_seconds=30.0)
    assert rate_0s == 6_000_000.0
    rate_2s = calculate_live_rate(50000, 2.0, min_smoothing_seconds=30.0)
    assert rate_2s == 6_000_000.0

    # Normal duration (duration >= 30s): exact calculation
    # 1,000,000 meseta in 1800 seconds (30 mins) = 2,000,000/hr
    rate_30m = calculate_live_rate(1_000_000, 1800.0)
    assert rate_30m == 2_000_000.0


def test_war_service_live_rate_lifecycle_and_reset():
    """Verify WarService manages first_farming_time, cold start, and reset properly."""
    from modules.war_mode.war_service import WarService

    war = WarService()
    assert war.first_farming_time is None
    assert war.get_live_rate() == 0.0

    # Earn meseta: sets first_farming_time
    war.on_meseta_earned(100000)
    assert war.first_farming_time is not None
    assert war.session_contribution == 100000
    assert war.get_live_rate() > 0.0

    # Reset: clears first_farming_time and resets rate to 0
    war.on_tracker_reset()
    assert war.first_farming_time is None
    assert war.session_contribution == 0
    assert war.get_live_rate() == 0.0

    # Tamper compromised: rate must be 0
    war.on_meseta_earned(50000)
    war.is_tamper_compromised = True
    assert war.get_live_rate() == 0.0

    war.stop()


def test_war_service_database_payload_includes_rate_fields():
    """Verify database payload and telemetry contain farming_rate_mhr and aliases."""
    from modules.war_mode.war_service import WarService

    war = WarService()
    war.set_operative("SpeedyHero")
    war.on_meseta_earned(300000)

    payload = war.get_database_payload()
    assert "farming_rate_mhr" in payload
    assert "farmingRateMhr" in payload
    assert "meseta_per_hour" in payload
    assert payload["farming_rate_mhr"] > 0
    assert payload["farming_rate_mhr"] == payload["farmingRateMhr"] == payload["meseta_per_hour"]

    # Cloud sync executes and sends rate
    ok, msg = war.sync_to_cloud_database()
    assert ok is True

    war.stop()


def test_firebase_broadcaster_sync_with_farming_rate():
    """Verify ARKSFirebaseBroadcaster includes farming_rate_mhr in payloads."""
    from tools.firebase_war_sync import ARKSFirebaseBroadcaster

    broadcaster = ARKSFirebaseBroadcaster(
        database_url="https://mock-test-default-rtdb.firebaseio.com"
    )

    # Sync with farming_rate_mhr
    ok = broadcaster.sync_operative_sector(
        character_name="TestHero",
        meseta=5_000_000,
        sector_x=1,
        sector_y=2,
        slot=1,
        client_version="7.1.0",
        farming_rate_mhr=2_500_000,
    )
    assert ok is True


