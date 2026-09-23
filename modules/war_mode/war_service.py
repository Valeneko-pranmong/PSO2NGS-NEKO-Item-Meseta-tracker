from __future__ import annotations

import json
import os
import re
import shutil
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

from modules.i18n import t
from modules.utils import calculate_live_rate

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
        CLIENT_VERSION,
        MIN_SECURE_VERSION,
        REVOKED_VERSIONS,
    )
except Exception:
    DEFAULT_FIREBASE_RTDB_URL = "https://arks-war-room-default-rtdb.asia-southeast1.firebasedatabase.app"
    SECTOR_X_MIN = -12
    SECTOR_X_MAX = 25
    SECTOR_Y_MIN = -11
    SECTOR_Y_MAX = 9
    SLOT_MIN = 1
    SLOT_MAX = 4
    SLOT_TARGET_MESETA = 10_000_000
    SECTOR_TARGET_MESETA = 40_000_000
    CLIENT_VERSION = "7.1.0"
    MIN_SECURE_VERSION = "7.1.0"
    REVOKED_VERSIONS = ["7.0.0-alpha", "7.0.0"]


from modules.version import parse_semver, compare_semver, is_version_secure

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
            if len(other) == 3:
                return (self[0], self[1], self[2]) == (other[0], other[1], other[2])
            return False
        return super().__eq__(other)

    __hash__ = tuple.__hash__


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
        client_version: Optional[str] = None,
        realtime_sync: bool = True,
        sync_debounce: float = 0.35,
        heartbeat_interval: float = 5.0,
        **kwargs: Any,
    ) -> None:
        self.war_room_path = war_room_path
        self.firebase_url = firebase_url
        self.client_version = client_version or CLIENT_VERSION
        self.operative_name = "Operative"
        self.target_coord: TargetCoord = TargetCoord(0, 0, 1)

        self.team_id = ""
        self.session_contribution = 0
        self.total_farmed = 0
        self.slot_farmed: Dict[str, int] = {}
        self.session_start_time = time.time()
        self.first_farming_time: Optional[float] = None
        self.war_logs: List[Dict[str, Any]] = []
        self._has_fetched_cloud_stats: bool = False
        self._logs_lock = threading.Lock()
        self._state_lock = threading.RLock()

        # Remote Version Control Policy (Dynamic Firebase RTDB Sync)
        self.remote_policy: Dict[str, Any] = {}
        self.latest_version: str = CLIENT_VERSION
        self.min_secure_version: str = MIN_SECURE_VERSION
        self.revoked_versions: List[str] = list(REVOKED_VERSIONS)
        self.remote_policy_fetched: bool = False

        # Security & Anti-Tamper State
        self.is_tamper_compromised: bool = False
        self.tamper_violations_count: int = 0
        self._last_processed_sequence: int = -1

        # Realtime Sync Architecture
        self.realtime_sync_enabled: bool = realtime_sync
        self.sync_debounce_seconds: float = sync_debounce
        self.sync_heartbeat_interval: float = heartbeat_interval
        self._is_syncing: bool = False
        self._is_dirty: bool = False
        self._last_sync_time: float = 0.0
        self._last_sync_status: Tuple[bool, str] = (True, "พร้อมทำงาน")
        self._last_cloud_ok: bool = True
        self._last_cloud_msg: str = ""
        self._cloud_fail_count: int = 0
        self._cloud_backoff_until: float = 0.0
        self._last_logged_contribution: int = 0
        self._last_synced_coord_key: Optional[str] = None
        self._last_synced_slot: Optional[int] = None
        self._last_synced_operative: Optional[str] = None
        self._sync_lock = threading.Lock()
        self._sync_event = threading.Event()
        self._stop_event = threading.Event()
        self.event_bus = kwargs.get("event_bus") or event_bus

        app_data = os.getenv("APPDATA") or os.path.expanduser("~")
        self.stats_file = kwargs.get("stats_file") or os.path.join(app_data, "NekoTrackerOffline", "war_stats.json")

        self._load_saved_stats()
        self._subscribe_events()

        # Start Realtime Background Worker
        if self.realtime_sync_enabled:
            self.ensure_sync_worker()

    def ensure_sync_worker(self) -> None:
        """Ensure background realtime sync worker thread is running."""
        with self._state_lock:
            if not self.realtime_sync_enabled or self._stop_event.is_set():
                return
            if not hasattr(self, "_sync_worker_thread") or not self._sync_worker_thread.is_alive():
                self._sync_worker_thread = threading.Thread(
                    target=self._realtime_sync_worker, daemon=True, name="WarService-RealtimeSync"
                )
                self._sync_worker_thread.start()

    def set_realtime_sync(self, enabled: bool) -> None:
        """
        Enable or disable realtime cloud synchronization (e.g. switching between war mode and offline mode).
        In offline mode, immediately clears pending sync signals to guarantee zero telemetry leakage.
        """
        with self._state_lock:
            self.realtime_sync_enabled = enabled
            if not enabled:
                self._is_dirty = False
                self._sync_event.clear()
        if enabled:
            self.ensure_sync_worker()
            self.trigger_realtime_sync()

    def _subscribe_events(self) -> None:
        self.event_bus.subscribe("meseta_earned", self.on_meseta_earned)
        self.event_bus.subscribe("tracker_reset", self.on_tracker_reset)
        self.event_bus.subscribe("character_detected", self.on_character_detected)
        self.event_bus.subscribe("board_coord_changed", self.on_board_coord_changed)
        self.event_bus.subscribe("tamper_violation", self.on_tamper_violation)

    def on_tamper_violation(self, violation: Any = None, **kwargs) -> None:
        """Handles anti-tamper violation events from tracker engine."""
        if violation:
            is_fatal = getattr(violation, "is_fatal", True)
            with self._state_lock:
                self.tamper_violations_count += 1
                if is_fatal:
                    self.is_tamper_compromised = True
            msg = f"🛡️ [ANTI-TAMPER] {getattr(violation, 'message', str(violation))}"
            self.add_log(msg, "warning" if not is_fatal else "danger")
            if is_fatal:
                self.trigger_realtime_sync()

    def on_character_detected(self, character_name: str = "", player_id: str = "", **kwargs) -> None:
        if character_name and character_name != self.operative_name:
            with self._state_lock:
                self.operative_name = character_name
                self._has_fetched_cloud_stats = False
            self.add_log(f"ตรวจพบชื่อในเกมจาก Log (Primary Key): {character_name}", "info")
            self._load_saved_stats()
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

        with self._state_lock:
            if parsed != self.target_coord:
                self.target_coord = parsed
                gx, gy, cslot = parsed.x, parsed.y, parsed.slot
                slot_label = parsed.slot_label
                changed = True
            else:
                changed = False

        if changed:
            slot_key = f"{gx},{gy}#{cslot}"
            slot_m = self.slot_farmed.get(slot_key, 0)
            self.add_log(f"อัปเดตพิกัดบนกระดานเป็น [{gx}, {gy}] ช่อง #{cslot} ({slot_label}) — ยอดสะสมช่องนี้: {slot_m:,} ℳ", "info")
            self._save_stats()
            self.trigger_realtime_sync()
        return self.target_coord

    def get_slot_meseta(self, coord_key: Optional[str] = None, slot: Optional[int] = None) -> int:
        """Get accumulated meseta farmed for a specific sector and quadrant slot."""
        with self._state_lock:
            ck = coord_key if coord_key is not None else self.target_coord.coord_key
            sl = slot if slot is not None else self.target_coord.slot
            return self.slot_farmed.get(f"{ck}#{sl}", 0)

    def get_sector_meseta(self, coord_key: Optional[str] = None) -> int:
        """Get total meseta farmed across all 4 sub-cells in a sector."""
        with self._state_lock:
            ck = coord_key if coord_key is not None else self.target_coord.coord_key
            return sum(self.slot_farmed.get(f"{ck}#{s}", 0) for s in range(1, 5))

    def set_operative(self, name: str, *args: Any, **kwargs: Any) -> None:
        with self._state_lock:
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

    def on_meseta_earned(self, amount: int, wallet: int = 0, sequence_number: int = -1, **kwargs) -> None:
        if amount > 0:
            with self._state_lock:
                if self.is_tamper_compromised:
                    return
                # Sequence deduplication guard: ignore replayed or duplicated sequence numbers
                if sequence_number >= 0:
                    if self._last_processed_sequence >= 0 and sequence_number <= self._last_processed_sequence:
                        return
                    self._last_processed_sequence = sequence_number

                if self.first_farming_time is None:
                    self.first_farming_time = time.time()
                self.session_contribution += amount
                self.total_farmed += amount
                gx, gy, slot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
                slot_key = f"{gx},{gy}#{slot}"
                self.slot_farmed[slot_key] = self.slot_farmed.get(slot_key, 0) + amount
                current_slot_meseta = self.slot_farmed[slot_key]
                current_contrib = self.session_contribution
                total_meseta = self.total_farmed

            self.add_log(
                f"+{amount:,} ℳ พิกัด [{gx}, {gy}] #{slot} (ยอดสะสมช่องนี้: {current_slot_meseta:,} ℳ | รวม: {total_meseta:,} ℳ)",
                "income",
            )
            self._save_stats()
            self.trigger_realtime_sync()

    def on_tracker_reset(self) -> None:
        with self._state_lock:
            self.session_contribution = 0
            self.session_start_time = time.time()
            self.first_farming_time = None
            self._last_logged_contribution = max(self.total_farmed, 0)
            self._last_processed_sequence = -1
            self.is_tamper_compromised = False
            self.tamper_violations_count = 0
        self.add_log("รีเซ็ตสถิติรอบการฟาร์ม (คงสถานะความคืบหน้ากระดานสงคราม)", "reset")
        self._save_stats()
        self.trigger_realtime_sync()

    def add_log(self, text: str, log_type: str = "info") -> None:
        entry = {
            "time": time.strftime("%H:%M:%S"),
            "text": text,
            "type": log_type,
            "timestamp": time.time(),
        }
        with self._logs_lock:
            self.war_logs.insert(0, entry)
            if len(self.war_logs) > 50:
                self.war_logs.pop()

    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._logs_lock:
            return list(self.war_logs[:limit])

    def get_live_rate(self) -> float:
        """
        Calculate live Meseta/hr for the current war session with cold-start smoothing.
        Applies a minimum duration floor (30s) to prevent erratic spikes.
        Returns 0.0 if session is compromised or client version is insecure.
        """
        with self._state_lock:
            if self.is_tamper_compromised or not self.is_version_secure():
                return 0.0
            if self.session_contribution <= 0:
                return 0.0

            ref_time = self.first_farming_time or self.session_start_time
            contrib = self.session_contribution
        duration = time.time() - ref_time
        return calculate_live_rate(contrib, duration, min_smoothing_seconds=30.0)

    def bootstrap_version_control_policy(self, timeout: float = 3.0) -> bool:
        """
        Auto-bootstrap canonical version_control policy on Firebase RTDB when database is empty (null).
        Allowed by database.rules.json: ".write": "!data.exists() || auth != null".
        """
        if not self.firebase_url:
            return False
        base_url = self.firebase_url.rstrip("/")
        url = f"{base_url}/arks_war_room/version_control.json"
        rev_dict = {r.replace(".", "_"): True for r in self.revoked_versions}
        payload = {
            "latest_version": self.latest_version,
            "min_secure_version": self.min_secure_version,
            "revoked_versions": rev_dict,
            "announcement": "ARKS War Room Initialized",
            "download_url": "",
            "last_updated": int(time.time() * 1000),
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": f"NEKOTracker/{self.client_version}"},
                method="PUT",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if status < 400:
                    self.remote_policy = payload
                    self.remote_policy_fetched = True
                    self.add_log("ตรวจพบฐานข้อมูลว่างเปล่า — ระบบทำการ Auto-Bootstrap โครงสร้างฐานข้อมูลเริ่มต้นสำเร็จ", "sync")
                    return True
        except Exception as exc:
            print(f"[WarService] Failed auto-bootstrapping version_control: {exc}")
        return False

    def fetch_remote_version_policy(self, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Fetch dynamic version control policy from Firebase RTDB (/arks_war_room/version_control.json).
        Updates local min_secure_version, latest_version, and revoked_versions if successfully fetched.
        If database is empty (null), automatically bootstraps baseline version control schema.
        """
        if not self.firebase_url:
            return {}
        base_url = self.firebase_url.rstrip("/")
        url = f"{base_url}/arks_war_room/version_control.json"
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": f"NEKOTracker/{self.client_version}"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw_body = resp.read().decode("utf-8").strip()
                data = json.loads(raw_body) if raw_body else None
                if isinstance(data, dict):
                    self.remote_policy = data
                    if "latest_version" in data and isinstance(data["latest_version"], str):
                        self.latest_version = data["latest_version"]
                    if "min_secure_version" in data and isinstance(data["min_secure_version"], str):
                        self.min_secure_version = data["min_secure_version"]
                    if "revoked_versions" in data:
                        rev = data["revoked_versions"]
                        if isinstance(rev, dict):
                            self.revoked_versions = [k.replace("_", ".") for k, v in rev.items() if v]
                        elif isinstance(rev, (list, set)):
                            self.revoked_versions = list(rev)
                    self.remote_policy_fetched = True
                    return data
                elif data is None:
                    # Database is empty (null): Auto-bootstrap version_control baseline
                    if self.bootstrap_version_control_policy(timeout=timeout):
                        return self.remote_policy
        except Exception:
            pass
        return {}

    def is_version_secure(self, version: Optional[str] = None) -> bool:
        """Check if current client version meets security verification standards (remote policy or local fallback)."""
        v = version or self.client_version
        return is_version_secure(
            v,
            min_version=self.min_secure_version,
            revoked_versions=self.revoked_versions,
        )

    def check_version_status(self) -> Dict[str, Any]:
        """
        Evaluate full status of client against remote version control policy:
        Returns structured status:
          - current_version: str
          - latest_version: str
          - min_secure_version: str
          - is_secure: bool
          - is_latest: bool
          - status: "SECURE_LATEST" | "UPDATE_AVAILABLE" | "REVOKED_INSECURE" | "OUTDATED_INSECURE"
          - message: str
          - download_url: str
        """
        if not self.remote_policy_fetched:
            self.fetch_remote_version_policy()

        is_sec = self.is_version_secure(self.client_version)
        cmp_latest = compare_semver(self.client_version, self.latest_version)
        is_latest = cmp_latest >= 0
        v_clean = self.client_version.strip().lower().lstrip("v").strip()
        rev_set = {r.lower().lstrip("v").strip() for r in self.revoked_versions}

        download_url = self.remote_policy.get(
            "download_url", "https://github.com/Vale3neko/PSO2NGS-NEKO-Item-Meseta-tracker/releases"
        )

        if v_clean in rev_set:
            status = "REVOKED_INSECURE"
            msg = f"เวอร์ชัน {self.client_version} ถูกเพิกถอนเนื่องจากมีปัญหาความปลอดภัย ยอดเงินจะไม่ถูกบันทึก กรุณาอัปเดตเป็น {self.latest_version}"
        elif not is_sec:
            status = "OUTDATED_INSECURE"
            msg = f"เวอร์ชัน {self.client_version} ต่ำกว่าเกณฑ์ความปลอดภัยขั้นต่ำ ({self.min_secure_version}) ยอดเงินจะไม่ถูกบันทึก กรุณาอัปเดตเป็น {self.latest_version}"
        elif not is_latest:
            status = "UPDATE_AVAILABLE"
            msg = f"มีเวอร์ชันใหม่ {self.latest_version} (เวอร์ชันปัจจุบัน: {self.client_version}) แนะนำให้อัปเดตเพื่อฟีเจอร์ล่าสุด"
        else:
            status = "SECURE_LATEST"
            msg = f"เวอร์ชันปัจจุบัน {self.client_version} เป็นเวอร์ชันล่าสุดและปลอดภัย"

        return {
            "current_version": self.client_version,
            "latest_version": self.latest_version,
            "min_secure_version": self.min_secure_version,
            "is_secure": is_sec,
            "is_latest": is_latest,
            "status": status,
            "message": msg,
            "download_url": download_url,
            "announcement": self.remote_policy.get("announcement", ""),
        }

    def get_database_payload(self) -> Dict[str, Any]:
        """
        Produce database record storing:
        - character_name: In-game name read from log (Primary Key, NOT ID)
        - meseta: Farmed meseta (gated by version security: 0 if version is insecure)
        - raw_meseta: Unfiltered session contribution
        - client_version: Client application version sent for security verification
        - version: Semantic version
        - security_status: SECURE or REVOKED_VERSION_INSECURE
        - version_security_valid: Boolean security verification flag
        - sector_coord: dict {"x": X, "y": Y, "slot": Slot}
        - target_coord: dict {"x": X, "y": Y, "slot": Slot}
        - coord_key: "X,Y"
        - slot: 1-4
        - lastUpdated: Unix timestamp in ms
        """
        with self._state_lock:
            gx, gy, slot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
            now_ms = int(time.time() * 1000)
            is_secure = self.is_version_secure() and not self.is_tamper_compromised

            # Security gate: Insecure/revoked versions or compromised tamper do NOT count meseta.
            # Preserve board meseta across session resets using cumulative total_farmed.
            effective_meseta = max(self.total_farmed, self.session_contribution)
            counted_meseta = effective_meseta if is_secure else 0
            if self.is_tamper_compromised:
                sec_status = "TAMPER_COMPROMISED"
            elif is_secure:
                sec_status = "SECURE"
            else:
                sec_status = "REVOKED_VERSION_INSECURE"

            rate_mhr = round(self.get_live_rate()) if is_secure else 0
            slot_key = f"{gx},{gy}#{slot}"
            slot_m = self.slot_farmed.get(slot_key, 0)
            counted_slot_m = slot_m if is_secure else 0

            sec_m = sum(self.slot_farmed.get(f"{gx},{gy}#{s}", 0) for s in range(1, 5))
            if sec_m == 0:
                sec_m = slot_m
            counted_sec_m = sec_m if is_secure else 0

            return {
                "character_name": self.operative_name,
                "meseta": counted_meseta,
                "raw_meseta": effective_meseta,
                "slot_meseta": counted_slot_m,
                "raw_slot_meseta": slot_m,
                "sector_meseta": counted_sec_m,
                "raw_sector_meseta": sec_m,
                "slot_farmed": dict(self.slot_farmed),
                "session_meseta": self.session_contribution,
                "total_farmed": self.total_farmed,
                "client_version": self.client_version,
                "version": self.client_version,
                "app_version": self.client_version,
                "security_status": sec_status,
                "version_security_valid": is_secure,
                "sector_coord": {"x": gx, "y": gy, "slot": slot},
                "target_coord": {"x": gx, "y": gy, "slot": slot},
                "coord_key": f"{gx},{gy}",
                "slot": slot,
                "lastUpdated": now_ms,
                "farming_rate_mhr": rate_mhr,
                "farmingRateMhr": rate_mhr,
                "meseta_per_hour": rate_mhr,
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": now_ms,
            }

    def trigger_realtime_sync(self, force: bool = False) -> None:
        """Queue or immediately signal a realtime sync event."""
        with self._state_lock:
            self._is_dirty = True
        if not self.realtime_sync_enabled and not force:
            return
        self.ensure_sync_worker()
        self._sync_event.set()

    def _realtime_sync_worker(self) -> None:
        """Background thread that executes non-blocking realtime syncs with debouncing."""
        min_cooldown = 1.2  # Cooldown between consecutive cloud sync cycles to prevent rapid thrashing
        while not self._stop_event.is_set():
            try:
                woken_by_event = self._sync_event.wait(timeout=self.sync_heartbeat_interval)
                if self._stop_event.is_set():
                    break

                if woken_by_event:
                    self._sync_event.clear()
                    # Trailing-edge debounce: wait for rapid consecutive events to settle
                    debounce_start = time.time()
                    while not self._stop_event.is_set():
                        new_event = self._sync_event.wait(timeout=self.sync_debounce_seconds)
                        if not new_event or (time.time() - debounce_start >= 1.5):
                            self._sync_event.clear()
                            break
                        self._sync_event.clear()

                # Enforce cooldown since last sync completion to avoid rapid back-to-back network churn
                elapsed_since_last = time.time() - self._last_sync_time
                if elapsed_since_last < min_cooldown:
                    wait_needed = min_cooldown - elapsed_since_last
                    if self._stop_event.wait(timeout=wait_needed):
                        break

                now = time.time()
                time_since_sync = now - self._last_sync_time
                with self._state_lock:
                    is_dirty = self._is_dirty
                    has_activity = (self.session_contribution > 0 or self.total_farmed > 0 or self.operative_name != "Operative")
                needs_heartbeat = has_activity and (time_since_sync >= self.sync_heartbeat_interval)

                if self.realtime_sync_enabled and (is_dirty or needs_heartbeat):
                    is_heartbeat = (not is_dirty and needs_heartbeat)
                    self._execute_realtime_cycle(is_heartbeat=is_heartbeat)
            except Exception as loop_exc:
                print(f"[WarService] Realtime sync worker loop exception: {loop_exc}")
                time.sleep(1.0)

    def _execute_realtime_cycle(self, is_heartbeat: bool = False) -> Tuple[bool, str]:
        """Execute one complete telemetry sync cycle under lock."""
        with self._sync_lock:
            with self._state_lock:
                if not self.realtime_sync_enabled:
                    return False, "ไม่อนุญาตให้ส่งข้อมูลในโหมดออฟไลน์ (Offline Mode)"
                self._is_dirty = False
                self._is_syncing = True
            if not is_heartbeat:
                self.event_bus.emit("realtime_sync_started")
            try:
                ok, msg = self.sync_to_war_room()
                self._last_sync_time = time.time()
                self._last_sync_status = (ok, msg)
                with self._state_lock:
                    active_contrib = max(self.total_farmed, self.session_contribution)
                if not is_heartbeat:
                    self.event_bus.emit(
                        "realtime_sync_completed",
                        success=ok,
                        message=msg,
                        timestamp=self._last_sync_time,
                        contribution=active_contrib,
                        cloud_synced=self._last_cloud_ok,
                    )
                return ok, msg
            except Exception as exc:
                self._last_sync_status = (False, str(exc))
                with self._state_lock:
                    active_contrib = max(self.total_farmed, self.session_contribution)
                if not is_heartbeat:
                    self.event_bus.emit(
                        "realtime_sync_completed",
                        success=False,
                        message=str(exc),
                        timestamp=time.time(),
                        contribution=active_contrib,
                    )
                return False, str(exc)
            finally:
                with self._state_lock:
                    self._is_syncing = False

    def stop(self) -> None:
        """Cleanly stop background realtime sync worker and unsubscribe."""
        self._stop_event.set()
        self._sync_event.set()
        if hasattr(self, "_sync_worker_thread") and self._sync_worker_thread.is_alive():
            self._sync_worker_thread.join(timeout=1.0)
        try:
            self.event_bus.unsubscribe("meseta_earned", self.on_meseta_earned)
            self.event_bus.unsubscribe("tracker_reset", self.on_tracker_reset)
            self.event_bus.unsubscribe("character_detected", self.on_character_detected)
            self.event_bus.unsubscribe("board_coord_changed", self.on_board_coord_changed)
            self.event_bus.unsubscribe("tamper_violation", self.on_tamper_violation)
        except Exception:
            pass

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
            return False, "ไม่ได้ระบุ URL สำหรับซิงค์ข้อมูล"

        if not self.remote_policy_fetched:
            self.fetch_remote_version_policy(timeout=min(2.0, timeout))

        base_url = self.firebase_url.rstrip("/")
        char_name = self.operative_name or "Operative"
        safe_key = "".join(
            c for c in char_name
            if c not in '.$#[]/\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f'
        ).strip() or "Operative"

        # Fetch authoritative database state to support "clean close / fetch fresh"
        # when the user deletes the database manually.
        if not self._has_fetched_cloud_stats and safe_key != "Operative":
            try:
                url_get = f"{base_url}/arks_war_room/operatives/{urllib.parse.quote(safe_key)}.json"
                req = urllib.request.Request(url_get, method="GET", headers={"User-Agent": f"NEKOTracker/{self.client_version}"})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = resp.read().decode("utf-8").strip()
                if data == "null":
                    # Database record is missing (deleted on cloud to reset). Clean local stats to match.
                    with self._state_lock:
                        self.total_farmed = self.session_contribution
                        self.slot_farmed.clear()
                        if self.session_contribution > 0:
                            ck = f"{self.target_coord.x},{self.target_coord.y}#{self.target_coord.slot}"
                            self.slot_farmed[ck] = self.session_contribution
                        self._has_fetched_cloud_stats = True
                    self.add_log("ไม่พบข้อมูลเดิมบนฐานข้อมูล (เริ่มนับยอดรวมใหม่ตาม Session)", "info")
                    self._save_stats()
                else:
                    try:
                        parsed = json.loads(data)
                    except Exception:
                        parsed = None

                    if isinstance(parsed, dict):
                        try:
                            db_meseta = max(0, int(parsed.get("meseta", 0)))
                        except (ValueError, TypeError):
                            db_meseta = 0
                        with self._state_lock:
                            # Adopt DB state unconditionally as source of truth (respecting current session)
                            self.total_farmed = max(db_meseta, self.session_contribution)
                            if not self.slot_farmed and self.total_farmed > 0:
                                ck = f"{self.target_coord.x},{self.target_coord.y}#{self.target_coord.slot}"
                                self.slot_farmed[ck] = self.total_farmed
                            self._has_fetched_cloud_stats = True
                        self.add_log(f"ดึงข้อมูลจากฐานข้อมูล: เริ่มนับที่ {self.total_farmed:,} ℳ", "info")
                    else:
                        with self._state_lock:
                            self._has_fetched_cloud_stats = True
            except Exception as exc:
                print(f"[WarService] Failed fetching initial cloud stats for {safe_key}: {exc}")
                # Don't fail the sync, mark as fetched to prevent blocking loops.
                # In emergency (cannot connect to DB), preserve local total_farmed in secret buffer.
                self._has_fetched_cloud_stats = True

        db_payload = self.get_database_payload()
        now_ms = db_payload["lastUpdated"]
        is_secure = db_payload["version_security_valid"]
        client_ver = self.client_version

        if self.is_tamper_compromised:
            return False, t("msg_anti_tamper_compromised")

        if not is_secure:
            return False, t("msg_security_revoked", version=client_ver)

        coord_key = db_payload["coord_key"]
        slot = db_payload["slot"]
        rate_mhr = db_payload.get("farming_rate_mhr", 0)
        slot_key = f"{coord_key}#{slot}"

        # If active slot has no local record, check Firebase for existing slot contribution
        if slot_key not in self.slot_farmed and self.firebase_url and safe_key != "Operative":
            try:
                url_sub_get = f"{base_url}/arks_war_room/sectors/{urllib.parse.quote(coord_key)}/sub_cells/{slot}/challengers/{urllib.parse.quote(safe_key)}.json"
                req_sg = urllib.request.Request(url_sub_get, method="GET", headers={"User-Agent": f"NEKOTracker/{self.client_version}"})
                with urllib.request.urlopen(req_sg, timeout=min(2.0, timeout)) as resp_sg:
                    sub_raw = resp_sg.read().decode("utf-8").strip()
                if sub_raw and sub_raw != "null":
                    sub_parsed = json.loads(sub_raw)
                    if isinstance(sub_parsed, dict) and "meseta" in sub_parsed:
                        with self._state_lock:
                            self.slot_farmed[slot_key] = max(0, int(sub_parsed.get("meseta", 0)))
            except Exception:
                pass

        slot_meseta = self.slot_farmed.get(slot_key, 0)
        counted_slot_meseta = slot_meseta if is_secure else 0

        sector_meseta = sum(self.slot_farmed.get(f"{coord_key}#{s}", 0) for s in range(1, 5))
        if sector_meseta == 0:
            sector_meseta = slot_meseta
        counted_sec_meseta = sector_meseta if is_secure else 0

        # Path 1: Operative record (Cumulative across galaxy)
        op_payload = {
            "character_name": char_name,
            "meseta": db_payload["meseta"],
            "raw_meseta": db_payload["raw_meseta"],
            "client_version": client_ver,
            "version": client_ver,
            "security_status": db_payload["security_status"],
            "version_security_valid": is_secure,
            "sector_coord": db_payload["sector_coord"],
            "coord_key": db_payload["coord_key"],
            "slot": slot,
            "lastUpdated": now_ms,
            "target_coord": db_payload["target_coord"],
            "farming_rate_mhr": rate_mhr,
            "farmingRateMhr": rate_mhr,
            "meseta_per_hour": rate_mhr,
            "updated_at": db_payload["updated_at"],
            "timestamp": db_payload["timestamp"],
        }

        # Path 2: Sector challengers (Aggregated across sub-cells in this sector)
        sec_payload = {
            "character_name": char_name,
            "meseta": counted_sec_meseta,
            "client_version": client_ver,
            "security_status": db_payload["security_status"],
            "status": "claimed" if (is_secure and counted_sec_meseta >= SLOT_TARGET_MESETA) else ("BLOCKED_INSECURE_VERSION" if not is_secure else "contributing"),
            "slot": slot,
            "farming_rate_mhr": rate_mhr,
            "farmingRateMhr": rate_mhr,
            "meseta_per_hour": rate_mhr,
            "lastUpdated": now_ms,
        }

        # Path 3: Sub-cell challengers (Per-slot continuous farming)
        sub_payload = {
            "character_name": char_name,
            "meseta": counted_slot_meseta,
            "client_version": client_ver,
            "security_status": db_payload["security_status"],
            "slot": slot,
            "farming_rate_mhr": rate_mhr,
            "farmingRateMhr": rate_mhr,
            "meseta_per_hour": rate_mhr,
            "lastUpdated": now_ms,
        }

        try:
            # Multi-Path Atomic Update Optimization for Firebase RTDB
            # Combines operative, sector, sub-cell, and latest_telemetry into 1 atomic PATCH request,
            # reducing network roundtrips from 4 to 1 for high concurrency (100+ operatives).
            patch_payload = {
                f"operatives/{safe_key}": op_payload,
                f"sectors/{coord_key}/challengers/{safe_key}": sec_payload,
                f"sectors/{coord_key}/sub_cells/{slot}/challengers/{safe_key}": sub_payload,
                "latest_telemetry": op_payload,
            }
            url_patch = f"{base_url}/arks_war_room.json"
            req_patch = urllib.request.Request(
                url_patch,
                data=json.dumps(patch_payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": f"NEKOTracker/{client_ver}"},
                method="PATCH",
            )
            patch_ok = False
            patch_err = None
            try:
                with urllib.request.urlopen(req_patch, timeout=timeout) as resp:
                    patch_ok = True
            except Exception as pe:
                patch_ok = False
                patch_err = pe

            if not patch_ok:
                err_s = str(patch_err) if patch_err else ""
                # If 404 Not Found, 401/403 Unauthorized, or network connection failure,
                # fail-fast immediately instead of repeating timeouts across 4 more endpoints!
                if any(code in err_s for code in ("404", "401", "403")) or isinstance(patch_err, (urllib.error.HTTPError, urllib.error.URLError)):
                    raise patch_err

                # Fallback to individual PUT calls only if root PATCH was specifically rejected (e.g. 405 Method Not Allowed)
                url_op = f"{base_url}/arks_war_room/operatives/{urllib.parse.quote(safe_key)}.json"
                req_op = urllib.request.Request(
                    url_op,
                    data=json.dumps(op_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": f"NEKOTracker/{client_ver}"},
                    method="PUT",
                )
                with urllib.request.urlopen(req_op, timeout=timeout) as resp:
                    pass

                url_sec = f"{base_url}/arks_war_room/sectors/{urllib.parse.quote(coord_key)}/challengers/{urllib.parse.quote(safe_key)}.json"
                req_sec = urllib.request.Request(
                    url_sec,
                    data=json.dumps(sec_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": f"NEKOTracker/{client_ver}"},
                    method="PUT",
                )
                try:
                    with urllib.request.urlopen(req_sec, timeout=timeout) as resp:
                        pass
                except Exception:
                    pass

                url_sub = f"{base_url}/arks_war_room/sectors/{urllib.parse.quote(coord_key)}/sub_cells/{slot}/challengers/{urllib.parse.quote(safe_key)}.json"
                req_sub = urllib.request.Request(
                    url_sub,
                    data=json.dumps(sub_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": f"NEKOTracker/{client_ver}"},
                    method="PUT",
                )
                try:
                    with urllib.request.urlopen(req_sub, timeout=timeout) as resp:
                        pass
                except Exception:
                    pass

                url_tel = f"{base_url}/arks_war_room/latest_telemetry.json"
                req_tel = urllib.request.Request(
                    url_tel,
                    data=json.dumps(op_payload).encode("utf-8"),
                    headers={"Content-Type": "application/json", "User-Agent": f"NEKOTracker/{client_ver}"},
                    method="PUT",
                )
                try:
                    with urllib.request.urlopen(req_tel, timeout=timeout) as resp:
                        pass
                except Exception:
                    pass

            # If client version is insecure, log security warning and reject counting meseta
            if not is_secure:
                warn_entry = {
                    "time": time.strftime("%H:%M:%S"),
                    "day": 1,
                    "type": "SECURITY_WARNING",
                    "character_name": char_name,
                    "meseta": 0,
                    "gain": 0,
                    "client_version": client_ver,
                    "security_status": "REVOKED_VERSION_INSECURE",
                    "coord": f"{self.target_coord.x}, {self.target_coord.y}, {slot}",
                    "slot": slot,
                    "message": f"[ความปลอดภัย] ตรวจพบไคลเอนต์เวอร์ชัน {client_ver} ซึ่งมีช่องโหว่ความปลอดภัย ยอดเงินจะไม่ถูกนับเข้าสู่ฐานข้อมูล กรุณาอัปเดตเป็น 7.1.0",
                    "timestamp": now_ms,
                    "lastUpdated": now_ms,
                }
                url_log = f"{base_url}/arks_war_room/war_logs.json"
                req_log = urllib.request.Request(
                    url_log,
                    data=json.dumps(warn_entry).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req_log, timeout=timeout) as resp:
                        pass
                except Exception:
                    pass
                return False, f"ไคลเอนต์เวอร์ชัน {client_ver} มีช่องโหว่ความปลอดภัย ยอดเงินจะไม่ถูกนับเข้าสู่ฐานข้อมูล (กรุณาอัปเดตเป็น 7.1.0)"

            # 5. Add to live war logs when contribution increases
            with self._state_lock:
                current_contrib = max(self.total_farmed, self.session_contribution)
                if current_contrib > self._last_logged_contribution:
                    gain = current_contrib - self._last_logged_contribution
                    self._last_logged_contribution = current_contrib
                else:
                    gain = 0
            if gain > 0:
                gx, gy, cslot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
                log_entry = {
                    "time": time.strftime("%H:%M:%S"),
                    "day": 1,
                    "type": "MESETA",
                    "character_name": char_name,
                    "meseta": current_contrib,
                    "gain": gain,
                    "client_version": client_ver,
                    "security_status": "SECURE",
                    "coord": f"{gx}, {gy}, {cslot}",
                    "slot": cslot,
                    "message": f"{char_name} เก็บเกี่ยว +{gain:,} ℳ พิกัด [{gx}, {gy}] ช่อง #{cslot} (ยอดสะสม: {current_contrib:,} ℳ | v{client_ver})",
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

            self._last_synced_coord_key = coord_key
            self._last_synced_slot = slot
            self._last_synced_operative = char_name
            return True, "ส่งข้อมูลขึ้นระบบคลาวด์สำเร็จ"
        except Exception as exc:
            err_str = str(exc)
            if "404" in err_str:
                return False, "ไม่พบฐานข้อมูล: กรุณาตรวจสอบ Firebase URL ใน config.py (เช่น โซน asia-southeast1)"
            elif "401" in err_str:
                return False, "ถูกปฏิเสธการเข้าถึง: กฎของ Firebase ไม่อนุญาตให้แก้ไขข้อมูล"
            return False, f"Cloud Sync Error: {exc}"

    def sync_to_war_room(self, force_cloud: bool = False) -> Tuple[bool, str]:
        """
        Synchronize current war contribution to ARKS War Room telemetry & database storage.
        Resilient execution writing to local files and remote Firebase RTDB.
        Operates smoothly even when remote database is down, deleted, or corrupted.
        """
        now = time.time()
        db_payload = self.get_database_payload()

        payload = {
            "version": self.client_version,
            "client_version": self.client_version,
            "security_status": db_payload["security_status"],
            "version_security_valid": db_payload["version_security_valid"],
            "lastSync": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(now * 1000),
            "lastUpdated": int(now * 1000),
            # Core database fields
            "character_name": db_payload["character_name"],
            "meseta": db_payload["meseta"],
            "raw_meseta": db_payload["raw_meseta"],
            "sector_coord": db_payload["sector_coord"],
            "target_coord": db_payload["target_coord"],
            "coord_key": db_payload["coord_key"],
            "slot": db_payload["slot"],
            "farmingRateMhr": db_payload.get("farming_rate_mhr", 0),
            "farming_rate_mhr": db_payload.get("farming_rate_mhr", 0),
            "meseta_per_hour": db_payload.get("farming_rate_mhr", 0),
            "operative": {
                "name": self.operative_name,
                "character_name": self.operative_name,
                "client_version": self.client_version,
                "security_status": db_payload["security_status"],
                "targetSector": db_payload["target_coord"],
                "sectorCoord": db_payload["sector_coord"],
                "slot": db_payload["slot"],
                "sessionContribution": db_payload["meseta"],
                "rawContribution": self.session_contribution,
                "totalFarmed": self.total_farmed,
                "farmingRateMhr": db_payload.get("farming_rate_mhr", 0),
                "farming_rate_mhr": db_payload.get("farming_rate_mhr", 0),
                "meseta_per_hour": db_payload.get("farming_rate_mhr", 0),
            },
            "recentLogs": self.get_recent_logs(10),
        }

        saved_paths = []
        # 1. Save to ARKS War Room data directory if available (atomic write)
        telemetry_dir = os.path.join(self.war_room_path, "data")
        try:
            if os.path.exists(self.war_room_path):
                os.makedirs(telemetry_dir, exist_ok=True)
                sync_file = os.path.join(telemetry_dir, "live_war_telemetry.json")
                tmp_sync = sync_file + f".tmp.{os.getpid()}"
                with open(tmp_sync, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                    f.flush()
                    try:
                        os.fsync(f.fileno())
                    except OSError:
                        pass
                os.replace(tmp_sync, sync_file)
                saved_paths.append(sync_file)

                db_file = os.path.join(telemetry_dir, "database_meseta_records.json")
                tmp_db = db_file + f".tmp.{os.getpid()}"
                with open(tmp_db, "w", encoding="utf-8") as f:
                    json.dump(db_payload, f, ensure_ascii=False, indent=2)
                    f.flush()
                    try:
                        os.fsync(f.fileno())
                    except OSError:
                        pass
                os.replace(tmp_db, db_file)
        except Exception as exc:
            print(f"[WarService] Telemetry write to War Room failed: {exc}")

        # 2. Save to local app data cache (atomic write)
        try:
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            self._save_stats()
            saved_paths.append(self.stats_file)

            local_db_file = os.path.join(os.path.dirname(self.stats_file), "database_meseta_records.json")
            tmp_local_db = local_db_file + f".tmp.{os.getpid()}"
            with open(tmp_local_db, "w", encoding="utf-8") as f:
                json.dump(db_payload, f, ensure_ascii=False, indent=2)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass
            os.replace(tmp_local_db, local_db_file)
        except Exception as exc:
            print(f"[WarService] Local stats cache write failed: {exc}")

        # 3. Cloud Database Sync (Firebase Realtime Database) with Backoff & Offline Resilience
        cloud_ok = False
        cloud_msg = ""
        now = time.time()
        if self.firebase_url:
            in_backoff = (now < self._cloud_backoff_until) and not force_cloud
            if in_backoff:
                cloud_ok = False
                wait_sec = int(self._cloud_backoff_until - now)
                cloud_msg = f"พักการเชื่อมต่อคลาวด์ชั่วคราว (รออีก {wait_sec}s)"
            else:
                try:
                    cloud_ok, cloud_msg = self.sync_to_cloud_database()
                except Exception as exc:
                    cloud_msg = str(exc)
                    print(f"[WarService] Cloud database sync exception: {exc}")

                completed_at = time.time()
                if cloud_ok:
                    self._cloud_fail_count = 0
                    self._cloud_backoff_until = 0.0
                else:
                    self._cloud_fail_count += 1
                    backoff_delay = min(60.0, 5.0 * (2 ** min(self._cloud_fail_count - 1, 4)))
                    self._cloud_backoff_until = completed_at + backoff_delay

        self._last_cloud_ok = cloud_ok
        self._last_cloud_msg = cloud_msg
        self._last_sync_time = now
        active_contrib = payload.get("meseta", max(self.total_farmed, self.session_contribution))

        if saved_paths or cloud_ok:
            gx, gy, slot = self.target_coord.x, self.target_coord.y, self.target_coord.slot
            self.event_bus.emit("war_telemetry_synced", payload=payload)

            # In emergency (cannot connect to cloud database):
            # Keep buffered data secretly on disk/memory, but report connection failure to UI
            # so user only sees error and reconnecting status.
            if self.firebase_url and not cloud_ok:
                err_msg = cloud_msg or "ขาดการเชื่อมต่อกับฐานข้อมูล (กำลังรอเชื่อมต่อใหม่...)"
                return False, err_msg

            if cloud_ok:
                self.add_log(f"ซิงค์ข้อมูลสำเร็จ: ส่งยอด {active_contrib:,} ℳ พิกัด [{gx}, {gy}] ช่อง #{slot} ({self.operative_name})", "sync")
                return True, f"ซิงค์ข้อมูลเรียลไทม์สำเร็จ (+{active_contrib:,} ℳ)"
            return True, f"บันทึกข้อมูลเรียลไทม์เรียบร้อย (+{active_contrib:,} ℳ)"

        return False, "ไม่สามารถบันทึกข้อมูล Telemetry ได้"

    def _save_stats(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
            # Do not overwrite real character data with placeholder Operative
            if self.operative_name == "Operative" and os.path.exists(self.stats_file):
                try:
                    with open(self.stats_file, "r", encoding="utf-8") as rf:
                        existing = json.load(rf)
                        if isinstance(existing, dict):
                            existing_op = str(existing.get("operative_name", "")).strip()
                            if existing_op and existing_op != "Operative":
                                return
                except Exception:
                    pass

            with self._state_lock:
                data = {
                    "operative_name": self.operative_name,
                    "target_coord": list(self.target_coord),
                    "session_contribution": self.session_contribution,
                    "total_farmed": self.total_farmed,
                    "slot_farmed": dict(self.slot_farmed),
                    "last_active": time.time(),
                }

            # Resilient atomic file write: write to temp file then atomic replace
            tmp_file = self.stats_file + f".tmp.{os.getpid()}"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                try:
                    os.fsync(f.fileno())
                except OSError:
                    pass
            os.replace(tmp_file, self.stats_file)
        except Exception as exc:
            print(f"[WarService] Failed saving war stats: {exc}")

    def _load_saved_stats(self) -> None:
        if not os.path.exists(self.stats_file):
            return
        is_corrupted = False
        corrupt_reason = ""
        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                raise ValueError("war_stats.json is empty (0 bytes)")
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError(f"war_stats.json root is not a JSON dictionary (got {type(data).__name__})")

            saved_op = str(data.get("operative_name", "")).strip()
            # If current operative_name is placeholder "Operative" and saved file has a named operative, adopt it!
            if self.operative_name == "Operative" and saved_op and saved_op != "Operative":
                with self._state_lock:
                    self.operative_name = saved_op

            if data.get("operative_name") == self.operative_name or (self.operative_name == "Operative" and not saved_op):
                try:
                    saved_total = max(0, int(data.get("total_farmed", 0) or 0))
                except (ValueError, TypeError):
                    saved_total = 0
                with self._state_lock:
                    self.total_farmed = max(saved_total, self.session_contribution)
                    raw_slots = data.get("slot_farmed", {})
                    if isinstance(raw_slots, dict):
                        self.slot_farmed = {
                            str(k): max(0, int(v)) for k, v in raw_slots.items()
                            if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit())
                        }
                    if not self.slot_farmed and self.total_farmed > 0:
                        ck = f"{self.target_coord.x},{self.target_coord.y}#{self.target_coord.slot}"
                        self.slot_farmed[ck] = self.total_farmed

            # Target coordinate always defaults to Core (0, 0, 1) on startup regardless of previous session
        except Exception as exc:
            is_corrupted = True
            corrupt_reason = str(exc)
            print(f"[WarService] Failed loading war stats: {exc}")

        if is_corrupted:
            # Self-healing: Backup corrupted file and recreate a valid clean stats file
            try:
                corrupt_backup = self.stats_file + f".corrupt.{int(time.time())}"
                if os.path.exists(self.stats_file):
                    shutil.copy2(self.stats_file, corrupt_backup)
            except Exception:
                pass
            self.add_log(f"ตรวจพบไฟล์ฐานข้อมูลในเครื่องเสียหาย ({corrupt_reason}) — สำรองไฟล์เดิมและกู้คืนอัตโนมัติ", "warning")
            self._save_stats()


if __name__ == "__main__":
    print("=" * 60)
    print("🪐  NEKO Tracker — WarService Self-Test")
    print("=" * 60)
    service = WarService()
    print(f" [✓] Operative: {service.operative_name}")
    print(f" [✓] Target Coord: {service.target_coord} (Slot #{service.target_coord.slot})")
    print(" [✓] WarService initialized cleanly without login!")
    print("=" * 60)
