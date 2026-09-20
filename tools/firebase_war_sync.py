#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARKS War Room — Google Firebase Synchronization Tool (Python)
ใช้สำหรับให้ Neko Tracker, Bot หรือ External Script ส่งข้อมูลสถานะ Sector + 4 ช่องย่อย,
ยอดเงิน Meseta, และพิกัดสงครามขึ้น Google Firebase Realtime Database เพื่อให้หน้าเว็บแสดงผลสด

การเรียกใช้งาน:
    from tools.firebase_war_sync import ARKSFirebaseBroadcaster

    broadcaster = ARKSFirebaseBroadcaster(
        service_account_key_path="firebase-key.json",
        database_url="https://your-project-default-rtdb.firebaseio.com"
    )

    # ส่งตัวละคร Vale3neko ไปยึด Sector [0, 0] ที่ช่อง #1 ด้วยเงิน 25M
    broadcaster.sync_operative_sector(
        character_name="Vale3neko",
        meseta=25000000,
        sector_x=0,
        sector_y=0,
        slot=1
    )
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List, Optional

try:
    import firebase_admin
    from firebase_admin import credentials, db, firestore
    FIREBASE_ADMIN_AVAILABLE = True
except ImportError:
    FIREBASE_ADMIN_AVAILABLE = False

MIN_SECURE_VERSION = "7.1.0"
REVOKED_VERSIONS = {"7.0.0-alpha", "7.0.0"}


def parse_semver(v: str):
    if not v or not isinstance(v, str):
        return (0, 0, 0, "")
    clean = v.strip().lstrip("vV").strip()
    pre = ""
    if "-" in clean:
        parts_pre = clean.split("-", 1)
        clean = parts_pre[0].strip()
        pre = parts_pre[1].strip()
    nums = clean.split(".")
    major = int(nums[0]) if len(nums) > 0 and nums[0].isdigit() else 0
    minor = int(nums[1]) if len(nums) > 1 and nums[1].isdigit() else 0
    patch = int(nums[2]) if len(nums) > 2 and nums[2].isdigit() else 0
    return (major, minor, patch, pre)


def compare_semver(v1: str, v2: str) -> int:
    p1 = parse_semver(v1)
    p2 = parse_semver(v2)
    if p1[:3] > p2[:3]:
        return 1
    if p1[:3] < p2[:3]:
        return -1
    if p1[3] and not p2[3]:
        return -1
    if not p1[3] and p2[3]:
        return 1
    if p1[3] and p2[3]:
        if p1[3] < p2[3]:
            return -1
        if p1[3] > p2[3]:
            return 1
    return 0


def is_version_secure(version: str, min_version: str = MIN_SECURE_VERSION) -> bool:
    if not version or not isinstance(version, str):
        return False
    v_clean = version.strip().lower().lstrip("v").strip()
    for rev in REVOKED_VERSIONS:
        if v_clean == rev.lower().lstrip("v").strip():
            return False
    return compare_semver(version, min_version) >= 0


class ARKSFirebaseBroadcaster:
    def __init__(
        self,
        service_account_key_path: Optional[str] = None,
        database_url: Optional[str] = None,
        base_path: str = "arks_war_room",
    ) -> None:
        """
        เชื่อมต่อ Google Firebase Admin SDK หรือ REST Realtime Database
        :param service_account_key_path: พาธของไฟล์ JSON Service Account จาก Firebase Console
        :param database_url: URL ของ Realtime Database (เช่น https://your-project-default-rtdb.firebaseio.com)
        :param base_path: Root key ใน Realtime Database (ค่าเริ่มต้น: 'arks_war_room')
        """
        self.base_path = base_path.strip("/")
        self.database_url = database_url.rstrip("/") if database_url else None
        self.rtdb = None
        self.app = None

        if service_account_key_path:
            if not os.path.exists(service_account_key_path):
                raise FileNotFoundError(f"ไม่พบไฟล์ Service Account Key ที่: {service_account_key_path}")

            if FIREBASE_ADMIN_AVAILABLE:
                cred = credentials.Certificate(service_account_key_path)
                options = {}
                if self.database_url:
                    options['databaseURL'] = self.database_url

                if not firebase_admin._apps:
                    self.app = firebase_admin.initialize_app(cred, options)
                else:
                    self.app = firebase_admin.get_app()

                self.rtdb = db if self.database_url else None
                print(f"[✓] เชื่อมต่อ Firebase Admin SDK สำเร็จ (Base path: {self.base_path})")
            else:
                print(f"[!] ไม่พบแพ็กเกจ firebase-admin ทำงานผ่านโหมด REST Fallback (URL: {self.database_url})")
        elif self.database_url:
            print(f"[✓] เชื่อมต่อ Firebase REST RTDB สำเร็จ (Base path: {self.base_path})")

    @staticmethod
    def is_version_secure(version: str) -> bool:
        """Verify client version against security policy."""
        return is_version_secure(version)

    def fetch_version_control_policy(self, timeout: float = 5.0) -> Dict[str, Any]:
        """
        อ่านนโยบายเวอร์ชันล่าสุดจาก Firebase RTDB (/arks_war_room/version_control)
        """
        if self.rtdb:
            ref = self.rtdb.reference(f"{self.base_path}/version_control")
            val = ref.get()
            return val if isinstance(val, dict) else {}
        elif self.database_url:
            try:
                url = f"{self.database_url}/{self.base_path}/version_control.json"
                req = urllib.request.Request(url, headers={"User-Agent": "NEKOTracker/7.1.0"})
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data if isinstance(data, dict) else {}
            except Exception as e:
                print(f"[!] ไม่สามารถอ่าน version_control จาก Firebase: {e}")
                return {}
        return {}

    def update_version_control_policy(
        self,
        latest_version: str,
        min_secure_version: str = "7.1.0",
        revoked_versions: Optional[Dict[str, bool]] = None,
        announcement: str = "",
        download_url: str = "",
        timeout: float = 5.0,
    ) -> bool:
        """
        อัปเดตนโยบายเวอร์ชันล่าสุดขึ้น Firebase RTDB (/arks_war_room/version_control)
        """
        if revoked_versions is None:
            revoked_versions = {"7_0_0-alpha": True, "7_0_0": True}
        payload = {
            "latest_version": latest_version,
            "min_secure_version": min_secure_version,
            "revoked_versions": revoked_versions,
            "announcement": announcement,
            "download_url": download_url,
            "last_updated": int(time.time() * 1000),
        }
        if self.rtdb:
            ref = self.rtdb.reference(f"{self.base_path}/version_control")
            ref.set(payload)
            print(f"[✓] อัปเดตนโยบายเวอร์ชันสำเร็จ: latest={latest_version}, min={min_secure_version}")
            return True
        elif self.database_url:
            try:
                url = f"{self.database_url}/{self.base_path}/version_control.json"
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="PUT",
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    print(f"[✓] อัปเดตนโยบายเวอร์ชันสำเร็จ: latest={latest_version}, min={min_secure_version}")
                    return True
            except Exception as e:
                print(f"[!] ไม่สามารถอัปเดต version_control: {e}")
                return False
        return False

    # -------------------------------------------------------------
    # SECTOR WAR — OPERATIVE FARMING (4 SLOTS PER SECTOR)
    # -------------------------------------------------------------
    def sync_operative_sector(
        self,
        character_name: str,
        meseta: int,
        sector_x: int,
        sector_y: int,
        slot: int = 1,
        client_version: str = "7.1.0",
    ) -> bool:
        """
        ซิงค์พิกัดและยอดเงินของตัวละครเข้าสู่ระบบ Sector + 4 ช่องย่อย (NW: 1, NE: 2, SW: 3, SE: 4)
        :param character_name: ชื่อตัวละคร (Primary Key) เช่น "Vale3neko"
        :param meseta: ยอดเงิน Meseta ที่สะสม/ฟาร์มใส่ในช่อง
        :param sector_x: พิกัด X ของ Sector ที่ต้องการฟาร์ม (-12 ถึง +25)
        :param sector_y: พิกัด Y ของ Sector ที่ต้องการฟาร์ม (-11 ถึง +9)
        :param slot: ช่องย่อย (1: NW บนซ้าย, 2: NE บนขวา, 3: SW ล่างซ้าย, 4: SE ล่างขวา)
        :param client_version: เลขเวอร์ชันไคลเอนต์ที่ส่งเพื่อตรวจความปลอดภัย (ค่าเริ่มต้น: 7.1.0)
        """
        now_ms = int(time.time() * 1000)
        # Clamping
        sector_x = max(-12, min(25, int(sector_x)))
        sector_y = max(-11, min(9, int(sector_y)))
        slot = max(1, min(4, int(slot)))
        coord_key = f"{sector_x},{sector_y}"

        is_secure = is_version_secure(client_version)
        counted_meseta = meseta if is_secure else 0
        sec_status = "SECURE" if is_secure else "REVOKED_VERSION_INSECURE"

        # 1. ข้อมูล Operative
        op_payload = {
            "character_name": character_name,
            "meseta": counted_meseta,
            "raw_meseta": meseta,
            "client_version": client_version,
            "version": client_version,
            "security_status": sec_status,
            "version_security_valid": is_secure,
            "sector_coord": {"x": sector_x, "y": sector_y, "slot": slot},
            "coord_key": coord_key,
            "slot": slot,
            "lastUpdated": now_ms,
        }

        # 2. ข้อมูล Challenger ใน Sector รวม
        sec_payload = {
            "character_name": character_name,
            "meseta": counted_meseta,
            "client_version": client_version,
            "security_status": sec_status,
            "status": "claimed" if (is_secure and counted_meseta >= 25_000_000) else ("BLOCKED_INSECURE_VERSION" if not is_secure else "contributing"),
            "slot": slot,
            "lastUpdated": now_ms,
        }

        # 3. ข้อมูล Challenger ใน Sub-Cell รายช่องย่อย
        sub_payload = {
            "character_name": character_name,
            "meseta": counted_meseta,
            "client_version": client_version,
            "security_status": sec_status,
            "lastUpdated": now_ms,
        }

        # Sync via Firebase Admin SDK if active
        if self.rtdb:
            ref_op = self.rtdb.reference(f"{self.base_path}/operatives/{character_name}")
            ref_op.update(op_payload)

            ref_sec = self.rtdb.reference(f"{self.base_path}/sectors/{coord_key}/challengers/{character_name}")
            ref_sec.update(sec_payload)

            ref_sub = self.rtdb.reference(f"{self.base_path}/sectors/{coord_key}/sub_cells/{slot}/challengers/{character_name}")
            ref_sub.update(sub_payload)

        # Fallback via REST API if database_url is provided
        elif self.database_url:
            safe_char = urllib.parse.quote(str(character_name))
            safe_coord = urllib.parse.quote(coord_key)
            base = self.database_url

            self._rest_put(f"{base}/{self.base_path}/operatives/{safe_char}.json", op_payload)
            self._rest_put(f"{base}/{self.base_path}/sectors/{safe_coord}/challengers/{safe_char}.json", sec_payload)
            self._rest_put(f"{base}/{self.base_path}/sectors/{safe_coord}/sub_cells/{slot}/challengers/{safe_char}.json", sub_payload)

        if not is_secure:
            print(f"[!] คำเตือนความปลอดภัย: ไคลเอนต์เวอร์ชัน {client_version} ไม่ปลอดภัย (ถูกแก้เป็น 7.1.0) ยอดเงินจะไม่ถูกนับเข้าสู่ฐานข้อมูล (บันทึก meseta = 0)")
            return False
        else:
            print(f"[✓] ซิงค์ Sector: ตัวละคร {character_name} (v{client_version}) ➔ พิกัด [{sector_x}, {sector_y}] ช่อง #{slot} | เงินสะสม {counted_meseta:,} ℳ")
            return True

    def _rest_put(self, url: str, data: Dict[str, Any], timeout: float = 3.5) -> bool:
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="PUT",
            )
            with urllib.request.urlopen(req, timeout=timeout):
                return True
        except Exception as exc:
            # Silently catch network errors in broadcaster
            return False

    # -------------------------------------------------------------
    # PLANETARY TELEMETRY
    # -------------------------------------------------------------
    def update_planet(
        self,
        planet_id: str,
        owner_team_id: str,
        current_value: int,
        injected_funds: int = 0,
        protection_hours: int = 24,
        status: str = "LIBERATED",
    ) -> None:
        """
        อัปเดตข้อมูลดวงดาวรายดวงขึ้น Firebase
        """
        now_ms = int(time.time() * 1000)
        protection_until_ms = now_ms + (protection_hours * 3600 * 1000) if protection_hours > 0 else 0
        payload = {
            "id": planet_id,
            "ownerTeamId": owner_team_id,
            "currentValue": current_value,
            "injectedFunds": injected_funds,
            "protectionHoursLeft": protection_hours,
            "protectionUntil": protection_until_ms,
            "status": status,
            "lastUpdated": now_ms,
        }
        if self.rtdb:
            ref = self.rtdb.reference(f"{self.base_path}/planets/{planet_id}")
            ref.update(payload)
        elif self.database_url:
            self._rest_put(f"{self.database_url}/{self.base_path}/planets/{planet_id}.json", payload)
        print(f"[✓] อัปเดตดาว {planet_id}: เจ้าของ {owner_team_id} | มูลค่า {current_value:,} ℳ | โพรเท็ก {protection_hours}h")

    # -------------------------------------------------------------
    # TEAM TREASURY & ROSTER
    # -------------------------------------------------------------
    def update_team(
        self,
        team_id: str,
        name: str,
        tag: str,
        emblem: str,
        color: str,
        leader: str,
        team_treasury: int,
        members: List[Dict[str, Any]],
        controlled_planets: List[str],
    ) -> None:
        """
        อัปเดตสถานะทีม เงินกองทุน และรายชื่อสมาชิกร่วมทัพ
        """
        payload = {
            "id": team_id,
            "name": name,
            "tag": tag,
            "emblem": emblem,
            "color": color,
            "leader": leader,
            "teamTreasury": team_treasury,
            "members": members,
            "controlledPlanets": controlled_planets,
            "lastUpdated": int(time.time() * 1000),
        }
        if self.rtdb:
            ref = self.rtdb.reference(f"{self.base_path}/teams/{team_id}")
            ref.update(payload)
        elif self.database_url:
            self._rest_put(f"{self.database_url}/{self.base_path}/teams/{team_id}.json", payload)
        print(f"[✓] อัปเดตทีม {name} [{tag}]: กองทุน {team_treasury:,} ℳ")

    # -------------------------------------------------------------
    # CAMPAIGN TELEMETRY
    # -------------------------------------------------------------
    def update_campaign(self, current_day: int, current_hour: int = 12, global_treasury: int = 0) -> None:
        payload = {
            "currentDay": current_day,
            "currentHour": current_hour,
            "globalTreasury": global_treasury,
            "lastUpdated": int(time.time() * 1000),
        }
        if self.rtdb:
            ref = self.rtdb.reference(f"{self.base_path}/campaign")
            ref.update(payload)
        elif self.database_url:
            self._rest_put(f"{self.database_url}/{self.base_path}/campaign.json", payload)
        print(f"[✓] อัปเดตแคมเปญ: วันที่ {current_day} | กองทุนรวม {global_treasury:,} ℳ")

    # -------------------------------------------------------------
    # WAR LOGS
    # -------------------------------------------------------------
    def push_war_log(self, message: str, log_type: str = "WAR", day: Optional[int] = None) -> None:
        payload = {
            "timestamp": int(time.time() * 1000),
            "time": time.strftime("%H:%M:%S"),
            "day": day or 1,
            "type": log_type,
            "message": message,
        }
        if self.rtdb:
            ref = self.rtdb.reference(f"{self.base_path}/war_logs")
            ref.push(payload)
        elif self.database_url:
            try:
                req = urllib.request.Request(
                    f"{self.database_url}/{self.base_path}/war_logs.json",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=3.5):
                    pass
            except Exception:
                pass
        print(f"[✓] บันทึกสงคราม: {message}")


if __name__ == "__main__":
    print("=" * 60)
    print("🪐 ARKS War Room — Google Firebase Sync Broadcaster")
    print("=" * 60)
    print("ตัวอย่างการเรียกใช้งาน:")
    print("""
    from tools.firebase_war_sync import ARKSFirebaseBroadcaster

    broadcaster = ARKSFirebaseBroadcaster(
        service_account_key_path="firebase-key.json",
        database_url="https://your-project-default-rtdb.firebaseio.com"
    )

    # ส่งตัวละคร Vale3neko ไปยึด Sector [0, 0] ที่ช่อง #1 ด้วยเงิน 25M
    broadcaster.sync_operative_sector(
        character_name="Vale3neko",
        meseta=25000000,
        sector_x=0,
        sector_y=0,
        slot=1
    )
    """)
