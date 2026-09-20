from __future__ import annotations

import json
import os
import re
import time
import threading
from typing import Any, Dict, List, Optional, Tuple, Union
import urllib.request
import urllib.parse
import urllib.error

try:
    from ..event_bus import event_bus
except (ImportError, ValueError):
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from modules.event_bus import event_bus

TEAMS_DATA: Dict[str, Dict[str, Any]] = {}

try:
    from config import (
        DEFAULT_FIREBASE_RTDB_URL,
        SECTOR_X_MIN,
        SECTOR_X_MAX,
        SECTOR_Y_MIN,
        SECTOR_Y_MAX,
        SLOT_MIN,
        SLOT_MAX,
        SLOT_TARGET_MESETA,
        SECTOR_TARGET_MESETA,
    )
except Exception:
    DEFAULT_FIREBASE_RTDB_URL = "https://arks-war-room-default-rtdb.asia-southeast1.firebasedatabase.app"
    SECTOR_X_MIN = -12
    SECTOR_X_MAX = 25
    SECTOR_Y_MIN = -11
    SECTOR_Y_MAX = 9
    SLOT_MIN = 1
    SLOT_MAX = 4
    SLOT_TARGET_MESETA = 25_000_000
    SECTOR_TARGET_MESETA = 100_000_000

# Canonical landmark coordinates for ARKS galaxy presets
LANDMARK_COORDINATES: Dict[str, Dict[str, Any]] = {
    "oracle_fleet": {"name": "Galactic Core / Oracle Fleet", "x": 0, "y": 0, "desc": "ใจกลางจักรวาล"},
    "central_city": {"name": "Halpha / Central City (PSO2: NGS)", "x": 3, "y": 3, "desc": "เมืองศูนย์กลาง NGS"},
    "earth": {"name": "Solar System (โลก / Earth)", "x": 9, "y": -3, "desc": "ดาวโลก"},
    "sun": {"name": "Solar System (ดวงอาทิตย์ / Sun)", "x": 8, "y": -3, "desc": "ดวงอาทิตย์"},
    "mars": {"name": "Mars (ดาวอังคาร)", "x": 9, "y": -4, "desc": "ดาวอังคาร"},
    "naberius": {"name": "Naberius (PSO2: Base)", "x": -2, "y": -2, "desc": "ดาวนาเบเรียส"},
    "amduskia": {"name": "Amduskia", "x": -3, "y": -3, "desc": "ดาวอัมดุสเกีย"},
    "lillipa": {"name": "Lillipa", "x": -1, "y": -3, "desc": "ดาวลิลลิปา"},
    "project_hail_mary": {"name": "Project Hail Mary (Deep Space Outpost)", "x": 20, "y": 7, "desc": "ฐานอวกาศลึก"},
}


class TargetCoord(tuple):
    """
    Represents a discrete 3-part coordinate: (sector_x, sector_y, slot).
    - sector_x: int between -12 and +25 (inclusive)
    - sector_y: int between -11 and +9 (inclusive)
    - slot: int between 1 and 4 (inclusive: 1=NW, 2=NE, 3=SW, 4=SE)
    Supports:
    - Indexing: coord[0], coord[1], coord[2]
    - Unpacking: gx, gy, slot = coord
    - Properties: coord.x, coord.y, coord.sector_x, coord.sector_y, coord.slot, coord.slot_label
    - Equality: (x, y, slot) == (x, y, slot); also (x, y) == (x, y) for backward compatibility
    """
    SECTOR_X_MIN = SECTOR_X_MIN
    SECTOR_X_MAX = SECTOR_X_MAX
    SECTOR_Y_MIN = SECTOR_Y_MIN
    SECTOR_Y_MAX = SECTOR_Y_MAX
    SLOT_MIN = SLOT_MIN
    SLOT_MAX = SLOT_MAX

    SLOT_INFO = {
        1: {"name": "NW", "th": "บนซ้าย", "target": SLOT_TARGET_MESETA},
        2: {"name": "NE", "th": "บนขวา", "target": SLOT_TARGET_MESETA},
        3: {"name": "SW", "th": "ล่างซ้าย", "target": SLOT_TARGET_MESETA},
        4: {"name": "SE", "th": "ล่างขวา", "target": SLOT_TARGET_MESETA},
    }

    def __new__(cls, x: Any, y: Any, slot: Any = 1):
        cx = max(cls.SECTOR_X_MIN, min(cls.SECTOR_X_MAX, int(x)))
        cy = max(cls.SECTOR_Y_MIN, min(cls.SECTOR_Y_MAX, int(y)))
        cslot = max(cls.SLOT_MIN, min(cls.SLOT_MAX, int(slot) if slot is not None else 1))
        return super().__new__(cls, (cx, cy, cslot))

    @property
    def x(self) -> int:
        return self[0]

    @property
    def y(self) -> int:
        return self[1]

    @property
    def sector_x(self) -> int:
        return self[0]

    @property
    def sector_y(self) -> int:
        return self[1]

    @property
    def slot(self) -> int:
        return self[2]

    @property
    def slot_name(self) -> str:
        return self.SLOT_INFO.get(self[2], {}).get("name", f"Slot {self[2]}")

    @property
    def slot_label(self) -> str:
        info = self.SLOT_INFO.get(self[2], {"name": f"Slot #{self[2]}", "th": ""})
        return f"#{self[2]} {info['name']} ({info['th']})"

    @property
    def coord_key(self) -> str:
        return f"{self[0]},{self[1]}"

    def to_dict(self) -> Dict[str, int]:
        return {"x": self[0], "y": self[1], "slot": self[2]}

    def to_str(self) -> str:
        return f"{self[0]}, {self[1]}, {self[2]}"

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return f"TargetCoord(x={self[0]}, y={self[1]}, slot={self[2]})"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, (tuple, list)):
            if len(other) == 2:
                return (self[0], self[1]) == (other[0], other[1])
            if len(other) == 3:
                return (self[0], self[1], self[2]) == (other[0], other[1], other[2])
        return super().__eq__(other)


class WarService:
    """
    Manages ARKS War Room campaign telemetry, farm contributions, and board coordinates.
    Decoupled from core tracker via EventBus.
    Primary Key: In-game character name read from log.
    Includes Realtime Sync Worker for instantaneous telemetry & Firebase RTDB updates.
    """

    def __init__(
        self,
        war_room_path: str = "E:/ARKS War Room",
        firebase_url: Optional[str] = DEFAULT_FIREBASE_RTDB_URL,
        realtime_sync: bool = True,
        sync_debounce: float = 0.35,
        heartbeat_interval: float = 5.0,
        **kwargs: Any,
    ) -> None:
        self.war_room_path = war_room_path
        self.firebase_url = firebase_url
        self.operative_name = "Operative"
        self.target_coord: TargetCoord = TargetCoord(0, 0, 1)

        self.team_id = ""
        self.session_contribution = 0
        self.total_farmed = 0
        self.session_start_time = time.time()
        self.war_logs: List[Dict[str, Any]] = []

        # Realtime Sync Architecture
        self.realtime_sync_enabled: bool = realtime_sync
        self.sync_debounce_seconds: float = sync_debounce
        self.sync_heartbeat_interval: float = heartbeat_interval
        self._is_syncing: bool = False
        self._is_dirty: bool = False
        self._last_sync_time: float = 0.0
        self._last_sync_status: Tuple[bool, str] = (True, "พร้อมทำงาน")
        self._last_logged_contribution: int = 0
        self._sync_lock = threading.Lock()
        self._sync_event = threading.Event()
        self._stop_event = threading.Event()

        app_data = os.getenv("APPDATA") or os.path.expanduser("~")
        self.stats_file = os.path.join(app_data, "NekoTrackerOffline", "war_stats.json")

        self._load_saved_stats()
        self._subscribe_events()

        # Start Realtime Background Worker
        self._sync_worker_thread = threading.Thread(
            target=self._realtime_sync_worker, daemon=True, name="WarService-RealtimeSync"
        )
        self._sync_worker_thread.start()

    def _subscribe_events(self) -> None:
        event_bus.subscribe("meseta_earned", self.on_meseta_earned)
        event_bus.subscribe("tracker_reset", self.on_tracker_reset)
        event_bus.subscribe("character_detected", self.on_character_detected)
        event_bus.subscribe("board_coord_changed", self.on_board_coord_changed)

    def on_character_detected(self, character_name: str = "", player_id: str = "", **kwargs) -> None:
        if character_name and character_name != self.operative_name:
            self.operative_name = character_name
            self.add_log(f"ตรวจพบชื่อในเกมจาก Log (Primary Key): {character_name}", "info")
            self._save_stats()
            self.trigger_realtime_sync()

    def on_board_coord_changed(self, coord: Any = None, slot: Optional[int] = None, **kwargs) -> None:
        if coord is not None:
            self.set_target_coord(coord, slot=slot)

    @classmethod
    def parse_coordinate(cls, coord_input: Any, default_slot: int = 1) -> TargetCoord:
        """
        Parse various coordinate representations into TargetCoord(sector_x, sector_y, slot).
        Ranges supported:
          sector_x: -12 to +25
          sector_y: -11 to +9
          slot: 1 to 4 (1: NW บนซ้าย, 2: NE บนขวา, 3: SW ล่างซ้าย, 4: SE ล่างขวา)

        Formats supported:
          1. 3-number string: "0, 0, 1", "0,0,1", "3, 3, 4"
          2. Hash format: "0,0#1", "3, 3 # 4"
          3. Bracket format: "[0, 0, 1]", "[3, 3, 4]"
          4. JSON dict or string: {"x": 0, "y": 0, "slot": 1}, {"sector_x": 3, "sector_y": 3, "slot": 4}
          5. Web copy text: "คัดลอกพิกัด [8, -2] ช่อง #3 ไปใส่ในโปรแกรม", "Sector [0, 0] · ช่อง #2"
          6. Quadrant text: "0, 0 NW", "0, 0 บนซ้าย"
          7. 2-number fallback: "0, 0", "[15, -8]", "(4, 9)", "X: 12, Y: -5" (defaults slot to default_slot)
        """
        if isinstance(coord_input, TargetCoord):
            return coord_input

        # Dict input
        if isinstance(coord_input, dict):
            try:
                gx = coord_input.get("sector_x", coord_input.get("x", coord_input.get("X", 0)))
                gy = coord_input.get("sector_y", coord_input.get("y", coord_input.get("Y", 0)))
                slot = coord_input.get("slot", coord_input.get("Slot", default_slot))
                return TargetCoord(gx, gy, slot)
            except (ValueError, TypeError):
                pass

        # List or tuple input
        if isinstance(coord_input, (list, tuple)):
            try:
                gx = coord_input[0]
                gy = coord_input[1]
                slot = coord_input[2] if len(coord_input) >= 3 else default_slot
                return TargetCoord(gx, gy, slot)
            except (ValueError, TypeError, IndexError):
                pass

        # String input
        if isinstance(coord_input, str):
            s = coord_input.strip()
            if s.startswith("{") and s.endswith("}"):
                try:
                    data = json.loads(s)
                    return cls.parse_coordinate(data, default_slot=default_slot)
                except Exception:
                    pass

            slot_val = None
            slot_match = re.search(r'(?:slot|ช่อง|\#)\s*[:=]?\s*([1-4])\b', s, re.IGNORECASE)
            if slot_match:
                slot_val = int(slot_match.group(1))
            else:
                if re.search(r'\b(?:NW|บนซ้าย|บนตก)\b', s, re.IGNORECASE):
                    slot_val = 1
                elif re.search(r'\b(?:NE|บนขวา|บนออก)\b', s, re.IGNORECASE):
                    slot_val = 2
                elif re.search(r'\b(?:SW|ล่างซ้าย|ใต้ตก)\b', s, re.IGNORECASE):
                    slot_val = 3
                elif re.search(r'\b(?:SE|ล่างขวา|ใต้ออก)\b', s, re.IGNORECASE):
                    slot_val = 4

            nums = re.findall(r'[-+]?\d+', s)
            if len(nums) >= 3:
                try:
                    x, y = int(nums[0]), int(nums[1])
                    slot = slot_val if slot_val is not None else int(nums[2])
                    return TargetCoord(x, y, slot)
                except ValueError:
                    pass
            elif len(nums) >= 2:
                try:
                    x, y = int(nums[0]), int(nums[1])
                    slot = slot_val if slot_val is not None else default_slot
                    return TargetCoord(x, y, slot)
                except ValueError:
                    pass

        return TargetCoord(0, 0, default_slot)

    def set_target_coord(self, coord_input: Any, slot: Optional[int] = None) -> TargetCoord:
        """Update active board coordinate (sector_x, sector_y, slot), log change, and trigger sync."""
        default_slot = slot if slot is not None else getattr(self.target_coord, "slot", 1)
        parsed = self.parse_coordinate(coord_input, default_slot=default_slot)
        if slot is not None and 1 <= slot <= 4:
            parsed = TargetCoord(parsed.x, parsed.y, slot)

        if parsed != self.target_coord:
            self.target_coord = parsed
            gx, gy, cslot = parsed.x, parsed.y, parsed.slot
            slot_label = parsed.slot_label
            self.add_log(f"อัปเดตพิกัดบนกระดานเป็น [{gx}, {gy}] ช่อง #{cslot} ({slot_label})", "info")
            self._save_stats()
            self.trigger_realtime_sync()
        return self.target_coord

    def set_operative(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.operative_name = name or "Operative"
        self._load_saved_stats()
        self.trigger_realtime_sync()

    def get_team_info(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {
            "id": "",
            "name": "",
            "nameTh": "",
            "tag": "---",
            "emblem": "",
            "color": "#10B981",
            "leader": "-",
            "desc": "",
            "planets": [],
            "teamTreasury": 0,
        }

    def on_auth_state_changed(self, user: Optional[Dict[str, Any]]) -> None:
        if user:
            name = user.get("character_name") or user.get("callsign") or user.get("username") or "Operative"
            self.set_operative(name)
            self.trigger_realtime_sync()

    def on_meseta_earned(self, amount: int, wallet: int = 0) -> None:
        if amount > 0:
            self.session_contribution += amount
            self.total_farmed += amount
            gx, gy, slot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
            self.add_log(
                f"+{amount:,} ℳ พิกัด [{gx}, {gy}] #{slot} (ยอดสะสม: {self.session_contribution:,} ℳ)",
                "income",
            )
            self._save_stats()
            self.trigger_realtime_sync()

    def on_tracker_reset(self) -> None:
        self.session_contribution = 0
        self.session_start_time = time.time()
        self._last_logged_contribution = 0
        self.add_log("รีเซ็ตสถิติรอบการฟาร์มสงคราม", "reset")
        self._save_stats()
        self.trigger_realtime_sync()

    def add_log(self, text: str, log_type: str = "info") -> None:
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "text": text,
            "type": log_type,
            "timestamp": time.time(),
        }
        self.war_logs.insert(0, entry)
        if len(self.war_logs) > 50:
            self.war_logs.pop()

    def get_live_rate(self) -> float:
        """Calculate live M/hr for the current war session."""
        duration = time.time() - self.session_start_time
        if duration >= 1 and self.session_contribution > 0:
            return (self.session_contribution / duration) * 3600
        return 0.0

    def get_database_payload(self) -> Dict[str, Any]:
        """
        Produce database record storing:
        - character_name: In-game name read from log (Primary Key, NOT ID)
        - meseta: Farmed meseta
        - sector_coord: dict {"x": X, "y": Y, "slot": Slot}
        - target_coord: dict {"x": X, "y": Y, "slot": Slot}
        - coord_key: "X,Y"
        - slot: 1-4
        - lastUpdated: Unix timestamp in ms
        """
        gx, gy, slot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
        now_ms = int(time.time() * 1000)
        return {
            "character_name": self.operative_name,
            "meseta": self.session_contribution,
            "sector_coord": {"x": gx, "y": gy, "slot": slot},
            "target_coord": {"x": gx, "y": gy, "slot": slot},
            "coord_key": f"{gx},{gy}",
            "slot": slot,
            "lastUpdated": now_ms,
            "farming_rate_mhr": round(self.get_live_rate()),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": now_ms,
        }

    def trigger_realtime_sync(self, force: bool = False) -> None:
        """Queue or immediately signal a realtime sync event."""
        if not self.realtime_sync_enabled and not force:
            return
        self._is_dirty = True
        self._sync_event.set()

    def _realtime_sync_worker(self) -> None:
        """Background thread that executes non-blocking realtime syncs with debouncing."""
        while not self._stop_event.is_set():
            woken_by_event = self._sync_event.wait(timeout=self.sync_heartbeat_interval)
            if self._stop_event.is_set():
                break

            if woken_by_event:
                self._sync_event.clear()
                time.sleep(self.sync_debounce_seconds)
                self._sync_event.clear()

            now = time.time()
            time_since_sync = now - self._last_sync_time
            has_activity = (self.session_contribution > 0 or self.operative_name != "Operative")
            needs_heartbeat = has_activity and (time_since_sync >= self.sync_heartbeat_interval)

            if self.realtime_sync_enabled and (self._is_dirty or needs_heartbeat):
                self._execute_realtime_cycle()

    def _execute_realtime_cycle(self) -> Tuple[bool, str]:
        """Execute one complete telemetry sync cycle under lock."""
        with self._sync_lock:
            self._is_dirty = False
            self._is_syncing = True
            event_bus.emit("realtime_sync_started")
            try:
                ok, msg = self.sync_to_war_room()
                self._last_sync_time = time.time()
                self._last_sync_status = (ok, msg)
                event_bus.emit(
                    "realtime_sync_completed",
                    success=ok,
                    message=msg,
                    timestamp=self._last_sync_time,
                    contribution=self.session_contribution,
                )
                return ok, msg
            except Exception as exc:
                self._last_sync_status = (False, str(exc))
                event_bus.emit(
                    "realtime_sync_completed",
                    success=False,
                    message=str(exc),
                    timestamp=time.time(),
                    contribution=self.session_contribution,
                )
                return False, str(exc)
            finally:
                self._is_syncing = False

    def stop(self) -> None:
        """Cleanly stop background realtime sync worker."""
        self._stop_event.set()
        self._sync_event.set()
        if hasattr(self, "_sync_worker_thread") and self._sync_worker_thread.is_alive():
            self._sync_worker_thread.join(timeout=1.0)

    def sync_to_cloud_database(self, timeout: float = 3.5) -> Tuple[bool, str]:
        """
        Synchronize live character_name, farmed meseta, and board coordinates to Firebase Realtime Database.
        Uses character_name from log as Primary Key.
        Updates 3 paths matching Firebase Schema:
          1. arks_war_room/operatives/{character_name}
          2. arks_war_room/sectors/{coord_key}/challengers/{character_name}
          3. arks_war_room/sectors/{coord_key}/sub_cells/{slot}/challengers/{character_name}
        Uses pure Python standard library (urllib.request) for zero dependencies & offline resilience.
        """
        if not self.firebase_url:
            return False, "ไม่ได้ระบุ Firebase Database URL"

        base_url = self.firebase_url.rstrip("/")
        db_payload = self.get_database_payload()
        now_ms = db_payload["lastUpdated"]

        char_name = self.operative_name or "Operative"
        safe_key = "".join(
            c for c in char_name
            if c not in '.$#[]/\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f'
        ).strip() or "Operative"

        coord_key = db_payload["coord_key"]
        slot = db_payload["slot"]

        # Path 1: Operative record
        op_payload = {
            "character_name": char_name,
            "meseta": db_payload["meseta"],
            "sector_coord": db_payload["sector_coord"],
            "coord_key": db_payload["coord_key"],
            "slot": slot,
            "lastUpdated": now_ms,
            "target_coord": db_payload["target_coord"],
            "farming_rate_mhr": db_payload["farming_rate_mhr"],
            "updated_at": db_payload["updated_at"],
            "timestamp": db_payload["timestamp"],
        }

        # Path 2: Sector challengers
        sec_payload = {
            "character_name": char_name,
            "meseta": db_payload["meseta"],
            "slot": slot,
            "lastUpdated": now_ms,
        }

        # Path 3: Sub-cell challengers
        sub_payload = {
            "character_name": char_name,
            "meseta": db_payload["meseta"],
            "lastUpdated": now_ms,
        }

        try:
            # 1. Update individual operative record
            url_op = f"{base_url}/arks_war_room/operatives/{urllib.parse.quote(safe_key)}.json"
            req_op = urllib.request.Request(
                url_op,
                data=json.dumps(op_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            with urllib.request.urlopen(req_op, timeout=timeout) as resp:
                pass

            # 2. Update sector challenger record
            url_sec = f"{base_url}/arks_war_room/sectors/{urllib.parse.quote(coord_key)}/challengers/{urllib.parse.quote(safe_key)}.json"
            req_sec = urllib.request.Request(
                url_sec,
                data=json.dumps(sec_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            try:
                with urllib.request.urlopen(req_sec, timeout=timeout) as resp:
                    pass
            except Exception:
                pass

            # 3. Update sub-cell challenger record
            url_sub = f"{base_url}/arks_war_room/sectors/{urllib.parse.quote(coord_key)}/sub_cells/{slot}/challengers/{urllib.parse.quote(safe_key)}.json"
            req_sub = urllib.request.Request(
                url_sub,
                data=json.dumps(sub_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            try:
                with urllib.request.urlopen(req_sub, timeout=timeout) as resp:
                    pass
            except Exception:
                pass

            # 4. Update global latest telemetry
            url_tel = f"{base_url}/arks_war_room/latest_telemetry.json"
            req_tel = urllib.request.Request(
                url_tel,
                data=json.dumps(op_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            try:
                with urllib.request.urlopen(req_tel, timeout=timeout) as resp:
                    pass
            except Exception:
                pass

            # 5. Add to live war logs when contribution increases
            if self.session_contribution > self._last_logged_contribution:
                gain = self.session_contribution - self._last_logged_contribution
                self._last_logged_contribution = self.session_contribution
                gx, gy, cslot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
                log_entry = {
                    "time": time.strftime("%H:%M:%S"),
                    "day": 1,
                    "type": "MESETA",
                    "character_name": char_name,
                    "meseta": self.session_contribution,
                    "gain": gain,
                    "coord": f"{gx}, {gy}, {cslot}",
                    "slot": cslot,
                    "message": f"{char_name} เก็บเกี่ยว +{gain:,} ℳ พิกัด [{gx}, {gy}] ช่อง #{cslot} (ยอดสะสม: {self.session_contribution:,} ℳ)",
                    "timestamp": now_ms,
                    "lastUpdated": now_ms,
                }
                url_log = f"{base_url}/arks_war_room/war_logs.json"
                req_log = urllib.request.Request(
                    url_log,
                    data=json.dumps(log_entry).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req_log, timeout=timeout) as resp:
                        pass
                except Exception:
                    pass

            return True, "ส่งข้อมูลขึ้น Firebase สำเร็จ"
        except Exception as exc:
            return False, f"Firebase Sync Error: {exc}"

    def sync_to_war_room(self) -> Tuple[bool, str]:
        """
        Synchronize current war contribution to ARKS War Room telemetry & database storage.
        Thread-safe execution writing to local files and remote Firebase RTDB.
        """
        now = time.time()
        db_payload = self.get_database_payload()

        payload = {
            "version": "2.0",
            "lastSync": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(now * 1000),
            "lastUpdated": int(now * 1000),
            # Core database fields
            "character_name": db_payload["character_name"],
            "meseta": db_payload["meseta"],
            "sector_coord": db_payload["sector_coord"],
            "target_coord": db_payload["target_coord"],
            "coord_key": db_payload["coord_key"],
            "slot": db_payload["slot"],
            "farmingRateMhr": round(self.get_live_rate()),
            "operative": {
                "name": self.operative_name,
                "character_name": self.operative_name,
                "targetSector": db_payload["target_coord"],
                "sectorCoord": db_payload["sector_coord"],
                "slot": db_payload["slot"],
                "sessionContribution": self.session_contribution,
                "totalFarmed": self.total_farmed,
                "farmingRateMhr": round(self.get_live_rate()),
            },
            "recentLogs": self.war_logs[:10],
        }

        # 1. Save to ARKS War Room data directory if available
        telemetry_dir = os.path.join(self.war_room_path, "data")
        saved_paths = []
        try:
            if os.path.exists(self.war_room_path):
                os.makedirs(telemetry_dir, exist_ok=True)
                sync_file = os.path.join(telemetry_dir, "live_war_telemetry.json")
                with open(sync_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                saved_paths.append(sync_file)

                db_file = os.path.join(telemetry_dir, "database_meseta_records.json")
                with open(db_file, "w", encoding="utf-8") as f:
                    json.dump(db_payload, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"[WarService] Telemetry write to War Room failed: {exc}")

        # 2. Save to local app data cache
        try:
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            self._save_stats()
            saved_paths.append(self.stats_file)

            local_db_file = os.path.join(os.path.dirname(self.stats_file), "database_meseta_records.json")
            with open(local_db_file, "w", encoding="utf-8") as f:
                json.dump(db_payload, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"[WarService] Local stats cache write failed: {exc}")

        # 3. Cloud Database Sync (Firebase Realtime Database)
        cloud_ok = False
        if self.firebase_url:
            try:
                cloud_ok, _ = self.sync_to_cloud_database()
            except Exception as exc:
                print(f"[WarService] Cloud database sync exception: {exc}")

        self._last_sync_time = now
        if saved_paths or cloud_ok:
            gx, gy, slot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
            self.add_log(f"ซิงค์ข้อมูลสำเร็จ: ส่งยอด {self.session_contribution:,} ℳ พิกัด [{gx}, {gy}] ช่อง #{slot} ({self.operative_name})", "sync")
            event_bus.emit("war_telemetry_synced", payload=payload)
            if cloud_ok:
                return True, f"ซิงค์ข้อมูลเรียลไทม์สำเร็จ (+{self.session_contribution:,} ℳ)"
            return True, f"บันทึกข้อมูลเรียลไทม์เรียบร้อย (+{self.session_contribution:,} ℳ)"
        return False, "ไม่สามารถบันทึกข้อมูล Telemetry ได้"

    def _save_stats(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            data = {
                "operative_name": self.operative_name,
                "target_coord": list(self.target_coord),
                "session_contribution": self.session_contribution,
                "total_farmed": self.total_farmed,
                "last_active": time.time(),
            }
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as exc:
            print(f"[WarService] Failed saving war stats: {exc}")

    def _load_saved_stats(self) -> None:
        if not os.path.exists(self.stats_file):
            return
        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("operative_name") == self.operative_name:
                    self.total_farmed = data.get("total_farmed", 0)
                if "target_coord" in data:
                    self.target_coord = self.parse_coordinate(data.get("target_coord"))
        except Exception as exc:
            print(f"[WarService] Failed loading war stats: {exc}")


if __name__ == "__main__":
    print("=" * 60)
    print("🪐  NEKO Tracker — WarService Self-Test")
    print("=" * 60)
    service = WarService()
    print(f" [✓] Operative: {service.operative_name}")
    print(f" [✓] Target Coord: {service.target_coord} (Slot #{service.target_coord.slot})")
    print(" [✓] WarService initialized cleanly without login!")
    print("=" * 60)
