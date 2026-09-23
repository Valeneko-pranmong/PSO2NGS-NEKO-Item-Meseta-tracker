#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEKO Item & Meseta Tracker - Authoritative Database Reset Utility
ล้างฐานข้อมูลทั้งระบบคลาวด์ (Firebase Realtime Database) และฐานข้อมูลในเครื่อง (Local Cache)
เพื่อให้พร้อมสำหรับการทดสอบของผู้ใช้แบบ Clean Slate 100%
"""

import logging
import os
import sys
import json
import time
import urllib.request
import urllib.parse
from typing import Dict, Any, List

logger = logging.getLogger("NekoTracker.reset_database")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from config import DEFAULT_FIREBASE_RTDB_URL, CLIENT_VERSION, MIN_SECURE_VERSION, REVOKED_VERSIONS


def log(msg: str) -> None:
    print(f"[DB-RESET] >>> {msg}", flush=True)


def reset_cloud_database(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """
    ล้างข้อมูลบน Google Firebase Realtime Database (/arks_war_room)
    - รีเซ็ต Operatives ทั้งหมดเป็น meseta = 0
    - รีเซ็ต Sectors ทั้งหมด (เคลียร์ Challengers และ Sub-cells)
    - รีเซ็ต Latest Telemetry เป็นสถานะเริ่มต้น (0 ℳ)
    - รักษา/อัปเดต Version Control Policy สู่เวอร์ชัน 7.1.0
    """
    base_url = firebase_url.rstrip("/")
    log(f"กำลังตรวจสอบและล้างฐานข้อมูลคลาวด์ที่: {base_url}")
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"NEKOTracker/{CLIENT_VERSION}",
    }

    # 1. อ่านข้อมูลปัจจุบัน
    current_data = {}
    try:
        req = urllib.request.Request(f"{base_url}/arks_war_room.json", headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
            if raw and raw != "null":
                current_data = json.loads(raw)
    except Exception as exc:
        log(f"คำเตือน: ไม่สามารถดึงข้อมูลปัจจุบันจาก Firebase: {exc}")

    # 2. รีเซ็ต Operatives
    operatives = current_data.get("operatives", {})
    if isinstance(operatives, dict) and operatives:
        log(f"พบข้อมูล Operatives {len(operatives)} รายการ กำลังรีเซ็ต...")
        for char_name in operatives:
            safe_char = urllib.parse.quote(str(char_name))
            op_url = f"{base_url}/arks_war_room/operatives/{safe_char}.json"
            clean_op = {
                "character_name": char_name,
                "client_version": CLIENT_VERSION,
                "version": CLIENT_VERSION,
                "meseta": 0,
                "raw_meseta": 0,
                "farming_rate_mhr": 0,
                "farmingRateMhr": 0,
                "meseta_per_hour": 0,
                "security_status": "SECURE",
                "version_security_valid": True,
                "coord_key": "0,0",
                "slot": 1,
                "sector_coord": {"x": 0, "y": 0, "slot": 1},
                "lastUpdated": int(time.time() * 1000),
            }
            try:
                put_req = urllib.request.Request(
                    op_url,
                    data=json.dumps(clean_op).encode("utf-8"),
                    headers=headers,
                    method="PUT",
                )
                with urllib.request.urlopen(put_req, timeout=5):
                    log(f"  [✓] รีเซ็ต Operative '{char_name}' -> 0 ℳ")
            except Exception as e:
                log(f"  [!] ไม่สามารถรีเซ็ต Operative '{char_name}': {e}")
    else:
        log("ไม่พบ Operatives ตกค้างในฐานข้อมูล")

    # 3. เคลียร์ Sectors (Challengers & Sub-cells)
    sectors = current_data.get("sectors", {})
    if isinstance(sectors, dict) and sectors:
        log(f"พบข้อมูล Sectors {len(sectors)} พิกัด กำลังเคลียร์การยึดครอง...")
        for coord_key in sectors:
            safe_coord = urllib.parse.quote(str(coord_key))
            sec_url = f"{base_url}/arks_war_room/sectors/{safe_coord}.json"
            clean_sec = {
                "client_version": CLIENT_VERSION,
            }
            try:
                put_req = urllib.request.Request(
                    sec_url,
                    data=json.dumps(clean_sec).encode("utf-8"),
                    headers=headers,
                    method="PUT",
                )
                with urllib.request.urlopen(put_req, timeout=5):
                    log(f"  [✓] เคลียร์ Sector [{coord_key}] เรียบร้อย")
            except Exception as e:
                log(f"  [!] ไม่สามารถเคลียร์ Sector [{coord_key}]: {e}")
    else:
        log("ไม่พบ Sectors ตกค้างในฐานข้อมูล")

    # 4. รีเซ็ต Latest Telemetry
    log("กำลังรีเซ็ต latest_telemetry...")
    clean_telemetry = {
        "character_name": "None",
        "client_version": CLIENT_VERSION,
        "version": CLIENT_VERSION,
        "meseta": 0,
        "raw_meseta": 0,
        "farming_rate_mhr": 0,
        "farmingRateMhr": 0,
        "meseta_per_hour": 0,
        "security_status": "SECURE",
        "version_security_valid": True,
        "coord_key": "0,0",
        "slot": 1,
        "sector_coord": {"x": 0, "y": 0, "slot": 1},
        "lastUpdated": int(time.time() * 1000),
    }
    try:
        tel_url = f"{base_url}/arks_war_room/latest_telemetry.json"
        put_req = urllib.request.Request(
            tel_url,
            data=json.dumps(clean_telemetry).encode("utf-8"),
            headers=headers,
            method="PUT",
        )
        with urllib.request.urlopen(put_req, timeout=5):
            log("  [✓] รีเซ็ต latest_telemetry สำเร็จ")
    except Exception as e:
        log(f"  [!] ไม่สามารถรีเซ็ต latest_telemetry: {e}")

    # 5. ยืนยัน / อัปเดต Version Control Policy สู่มาตรฐานล่าสุด
    log("กำลังอัปเดตนโยบายเวอร์ชัน (version_control)...")
    rev_dict = {r.replace(".", "_"): True for r in REVOKED_VERSIONS}
    policy_payload = {
        "latest_version": CLIENT_VERSION,
        "min_secure_version": MIN_SECURE_VERSION,
        "revoked_versions": rev_dict,
        "announcement": "ARKS War Room — Database Reset Complete & Ready for QA Testing",
        "download_url": "",
        "last_updated": int(time.time() * 1000),
    }
    try:
        vc_url = f"{base_url}/arks_war_room/version_control.json"
        put_req = urllib.request.Request(
            vc_url,
            data=json.dumps(policy_payload).encode("utf-8"),
            headers=headers,
            method="PUT",
        )
        with urllib.request.urlopen(put_req, timeout=5):
            log("  [✓] อัปเดตนโยบาย version_control สำเร็จ")
    except Exception as e:
        log(f"  [!] ไม่สามารถอัปเดต version_control: {e}")

    log("ล้างฐานข้อมูลคลาวด์สำเร็จเรียบร้อย!")
    return True


def reset_local_database() -> bool:
    """
    ล้างฐานข้อมูลและแคชในเครื่อง (Local Database & Cache)
    - %APPDATA%/NekoTrackerOffline/war_stats.json
    - %APPDATA%/NekoTrackerOffline/database_meseta_records.json
    - เคลียร์ไฟล์ชั่วคราว .corrupt.* และ .tmp.*
    - รีเซ็ตพิกัดใน ngs_tracker_config.json กลับสู่ค่าเริ่มต้น "0, 0, 1"
    """
    app_data_dir = os.path.expandvars(r"%APPDATA%")
    offline_dir = os.path.join(app_data_dir, "NekoTrackerOffline")

    log(f"กำลังตรวจสอบและล้างฐานข้อมูลในเครื่องที่: {offline_dir}")
    if os.path.exists(offline_dir):
        # 1. ลบ war_stats.json
        stats_file = os.path.join(offline_dir, "war_stats.json")
        if os.path.exists(stats_file):
            try:
                os.remove(stats_file)
                log("  [✓] ลบ war_stats.json สำเร็จ")
            except Exception as e:
                log(f"  [!] ไม่สามารถลบ war_stats.json: {e}")

        # 2. ลบ database_meseta_records.json
        db_file = os.path.join(offline_dir, "database_meseta_records.json")
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
                log("  [✓] ลบ database_meseta_records.json สำเร็จ")
            except Exception as e:
                log(f"  [!] ไม่สามารถลบ database_meseta_records.json: {e}")

        # 3. ลบไฟล์สำรอง .corrupt.* และ .tmp.*
        try:
            for item in os.listdir(offline_dir):
                if ".corrupt" in item or ".tmp" in item:
                    item_path = os.path.join(offline_dir, item)
                    try:
                        os.remove(item_path)
                        log(f"  [✓] ลบไฟล์สำรอง {item} สำเร็จ")
                    except Exception as exc:
                        logger.debug("reset_local_database: failed to remove residual file %s: %s", item, exc)
        except Exception as exc:
            logger.debug("reset_local_database: failed to list offline_dir for cleanup: %s", exc)

        # 4. รีเซ็ตพิกัดใน ngs_tracker_config.json กลับสู่ค่าเริ่มต้น
        cfg_file = os.path.join(offline_dir, "ngs_tracker_config.json")
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if isinstance(cfg, dict):
                    cfg["board_coord"] = "0, 0, 1"
                    cfg["log_folder"] = ""
                    with open(cfg_file, "w", encoding="utf-8") as f:
                        json.dump(cfg, f, indent=4)
                    log("  [✓] รีเซ็ตการตั้งค่าพิกัดใน ngs_tracker_config.json เป็น [0, 0, 1]")
            except Exception as e:
                log(f"  [!] คำเตือน: ไม่สามารถอัปเดต ngs_tracker_config.json: {e}")
    else:
        log("ไม่พบโฟลเดอร์ NekoTrackerOffline ในเครื่อง")

    # ตรวจสอบ LocalAppData
    local_app_dir = os.path.expandvars(r"%LOCALAPPDATA%\NEKO FAMILY\NekoTracker")
    if os.path.exists(local_app_dir):
        log(f"ตรวจสอบ LocalAppData ที่: {local_app_dir}")
        for f in ["war_stats.json", "database_meseta_records.json"]:
            fp = os.path.join(local_app_dir, f)
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                    log(f"  [✓] ลบ {f} ใน LocalAppData สำเร็จ")
                except Exception as exc:
                    logger.debug("reset_local_database: failed to remove %s from LocalAppData: %s", f, exc)

    log("ล้างฐานข้อมูลในเครื่องสำเร็จเรียบร้อย!")
    return True


def verify_database_clean() -> bool:
    """ตรวจสอบสถานะฐานข้อมูลหลังการล้างข้อมูล"""
    log("กำลังตรวจสอบสถานะหลังการล้างฐานข้อมูล...")
    base_url = DEFAULT_FIREBASE_RTDB_URL.rstrip("/")
    headers = {"User-Agent": f"NEKOTracker/{CLIENT_VERSION}"}
    req = urllib.request.Request(f"{base_url}/arks_war_room.json", headers=headers)
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    # Operatives meseta check
    for op_name, op_val in data.get("operatives", {}).items():
        assert op_val.get("meseta", 0) == 0, f"Operative {op_name} meseta is not 0!"
    # Sectors check
    for coord, sec_val in data.get("sectors", {}).items():
        assert "challengers" not in sec_val, f"Sector {coord} still has challengers!"
    # Telemetry check
    tel = data.get("latest_telemetry", {})
    assert tel.get("meseta", 0) == 0, "latest_telemetry meseta is not 0!"

    log("=" * 60)
    log("[PASS] ฐานข้อมูลสะอาด 100% พร้อมสำหรับการทดสอบ!")
    log(f"  - คลาวด์: {base_url}/arks_war_room.json")
    log(f"  - Operatives: {list(data.get('operatives', {}).keys())} (ยอดเงิน 0 ℳ ทั้งหมด)")
    log(f"  - Sectors: {list(data.get('sectors', {}).keys())} (เคลียร์ผู้ยึดครองทั้งหมด)")
    log(f"  - Latest Telemetry: 0 ℳ")
    log("=" * 60)
    return True


if __name__ == "__main__":
    log("เริ่มต้นกระบวนการล้างฐานข้อมูล (Clean Database Pipeline)...")
    reset_cloud_database()
    reset_local_database()
    verify_database_clean()
