from __future__ import annotations

import json
import os
import re
import time
import threading
from typing import Any, Dict, List, Optional, Tuple
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
    from config import DEFAULT_FIREBASE_RTDB_URL
except Exception:
    DEFAULT_FIREBASE_RTDB_URL = "https://arks-war-room-default-rtdb.asia-southeast1.firebasedatabase.app"


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
        self.target_coord: Tuple[int, int] = (0, 0)

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

    def on_board_coord_changed(self, coord: Any = None, **kwargs) -> None:
        if coord is not None:
            self.set_target_coord(coord)

    @staticmethod
    def parse_coordinate(coord_input: Any) -> Tuple[int, int]:
        """
        Parse various coordinate representations into an integer (x, y) tuple:
        Accepts: "0, 0", "[0, 0]", "(0, 0)", "0 0", "X: 5, Y: -3", dict {"x": 5, "y": -3}, tuple/list.
        Defaults to (0, 0) on failure.
        """
        if isinstance(coord_input, (list, tuple)) and len(coord_input) >= 2:
            try:
                return (int(coord_input[0]), int(coord_input[1]))
            except (ValueError, TypeError):
                pass
        elif isinstance(coord_input, dict):
            try:
                gx = coord_input.get("x", coord_input.get("X", 0))
                gy = coord_input.get("y", coord_input.get("Y", 0))
                return (int(gx), int(gy))
            except (ValueError, TypeError):
                pass
        elif isinstance(coord_input, str):
            cleaned = re.sub(r'[^0-9\-,\s]', '', coord_input).strip()
            if ',' in cleaned:
                parts = [p.strip() for p in cleaned.split(',') if p.strip()]
            else:
                parts = cleaned.split()
            if len(parts) >= 2:
                try:
                    return (int(parts[0]), int(parts[1]))
                except ValueError:
                    pass
        return (0, 0)

    def set_target_coord(self, coord_input: Any) -> Tuple[int, int]:
        """Update active board coordinate, log change, and trigger realtime Firebase sync."""
        parsed = self.parse_coordinate(coord_input)
        if parsed != self.target_coord:
            self.target_coord = parsed
            gx, gy = parsed
            self.add_log(f"อัปเดตพิกัดบนกระดานเป็น [{gx}, {gy}]", "info")
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
        # Backward compatibility: sync if user info passed
        if user:
            name = user.get("character_name") or user.get("callsign") or user.get("username") or "Operative"
            self.set_operative(name)
            self.trigger_realtime_sync()

    def on_meseta_earned(self, amount: int, wallet: int = 0) -> None:
        if amount > 0:
            self.session_contribution += amount
            self.total_farmed += amount
            gx, gy = self.target_coord
            self.add_log(
                f"+{amount:,} ℳ พิกัด [{gx}, {gy}] (ยอดสะสม: {self.session_contribution:,} ℳ)",
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
        - sector_coord / target_coord: Board coordinate entered by user
        """
        gx, gy = self.target_coord
        return {
            "character_name": self.operative_name,
            "meseta": self.session_contribution,
            "sector_coord": f"{gx}, {gy}",
            "target_coord": {"x": gx, "y": gy},
            "coord_key": f"{gx},{gy}",
            "farming_rate_mhr": round(self.get_live_rate()),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(time.time() * 1000),
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
                # Micro-debounce to batch rapid successive drops (e.g. PSE burst)
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
        Uses pure Python standard library (urllib.request) for zero dependencies & offline resilience.
        """
        if not self.firebase_url:
            return False, "ไม่ได้ระบุ Firebase Database URL"

        base_url = self.firebase_url.rstrip("/")
        db_payload = self.get_database_payload()
        now = time.time()

        char_name = self.operative_name or "Operative"
        # Sanitize key for Firebase RTDB (disallows ., $, #, [, ], /, and control characters)
        safe_key = "".join(
            c for c in char_name
            if c not in '.$#[]/\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f'
        ).strip() or "Operative"

        telemetry_payload = {
            "character_name": db_payload["character_name"],
            "meseta": db_payload["meseta"],
            "sector_coord": db_payload["sector_coord"],
            "target_coord": db_payload["target_coord"],
            "coord_key": db_payload["coord_key"],
            "farming_rate_mhr": db_payload["farming_rate_mhr"],
            "updated_at": db_payload["updated_at"],
            "timestamp": db_payload["timestamp"],
        }

        try:
            # 1. Update individual operative record with character_name as primary key
            url_op = f"{base_url}/arks_war_room/operatives/{urllib.parse.quote(safe_key)}.json"
            req_op = urllib.request.Request(
                url_op,
                data=json.dumps(telemetry_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            with urllib.request.urlopen(req_op, timeout=timeout) as resp:
                pass

            # 2. Update sector challenger record
            coord_key = db_payload["coord_key"]
            url_sec = f"{base_url}/arks_war_room/sectors/{urllib.parse.quote(coord_key)}/challengers/{urllib.parse.quote(safe_key)}.json"
            req_sec = urllib.request.Request(
                url_sec,
                data=json.dumps(telemetry_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            try:
                with urllib.request.urlopen(req_sec, timeout=timeout) as resp:
                    pass
            except Exception:
                pass

            # 3. Update global latest telemetry
            url_tel = f"{base_url}/arks_war_room/latest_telemetry.json"
            req_tel = urllib.request.Request(
                url_tel,
                data=json.dumps(telemetry_payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            try:
                with urllib.request.urlopen(req_tel, timeout=timeout) as resp:
                    pass
            except Exception:
                pass

            # 4. Add to live war logs when contribution increases
            if self.session_contribution > self._last_logged_contribution:
                gain = self.session_contribution - self._last_logged_contribution
                self._last_logged_contribution = self.session_contribution
                gx, gy = self.target_coord
                log_entry = {
                    "time": time.strftime("%H:%M:%S"),
                    "day": 1,
                    "type": "MESETA",
                    "character_name": char_name,
                    "meseta": self.session_contribution,
                    "gain": gain,
                    "coord": f"{gx}, {gy}",
                    "message": f"{char_name} เก็บเกี่ยว +{gain:,} ℳ พิกัด [{gx}, {gy}] (ยอดสะสม: {self.session_contribution:,} ℳ)",
                    "timestamp": int(now * 1000),
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
            "version": "1.0",
            "lastSync": time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(now * 1000),
            # Core database fields
            "character_name": db_payload["character_name"],
            "meseta": db_payload["meseta"],
            "sector_coord": db_payload["sector_coord"],
            "target_coord": db_payload["target_coord"],
            "coord_key": db_payload["coord_key"],
            "farmingRateMhr": round(self.get_live_rate()),
            "operative": {
                "name": self.operative_name,
                "character_name": self.operative_name,
                "targetSector": db_payload["target_coord"],
                "sectorCoord": db_payload["sector_coord"],
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

                # Save standalone database table format
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
            gx, gy = self.target_coord
            self.add_log(f"ซิงค์ข้อมูลสำเร็จ: ส่งยอด {self.session_contribution:,} ℳ พิกัด [{gx}, {gy}] ({self.operative_name})", "sync")
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
    print(f" [✓] Target Coord: {service.target_coord}")
    print(" [✓] WarService initialized cleanly without login!")
    print("=" * 60)
