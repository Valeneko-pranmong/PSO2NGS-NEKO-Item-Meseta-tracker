#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARKS War Room — All-in-One Database Admin & Factory Reset Utility
เครื่องมือสารพัดประโยชน์ระดับ Admin / Dev Ops:
1. สร้าง/ติดตั้งโครงสร้างเริ่มต้น (Setup / Bootstrap) หลังลบฐานข้อมูลเป็น null
2. ลบแบบปลอดภัย คืนค่าโรงงาน (Safe Factory Reset: ลบชื่อตัวละคร, เงินทุกช่อง, ล้างแคชในเครื่อง)
3. รันทั้งสองอย่างพร้อมกันในคลิกเดียว (All-in-One: Factory Reset & Setup Fresh)
4. ตรวจสอบสถานะความพร้อมสดบน Google Firebase Realtime Database (Verify)
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import argparse
from typing import Dict, Any, Optional

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

try:
    from config import (
        DEFAULT_FIREBASE_RTDB_URL,
        CLIENT_VERSION,
        MIN_SECURE_VERSION,
        REVOKED_VERSIONS,
    )
except ImportError:
    DEFAULT_FIREBASE_RTDB_URL = os.getenv(
        "FIREBASE_RTDB_URL",
        os.getenv("ARKS_FIREBASE_RTDB_URL", "")
    )
    CLIENT_VERSION = "7.1.0"
    MIN_SECURE_VERSION = "7.1.0"
    REVOKED_VERSIONS = ["7.0.0-alpha", "7.0.0"]

BASE_PATH = "arks_war_room"

# ปรับปรุง Windows Console Output ให้รองรับ UTF-8 และสัญลักษณ์ Unicode (เช่น ℳ) ป้องกันแครชบน CP874 / CP437
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def log_header(msg: str) -> None:
    print(f"\n=================================================================", flush=True)
    print(f"  {msg}", flush=True)
    print(f"=================================================================", flush=True)


def log_step(step_num: str, msg: str) -> None:
    print(f"\n[{step_num}] {msg}", flush=True)


def log_ok(msg: str) -> None:
    print(f"  [✓] {msg}", flush=True)


def log_warn(msg: str) -> None:
    print(f"  [!] คำเตือน: {msg}", flush=True)


def log_err(msg: str) -> None:
    print(f"  [✗] ข้อผิดพลาด: {msg}", flush=True)


def make_request(url: str, method: str = "GET", data: Optional[Dict[str, Any]] = None, timeout: float = 6.0) -> Optional[Dict[str, Any]]:
    headers = {
        "User-Agent": f"NEKOTracker/{CLIENT_VERSION}",
        "Content-Type": "application/json; charset=utf-8",
    }
    encoded_data = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8").strip()
            if not raw or raw == "null":
                return None
            return json.loads(raw)
    except urllib.error.HTTPError as he:
        raise he
    except Exception as exc:
        raise exc


def get_cloud_state(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> Optional[Dict[str, Any]]:
    base_url = firebase_url.rstrip("/")
    url = f"{base_url}/{BASE_PATH}.json"
    return make_request(url, method="GET")


# -----------------------------------------------------------------------------
# 1. ลบแบบปลอดภัย คืนค่าโรงงาน (SAFE FACTORY RESET)
# -----------------------------------------------------------------------------
def safe_factory_reset_cloud(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """
    ล้างข้อมูลบน Google Firebase Realtime Database ให้เหมือนคืนค่าโรงงาน:
    - เคลียร์ยอดเงินและชื่อในทุก Sector, Sub-cell, และ Challengers ทั้งหมด
    - เคลียร์ Operatives ให้ยอดเงินเป็น 0 และมีสถานะ REMOVED
    - รีเซ็ต latest_telemetry เป็น Standby 0 ℳ
    - ล้าง war_logs ให้เหลือเฉพาะ log ระบบเริ่มต้น
    """
    base_url = firebase_url.rstrip("/")
    log_step("1/4", "กำลังสแกนและล้างข้อมูลบน Google Firebase (Cloud Reset)...")

    data = None
    try:
        data = get_cloud_state(firebase_url)
    except Exception as exc:
        log_warn(f"ไม่สามารถดึงข้อมูลปัจจุบันจาก Firebase: {exc}")

    if not isinstance(data, dict):
        log_ok("ฐานข้อมูลคลาวด์ว่างเปล่า (null) อยู่แล้ว — ไม่มีข้อมูลตกค้าง")
        return True

    # 1. เคลียร์ Sectors (ล้างทุกช่องย่อยและเงินของผู้ท้าชิงทุกคนในทุกพิกัด)
    sectors = data.get("sectors", {})
    if isinstance(sectors, dict) and sectors:
        log_ok(f"พบกระดาน Sectors {len(sectors)} พิกัด กำลังล้างยอดเงินทุกช่อง...")
        for coord_key in sectors:
            safe_coord = urllib.parse.quote(str(coord_key))
            sec_url = f"{base_url}/{BASE_PATH}/sectors/{safe_coord}.json"
            clean_sec_payload = {
                "client_version": CLIENT_VERSION
            }
            try:
                make_request(sec_url, method="PUT", data=clean_sec_payload)
            except Exception as e:
                log_warn(f"ไม่สามารถเคลียร์ Sector [{coord_key}]: {e}")
        log_ok(f"เคลียร์การยึดครองในทุกพิกัดเรียบร้อย (ล้างเงินทุกช่องเป็น 0)")
    else:
        log_ok("ไม่มี Sectors ตกค้างในฐานข้อมูล")

    # 2. เคลียร์ Operatives (ล้างชื่อและยอดเงินสะสมของนักรบทุกคน)
    operatives = data.get("operatives", {})
    if isinstance(operatives, dict) and operatives:
        log_ok(f"พบทะเบียน Operatives {len(operatives)} รายการ กำลังล้างข้อมูลนักรบ...")
        for char_name in operatives:
            safe_char = urllib.parse.quote(str(char_name))
            op_url = f"{base_url}/{BASE_PATH}/operatives/{safe_char}.json"
            clean_op_payload = {
                "character_name": str(char_name),
                "client_version": CLIENT_VERSION,
                "version": CLIENT_VERSION,
                "meseta": 0,
                "raw_meseta": 0,
                "status": "REMOVED",
                "security_status": "SECURE",
                "farming_rate_mhr": 0,
                "farmingRateMhr": 0,
                "meseta_per_hour": 0,
                "lastUpdated": int(time.time() * 1000)
            }
            try:
                make_request(op_url, method="PUT", data=clean_op_payload)
            except Exception as e:
                log_warn(f"ไม่สามารถเคลียร์ Operative '{char_name}': {e}")
        log_ok("ถอดถอนและล้างยอดเงิน Operatives ทั้งหมดเรียบร้อย (Status: REMOVED | 0 ℳ)")
    else:
        log_ok("ไม่มี Operatives ตกค้างในฐานข้อมูล")

    # 3. รีเซ็ต latest_telemetry เป็น Standby 0 ℳ
    setup_latest_telemetry(firebase_url)

    # 4. รีเซ็ต war_logs เป็น Log โรงงาน
    setup_initial_war_log(firebase_url, message="ระบบศูนย์บัญชาการ ARKS War Room ดำเนินการคืนค่าโรงงาน (Factory Reset) เรียบร้อย")

    return True


def safe_factory_reset_local() -> bool:
    """
    ล้างฐานข้อมูลและแคชในเครื่องทั้งหมด (Local Storage & Cache Reset)
    - data/live_war_telemetry.json ใน ARKS War Room
    - data/database_meseta_records.json ใน ARKS War Room
    - %APPDATA%/NekoTrackerOffline/war_stats.json
    - %APPDATA%/NekoTrackerOffline/database_meseta_records.json
    - %LOCALAPPDATA%/NEKO FAMILY/NekoTracker/*
    - รีเซ็ตพิกัดใน ngs_tracker_config.json กลับสู่ค่าเริ่มต้น "0, 0, 1"
    """
    log_step("2/4", "กำลังล้างฐานข้อมูลและแคชในเครื่อง (Local Cache Factory Reset)...")

    # 1. รีเซ็ตไฟล์ในโฟลเดอร์ data/ ของ War Room
    setup_local_workspace_data()

    # 2. ล้างแคช Neko Tracker ในเครื่อง
    app_data = os.path.expandvars(r"%APPDATA%")
    offline_dir = os.path.join(app_data, "NekoTrackerOffline")

    if os.path.exists(offline_dir):
        log_ok(f"พบโฟลเดอร์ NekoTrackerOffline ที่: {offline_dir}")
        for fname in ["war_stats.json", "database_meseta_records.json"]:
            fpath = os.path.join(offline_dir, fname)
            if os.path.exists(fpath):
                try:
                    os.remove(fpath)
                    log_ok(f"ลบไฟล์แคชเก่า: {fname}")
                except Exception as e:
                    log_warn(f"ไม่สามารถลบ {fname}: {e}")

        # ล้างไฟล์ .tmp และ .corrupt
        try:
            for item in os.listdir(offline_dir):
                if ".corrupt" in item or ".tmp" in item:
                    try:
                        os.remove(os.path.join(offline_dir, item))
                        log_ok(f"ลบไฟล์ตกค้าง: {item}")
                    except Exception:
                        pass
        except Exception:
            pass

        # รีเซ็ต config
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
                    log_ok("รีเซ็ตพิกัดใน ngs_tracker_config.json -> [0, 0, 1]")
            except Exception as e:
                log_warn(f"ไม่สามารถอัปเดต ngs_tracker_config.json: {e}")
    else:
        log_ok("ไม่พบโฟลเดอร์ NekoTrackerOffline (เครื่องสะอาด)")

    # 3. ล้าง LocalAppData ถ้ามี
    local_app_dir = os.path.expandvars(r"%LOCALAPPDATA%\NEKO FAMILY\NekoTracker")
    if os.path.exists(local_app_dir):
        for f in ["war_stats.json", "database_meseta_records.json"]:
            fp = os.path.join(local_app_dir, f)
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                    log_ok(f"ลบ {f} ใน LocalAppData")
                except Exception:
                    pass

    return True


# -----------------------------------------------------------------------------
# 2. สร้างโครงสร้างฐานข้อมูลเริ่มต้น (CREATE / SETUP / BOOTSTRAP)
# -----------------------------------------------------------------------------
def setup_version_control(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """
    ติดตั้งนโยบายควบคุมเวอร์ชัน (version_control) บน Firebase RTDB
    อนุญาตให้เขียนได้เมื่อ version_control ยังไม่เคยมีอยู่ (!data.exists() || auth != null)
    """
    log_step("3/4", "ตรวจสอบและติดตั้งนโยบายควบคุมเวอร์ชัน (version_control)...")
    base_url = firebase_url.rstrip("/")
    url = f"{base_url}/{BASE_PATH}/version_control.json"
    rev_dict = {r.replace(".", "_"): True for r in REVOKED_VERSIONS}
    payload = {
        "latest_version": CLIENT_VERSION,
        "min_secure_version": MIN_SECURE_VERSION,
        "revoked_versions": rev_dict,
        "announcement": "ARKS War Room — Database Operational & Ready",
        "download_url": "",
        "last_updated": int(time.time() * 1000),
    }

    try:
        make_request(url, method="PUT", data=payload)
        log_ok(f"ติดตั้ง version_control สำเร็จ (min_secure_version: {MIN_SECURE_VERSION})")
        return True
    except urllib.error.HTTPError as he:
        if he.code == 401:
            existing = None
            try:
                existing = make_request(url, method="GET")
            except Exception:
                pass
            if isinstance(existing, dict) and existing.get("min_secure_version"):
                log_ok(f"version_control พร้อมใช้งานอยู่แล้ว (min_secure: {existing.get('min_secure_version')})")
                return True
            else:
                log_warn("version_control ป้องกันการเขียนทับตาม Security Rules")
                return False
        else:
            log_err(f"HTTP Error {he.code} ขณะเขียน version_control: {he}")
            return False
    except Exception as exc:
        log_err(f"ไม่สามารถติดตั้ง version_control: {exc}")
        return False


def setup_latest_telemetry(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """
    ติดตั้งโหนด latest_telemetry ในสถานะพร้อมรบ (Standby 0 ℳ)
    """
    base_url = firebase_url.rstrip("/")
    url = f"{base_url}/{BASE_PATH}/latest_telemetry.json"
    now_ms = int(time.time() * 1000)
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")

    payload = {
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
        "target_coord": {"x": 0, "y": 0, "slot": 1},
        "lastUpdated": now_ms,
        "timestamp": now_ms,
        "updated_at": now_str,
    }

    try:
        make_request(url, method="PUT", data=payload)
        log_ok("ติดตั้ง latest_telemetry สำเร็จ (สถานะ Standby: [0, 0] #1 | 0 ℳ)")
        return True
    except Exception as exc:
        log_err(f"ไม่สามารถติดตั้ง latest_telemetry: {exc}")
        return False


def setup_initial_war_log(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL, message: Optional[str] = None) -> bool:
    """
    บันทึกข้อความเริ่มต้นระบบลงใน war_logs
    """
    base_url = firebase_url.rstrip("/")
    url = f"{base_url}/{BASE_PATH}/war_logs.json"
    now_ms = int(time.time() * 1000)
    now_time = time.strftime("%H:%M:%S")

    msg = message or "ระบบฐานข้อมูลศูนย์บัญชาการยุทธการ ARKS War Room ติดตั้งและเชื่อมต่อสมบูรณ์ (Setup Ready)"

    payload = {
        "client_version": CLIENT_VERSION,
        "init": {
            "timestamp": now_ms,
            "time": now_time,
            "day": 1,
            "type": "SYSTEM",
            "client_version": CLIENT_VERSION,
            "message": msg,
        }
    }

    try:
        make_request(url, method="PUT", data=payload)
        log_ok(f"บันทึกปูมยุทธการเริ่มต้นลง war_logs เรียบร้อย ({now_time})")
        return True
    except Exception as exc:
        log_warn(f"ไม่สามารถส่งข้อความ war_logs: {exc}")
        return False


def setup_local_workspace_data() -> bool:
    r"""
    รีเซ็ตไฟล์ข้อมูลแคชในโฟลเดอร์ data/ ของ ARKS War Room ให้พร้อมใช้งาน
    รองรับการรันจากทั้ง E:\Admin war control, E:\ARKS War Room และ E:\PSO2NGS-NEKO-Item-Meseta-tracker
    """
    now_ms = int(time.time() * 1000)
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    now_time = time.strftime("%H:%M:%S")

    clean_telemetry = {
        "version": CLIENT_VERSION,
        "client_version": CLIENT_VERSION,
        "security_status": "SECURE",
        "version_security_valid": True,
        "lastSync": now_str,
        "timestamp": now_ms,
        "lastUpdated": now_ms,
        "character_name": "None",
        "meseta": 0,
        "raw_meseta": 0,
        "sector_coord": {"x": 0, "y": 0, "slot": 1},
        "target_coord": {"x": 0, "y": 0, "slot": 1},
        "coord_key": "0,0",
        "slot": 1,
        "farmingRateMhr": 0,
        "farming_rate_mhr": 0,
        "meseta_per_hour": 0,
        "operative": {
            "name": "None",
            "character_name": "None",
            "client_version": CLIENT_VERSION,
            "security_status": "SECURE",
            "targetSector": {"x": 0, "y": 0, "slot": 1},
            "sectorCoord": {"x": 0, "y": 0, "slot": 1},
            "slot": 1,
            "sessionContribution": 0,
            "rawContribution": 0,
            "totalFarmed": 0,
            "farmingRateMhr": 0,
            "farming_rate_mhr": 0,
            "meseta_per_hour": 0,
        },
        "recentLogs": [
            {
                "time": now_time,
                "text": "ระบบฐานข้อมูลเริ่มต้นใหม่เรียบร้อย (Database Setup Baseline Ready)",
                "type": "info",
                "timestamp": now_ms / 1000.0,
            }
        ],
    }

    clean_record = {
        "character_name": "None",
        "meseta": 0,
        "raw_meseta": 0,
        "slot_meseta": 0,
        "raw_slot_meseta": 0,
        "sector_meseta": 0,
        "raw_sector_meseta": 0,
        "slot_farmed": {},
        "session_meseta": 0,
        "total_farmed": 0,
        "client_version": CLIENT_VERSION,
        "version": CLIENT_VERSION,
        "app_version": CLIENT_VERSION,
        "security_status": "SECURE",
        "version_security_valid": True,
        "sector_coord": {"x": 0, "y": 0, "slot": 1},
        "target_coord": {"x": 0, "y": 0, "slot": 1},
        "coord_key": "0,0",
        "slot": 1,
        "lastUpdated": now_ms,
        "farming_rate_mhr": 0,
        "farmingRateMhr": 0,
        "meseta_per_hour": 0,
        "updated_at": now_str,
        "timestamp": now_ms,
    }

    target_roots = [WORKSPACE_ROOT]
    # Dynamically locate sibling workspaces if present without hardcoding absolute paths
    parent_dir = os.path.dirname(WORKSPACE_ROOT)
    for sibling_name in ["ARKS War Room", "Admin war control"]:
        sibling_path = os.path.join(parent_dir, sibling_name)
        if os.path.exists(sibling_path):
            target_roots.append(sibling_path)

    # Optional environment variable for custom test/admin deployment paths
    env_roots = os.environ.get("WAR_ROOM_TARGET_ROOTS", "")
    if env_roots:
        for r in env_roots.split(";"):
            r = r.strip()
            if r and os.path.exists(r):
                target_roots.append(r)

    seen_dirs = set()
    for root in target_roots:
        if not os.path.exists(root):
            continue
        data_dir = os.path.join(root, "data")
        norm_dir = os.path.normpath(data_dir).lower()
        if norm_dir in seen_dirs:
            continue
        seen_dirs.add(norm_dir)

        # 1. live_war_telemetry.json
        t_file = os.path.join(data_dir, "live_war_telemetry.json")
        try:
            os.makedirs(data_dir, exist_ok=True)
            with open(t_file, "w", encoding="utf-8") as f:
                json.dump(clean_telemetry, f, indent=2, ensure_ascii=False)
            log_ok(f"รีเซ็ตแคชในเครื่อง: {t_file}")
        except Exception as exc:
            log_warn(f"ไม่สามารถเขียน {t_file}: {exc}")

        # 2. database_meseta_records.json
        r_file = os.path.join(data_dir, "database_meseta_records.json")
        try:
            with open(r_file, "w", encoding="utf-8") as f:
                json.dump(clean_record, f, indent=2, ensure_ascii=False)
            log_ok(f"รีเซ็ตแคชในเครื่อง: {r_file}")
        except Exception as exc:
            log_warn(f"ไม่สามารถเขียน {r_file}: {exc}")

    return True


# -----------------------------------------------------------------------------
# 3. VERIFICATION & HEALTH CHECK
# -----------------------------------------------------------------------------
def verify_database(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """
    ตรวจสอบความสมบูรณ์ของฐานข้อมูล
    """
    log_step("4/4", "กำลังตรวจสอบสถานะความพร้อมของฐานข้อมูล...")
    base_url = firebase_url.rstrip("/")
    try:
        data = get_cloud_state(firebase_url)
    except Exception as exc:
        log_err(f"ไม่สามารถเชื่อมต่อ Firebase เพื่อตรวจสอบ: {exc}")
        return False

    if not isinstance(data, dict):
        log_warn("ฐานข้อมูลยังคงเป็น null (ว่างเปล่า 100%) — สามารถสั่งรัน Setup ได้ทันที")
        return False

    vc = data.get("version_control")
    latest_tel = data.get("latest_telemetry")
    war_logs = data.get("war_logs")
    operatives = data.get("operatives", {})
    sectors = data.get("sectors", {})

    is_vc_valid = isinstance(vc, dict) and vc.get("min_secure_version") == MIN_SECURE_VERSION
    is_tel_valid = isinstance(latest_tel, dict) and latest_tel.get("meseta", -1) == 0

    # ตรวจสอบยอดเงินค้างใน Operatives
    active_ops_with_money = 0
    if isinstance(operatives, dict):
        for op_name, op_val in operatives.items():
            if isinstance(op_val, dict) and op_val.get("meseta", 0) > 0 and op_val.get("status") != "REMOVED":
                active_ops_with_money += 1

    # ตรวจสอบยอดเงินค้างใน Sectors
    active_sectors_with_money = 0
    if isinstance(sectors, dict):
        for sec_name, sec_val in sectors.items():
            if isinstance(sec_val, dict) and sec_val.get("challengers"):
                active_sectors_with_money += 1

    print("=" * 65)
    print("           สรุปสถานะฐานข้อมูล ARKS War Room (Firebase RTDB)")
    print("=" * 65)
    print(f" URL:              {base_url}/{BASE_PATH}.json")
    print(f" version_control:  {'[PASS] ปกติ' if is_vc_valid else '[WARN] ตรวจสอบนโยบาย'}")
    if isinstance(vc, dict):
        print(f"   - min_secure_version: {vc.get('min_secure_version')}")
        print(f"   - latest_version:     {vc.get('latest_version')}")
    print(f" latest_telemetry: {'[PASS] พร้อมรบ (0 ℳ Standby)' if is_tel_valid else '[WARN] ตรวจสอบยอด'}")
    if isinstance(latest_tel, dict):
        print(f"   - character_name:     {latest_tel.get('character_name')}")
        print(f"   - meseta:             {latest_tel.get('meseta'):,} ℳ")
        print(f"   - sector_coord:       {latest_tel.get('coord_key', '0,0')} #{latest_tel.get('slot', 1)}")
    print(f" Operatives:       {len(operatives) if isinstance(operatives, dict) else 0} รายการ (มียอดเงินค้าง: {active_ops_with_money})")
    print(f" Sectors:          {len(sectors) if isinstance(sectors, dict) else 0} พิกัด (มีผู้ยึดครองค้าง: {active_sectors_with_money})")
    print(f" war_logs:         {len(war_logs) if isinstance(war_logs, dict) else 0} รายการ")
    print("=" * 65)

    if is_vc_valid and is_tel_valid and active_ops_with_money == 0 and active_sectors_with_money == 0:
        print("\n [✓] ยืนยัน: ฐานข้อมูลสะอาดและติดตั้งสมบูรณ์ 100% พร้อมใช้งาน War Room และ Neko Tracker!\n")
        return True
    else:
        print("\n [!] สถานะ: มีข้อมูลบนฐานข้อมูล (หากต้องการคืนค่าโรงงานให้เลือกเมนู [1] หรือ [2])\n")
        return False


# -----------------------------------------------------------------------------
# 4. MASTER WORKFLOWS
# -----------------------------------------------------------------------------
def run_factory_reset_and_setup(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """Workflow 1: คืนค่าโรงงาน + ติดตั้งใหม่ทันที (All-in-One)"""
    log_header("เริ่มต้นกระบวนการ: คืนค่าโรงงาน + ติดตั้งฐานข้อมูลใหม่ (All-in-One)")
    safe_factory_reset_cloud(firebase_url)
    safe_factory_reset_local()
    setup_version_control(firebase_url)
    return verify_database(firebase_url)


def run_factory_reset_only(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """Workflow 2: คืนค่าโรงงานอย่างเดียว (Safe Wipe Only)"""
    log_header("เริ่มต้นกระบวนการ: ล้างข้อมูลปลอดภัย คืนค่าโรงงาน (Factory Reset Only)")
    safe_factory_reset_cloud(firebase_url)
    safe_factory_reset_local()
    return verify_database(firebase_url)


def run_setup_only(firebase_url: str = DEFAULT_FIREBASE_RTDB_URL) -> bool:
    """Workflow 3: ติดตั้งโครงสร้างอย่างเดียว (Setup / Bootstrap Only)"""
    log_header("เริ่มต้นกระบวนการ: ติดตั้งโครงสร้างฐานข้อมูลเริ่มต้น (Setup Only)")
    setup_version_control(firebase_url)
    setup_latest_telemetry(firebase_url)
    setup_initial_war_log(firebase_url)
    setup_local_workspace_data()
    return verify_database(firebase_url)


def main():
    parser = argparse.ArgumentParser(description="ARKS War Room All-in-One Admin Database Utility")
    parser.add_argument("--url", default=DEFAULT_FIREBASE_RTDB_URL, help="Firebase RTDB URL")
    parser.add_argument("--all", "-a", "--reset-all", action="store_true", help="คืนค่าโรงงาน + ติดตั้งใหม่ทันที")
    parser.add_argument("--wipe", "--factory-reset", action="store_true", help="ลบแบบปลอดภัย คืนค่าโรงงานอย่างเดียว")
    parser.add_argument("--setup", action="store_true", help="ติดตั้งโครงสร้างฐานข้อมูลอย่างเดียว")
    parser.add_argument("--verify", "-v", action="store_true", help="ตรวจสอบสถานะฐานข้อมูลเท่านั้น")
    parser.add_argument("--yes", "-y", action="store_true", help="รันโดยไม่ต้องถามยืนยัน")
    args = parser.parse_args()

    # CLI Flags execution
    if args.verify:
        verify_database(args.url)
        return
    if args.all or args.yes:
        run_factory_reset_and_setup(args.url)
        return
    if args.wipe:
        run_factory_reset_only(args.url)
        return
    if args.setup:
        run_setup_only(args.url)
        return

    # Interactive Menu
    print("=" * 67)
    print("   ARKS War Room — All-in-One Admin & Database Factory Reset")
    print("===================================================================")
    print(" [1] 🏭 คืนค่าโรงงาน + ติดตั้งใหม่ทันที (Factory Reset & Setup) [แนะนำ]")
    print("     -> ล้างชื่อตัวละคร, ลบเงินทุกช่อง, ล้างแคชในเครื่อง และสร้างโครงสร้างใหม่")
    print()
    print(" [2] 🧹 ลบแบบปลอดภัย คืนค่าโรงงานอย่างเดียว (Safe Factory Reset Only)")
    print("     -> เคลียร์ชื่อ, เงินในทุกพิกัด และแคชในเครื่องให้เกลี้ยง 100%")
    print()
    print(" [3] 🚀 ติดตั้งโครงสร้างฐานข้อมูลเริ่มต้น (Setup/Bootstrap Only)")
    print("     -> ติดตั้ง version_control และ telemetry (กรณีเพิ่งลบเป็น null)")
    print()
    print(" [4] 🔍 ตรวจสอบสถานะฐานข้อมูลสดบน Cloud (Verify Database Status)")
    print(" [0] ❌ ยกเลิก / ออก (Exit)")
    print("=" * 67)

    try:
        choice = input("กรุณาเลือกคำสั่ง [กด Enter เพื่อเลือก 1]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nยกเลิกการทำงาน")
        return

    if choice in ("", "1"):
        run_factory_reset_and_setup(args.url)
    elif choice == "2":
        run_factory_reset_only(args.url)
    elif choice == "3":
        run_setup_only(args.url)
    elif choice == "4":
        verify_database(args.url)
    elif choice == "0":
        print("ยกเลิกการทำงาน")
        return
    else:
        print(f"ตัวเลือก '{choice}' ไม่ถูกต้อง ทำการรันเมนู [1] อัตโนมัติ...")
        run_factory_reset_and_setup(args.url)

    try:
        input("\nกด Enter เพื่อปิดหน้าต่าง...")
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
