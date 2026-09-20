#!/usr/bin/env python3
"""
NEKO Item & Meseta Tracker - Portable Test Package Builder
Packages standalone testing distribution before making the installer.
"""

import os
import sys
import shutil
import hashlib
import zipfile
import subprocess
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BUILD_DIR = os.path.join(ROOT_DIR, "build")
DIST_DIR = os.path.join(ROOT_DIR, "dist")
ARTIFACTS_DIR = os.path.join(ROOT_DIR, "artifacts")
PORTABLE_DIR = os.path.join(ARTIFACTS_DIR, "portable-test-v7.1.0")
ZIP_OUTPUT = os.path.join(ARTIFACTS_DIR, "NekoTracker-v7.1.0-Portable-Test.zip")

def log(msg: str) -> None:
    print(f"\n[TEST-PACKAGER] >>> {msg}", flush=True)

def compute_sha256(filepath: str) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()

def ensure_binaries(force_rebuild: bool = False) -> None:
    py_exe = os.path.join(DIST_DIR, "NekoTracker", "NekoTracker.exe")
    
    if force_rebuild or not os.path.isfile(py_exe):
        log("Compiling Python Tracker with PyInstaller...")
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--onedir", "--windowed",
            "--name", "NekoTracker",
            "--icon", "icon.ico",
            "--add-data", "logo.png;.",
            "--add-data", "icon.ico;.",
            "--add-data", "fonts;fonts",
            "--collect-all", "customtkinter",
            "--collect-all", "modules",
            "--hidden-import", "PIL",
            "--hidden-import", "PIL.Image",
            "--hidden-import", "modules.event_bus",
            "--hidden-import", "modules.i18n",
            "--hidden-import", "modules.guide_dialog",
            "--hidden-import", "modules.utils",
            "--hidden-import", "modules.security",
            "--hidden-import", "modules.anti_tamper",
            "--hidden-import", "modules.war_mode.war_service",
            "--hidden-import", "modules.war_mode.war_view",
            "--hidden-import", "tools.firebase_war_sync",
            "meseta_tracker.py"
        ], cwd=ROOT_DIR, check=True)

def build_portable_package() -> None:
    log("Assembling portable test package structure...")
    if os.path.exists(PORTABLE_DIR):
        shutil.rmtree(PORTABLE_DIR, ignore_errors=True)
    os.makedirs(PORTABLE_DIR, exist_ok=True)
    
    # 1. Copy Python Tracker Onedir
    log("Copying Python Tracker binary payload...")
    shutil.copytree(os.path.join(DIST_DIR, "NekoTracker"), os.path.join(PORTABLE_DIR, "NekoTracker"))
            
    # 2. Setup Tools and Simulator
    tools_dir = os.path.join(PORTABLE_DIR, "tools")
    os.makedirs(tools_dir, exist_ok=True)
    shutil.copy2(os.path.join(ROOT_DIR, "tools", "mock_log_simulator.py"), os.path.join(tools_dir, "mock_log_simulator.py"))
    
    # 4. Generate Sample Logs
    sample_logs_dir = os.path.join(PORTABLE_DIR, "sample_logs")
    os.makedirs(sample_logs_dir, exist_ok=True)
    subprocess.run([
        sys.executable,
        os.path.join(ROOT_DIR, "tools", "mock_log_simulator.py"),
        "--dir", sample_logs_dir,
        "--static",
        "--events", "20"
    ], check=True)
    
    how_to_use_src = os.path.join(ROOT_DIR, "Doc", "current", "HOW_TO_USE.md")
    if os.path.exists(how_to_use_src):
        shutil.copy2(how_to_use_src, os.path.join(PORTABLE_DIR, "HOW_TO_USE.md"))

    # 4. Create Batch Launchers
    log("Creating Windows test launcher scripts...")
    
    # 1_Run_NekoTracker_Test.bat
    with open(os.path.join(PORTABLE_DIR, "1_Run_NekoTracker_Test.bat"), "w", encoding="utf-8") as f:
        f.write("@echo off\r\n")
        f.write("chcp 65001 > nul\r\n")
        f.write("title NEKO Item & Meseta Tracker - Portable Test Mode\r\n")
        f.write("cd /d \"%~dp0\"\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("echo  🌸 NEKO Item & Meseta Tracker - Standalone Test Runner (V7.1.0)\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("echo [INFO] Starting Primary Python Tracker (CustomTkinter + War Room)...\r\n")
        f.write("echo [INFO] Zero-Login: Operative identity will be detected from ActionLog.\r\n")
        f.write("echo [INFO] Standalone Test Mode: Local test environment active.\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("set NEKO_PROCESS_VALIDATION=0\r\n")
        f.write("set NEKO_FILE_HANDLE_VALIDATION=0\r\n")
        f.write("set NEKO_CADENCE_VALIDATION=0\r\n")
        f.write("start \"\" \"%~dp0NekoTracker\\NekoTracker.exe\"\r\n")

    # 2_Start_Mock_Log_Feed.bat
    with open(os.path.join(PORTABLE_DIR, "2_Start_Mock_Log_Feed.bat"), "w", encoding="utf-8") as f:
        f.write("@echo off\r\n")
        f.write("chcp 65001 > nul\r\n")
        f.write("title NEKO Tracker - PSO2 NGS ActionLog Mock Streamer\r\n")
        f.write("cd /d \"%~dp0\"\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("echo  🎮 PSO2:NGS ActionLog Live Mock Streamer\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("echo [INFO] Streaming live events into: sample_logs\r\n")
        f.write("echo [INFO] In NekoTracker, click \"เลือกโฟลเดอร์ Log\" and select:\r\n")
        f.write("echo        %~dp0sample_logs\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("python \"%~dp0tools\\mock_log_simulator.py\" --dir \"%~dp0sample_logs\" --stream --interval 2.5\r\n")
        f.write("if %ERRORLEVEL% NEQ 0 (\r\n")
        f.write("    py \"%~dp0tools\\mock_log_simulator.py\" --dir \"%~dp0sample_logs\" --stream --interval 2.5\r\n")
        f.write(")\r\n")
        f.write("pause\r\n")

    # 3_Quick_Test_All_In_One.bat
    with open(os.path.join(PORTABLE_DIR, "3_Quick_Test_All_In_One.bat"), "w", encoding="utf-8") as f:
        f.write("@echo off\r\n")
        f.write("chcp 65001 > nul\r\n")
        f.write("title NEKO Tracker - Quick All-In-One Test\r\n")
        f.write("cd /d \"%~dp0\"\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("echo  🌸 NEKO Tracker - Automated Live Test (App + Live Mock Stream)\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("echo 1. Generating fresh sample log...\r\n")
        f.write("python \"%~dp0tools\\mock_log_simulator.py\" --dir \"%~dp0sample_logs\" --static --events 5 > nul 2>&1\r\n")
        f.write("echo 2. Launching background live log streamer...\r\n")
        f.write("start \"PSO2 Live Log Streamer\" cmd /k \"title PSO2 NGS Log Streamer && python \"%~dp0tools\\mock_log_simulator.py\" --dir \"%~dp0sample_logs\" --stream --interval 2.5\"\r\n")
        f.write("echo 3. Launching NEKO Tracker...\r\n")
        f.write("echo.\r\n")
        f.write("echo >> คำแนะนำ: ในหน้าต่าง NEKO Tracker ให้คลิกปุ่ม \"เลือกโฟลเดอร์ Log\"\r\n")
        f.write("echo    แล้วเลือกโฟลเดอร์: %~dp0sample_logs\r\n")
        f.write("echo    เพื่อดูตัวเลขเงินและไอเทมอัปเดตสดแบบ Real-time ทันที!\r\n")
        f.write("echo ======================================================================\r\n")
        f.write("set NEKO_PROCESS_VALIDATION=0\r\n")
        f.write("set NEKO_FILE_HANDLE_VALIDATION=0\r\n")
        f.write("set NEKO_CADENCE_VALIDATION=0\r\n")
        f.write("start \"\" \"%~dp0NekoTracker\\NekoTracker.exe\"\r\n")

    # 5. Documentation
    guide_th = """==============================================================================
🌸 NEKO Item & Meseta Tracker (V7.1.0) — คู่มือชุดทดสอบก่อนติดตั้ง (Portable Test)
==============================================================================

ชุดไฟล์นี้ถูกสร้างขึ้นสำหรับทดสอบการทำงานของ NEKO Item & Meseta Tracker
ก่อนทำการคอมไพล์หรือรัน Inno Setup Installer เพื่อให้คุณสามารถตรวจสอบฟังก์ชันทุกอย่าง
ได้แบบ Standalone โดยไม่ต้องติดตั้งลงเครื่อง (%LOCALAPPDATA%) และไม่ต้องใช้สิทธิ์ Admin

------------------------------------------------------------------------------
📂 โครงสร้างไฟล์ในชุดทดสอบ:
------------------------------------------------------------------------------
1_Run_NekoTracker_Test.bat     -> รันตัวโปรแกรมหลัก Python Tracker V7.1.0 (พร้อมโหมด ARKS War Room & Cloud Sync)
2_Start_Mock_Log_Feed.bat     -> รันโปรแกรมจำลองเหตุการณ์ Log สด (Streaming PSE Burst & Drops)
3_Quick_Test_All_In_One.bat   -> รันทั้งตัวจำลอง Log และโปรแกรม Tracker พร้อมกันทันที
NekoTracker/                  -> โฟลเดอร์ไบนารีหลักแบบไม่ต้องติดตั้ง (PyInstaller Onedir)
sample_logs/                  -> โฟลเดอร์ Log ตัวอย่างสำหรับทดสอบการอ่านไฟล์
tools/mock_log_simulator.py   -> สคริปต์จำลอง ActionLog สำหรับทดสอบ

------------------------------------------------------------------------------
🧪 วิธีการทดสอบแบบเร็วที่สุด (All-in-One Quick Test):
------------------------------------------------------------------------------
1. ดับเบิ้ลคลิกที่ไฟล์: "3_Quick_Test_All_In_One.bat"
2. หน้าต่าง Command Prompt "PSO2 Live Log Streamer" จะเปิดขึ้นมาและเริ่มยิงข้อมูลดรอปเงิน/ไอเทมสดทุก 2.5 วินาที
3. หน้าต่าง "NEKO Item & Meseta Tracker" จะเปิดขึ้นมา
4. ที่หน้าต่าง Tracker ให้คลิกปุ่ม "เลือกโฟลเดอร์ Log" แล้วเลือกโฟลเดอร์:
   "sample_logs" ที่อยู่ในโฟลเดอร์นี้
5. สังเกตผลลัพธ์:
   - Zero-Login Detection: ระบบจะตรวจพบชื่อตัวละคร "Vale3neko" อัตโนมัติ (ไม่ถามรหัสผ่าน)
   - Meseta Tracker: ตัวเลขเงิน Meseta รวมในเซสชัน และอัตรา M/hr จะเริ่มวิ่งนับขึ้น
   - Items Tracker: ไอเทมหายาก เช่น C/Astraea II, Arms Refiner II จะปรากฏในรายการดรอป
   - Gadget Mode (Overlay): กดปุ่ม "โหมด Gadget (Overlay)" เพื่อทดสอบหน้าต่างลอยทับหน้าจอเกม
   - ARKS War Room: กดปุ่ม "โหมด ARKS War Room" เพื่อทดสอบการป้อนพิกัด เช่น "15, -6, 2"
     และการส่ง Telemetry ปลอดภัยด้วย Client Version 7.1.0

------------------------------------------------------------------------------
🔒 มาตรฐานความปลอดภัย:
------------------------------------------------------------------------------
- 100% TOS Safe: อ่านเฉพาะไฟล์ข้อความ ActionLog เท่านั้น ไม่แตะต้อง Process หรือ RAM ของเกม
- Zero-Login: ไม่มีการขอหรือจัดเก็บ Username / Password ใดๆ ทั้งสิ้น
- Client Version Security: บังคับใช้ Version 7.1.0 (บล็อกเวอร์ชันไม่ปลอดภัย 7.0.0-alpha)

------------------------------------------------------------------------------
🌸 ชุมชน Discord & เครดิตทางการ:
------------------------------------------------------------------------------
NEKO★FAMILY PSO2:NGS Community discord.gg/fkjXW9AJ6a
Discord: https://discord.gg/fkjXW9AJ6a
"""
    with open(os.path.join(PORTABLE_DIR, "คู่มือการทดสอบ_README.txt"), "w", encoding="utf-8") as f:
        f.write(guide_th)

    readme_md = f"""# 🌸 NEKO Item & Meseta Tracker — Portable Test Package (V7.1.0)

> **สถานะ:** `[PORTABLE TEST ARTIFACT]` 🟢  
> **รุ่น:** `7.1.0` (Pure Python Modular Architecture)  
> **วัตถุประสงค์:** ชุดทดสอบการทำงานแบบ Standalone ก่อนสร้างและติดตั้งผ่าน Installer  

---

## 🚀 ไฟล์เรียกใช้งานหลัก (Launchers)

| ไฟล์ Script | หน้าที่ |
| :--- | :--- |
| **`1_Run_NekoTracker_Test.bat`** | เปิดตัวโปรแกรมหลัก Python Tracker V7.1.0 (พร้อมโหมด ARKS War Room & Cloud Sync) |
| **`2_Start_Mock_Log_Feed.bat`** | เริ่มสตรีม ActionLog จำลองสด (Drop เงิน, ไอเทม, PSE Burst) ลงโฟลเดอร์ `sample_logs/` |
| **`3_Quick_Test_All_In_One.bat`** | รันตัวจำลอง Log พร้อมเปิด NekoTracker ให้อัตโนมัติในคลิกเดียว |

---

## 🧪 ขั้นตอนการทดสอบ (Testing Workflow)

1. ดับเบิ้ลคลิก `3_Quick_Test_All_In_One.bat`
2. บนหน้าต่าง Tracker คลิกปุ่ม **"เลือกโฟลเดอร์ Log"** แล้วเลือกพาธ `sample_logs`
3. ตรวจสอบการทำงาน:
   - **Zero-Login Detection:** พบชื่อตัวละคร `Vale3neko` จากไฟล์ Log ทันที
   - **Meseta Counter & M/hr:** ยอดเงินวิ่งนับสดตามจังหวะ PSE Burst
   - **Item Drop Watchlist:** แคปซูลและวัตถุดิบปรากฏในรายการ
   - **Overlay Window:** หน้าต่าง Overlay ลอยทับหน้าจอแสดงผลถูกต้อง
   - **ARKS War Room:** สลับหน้าจอ War Room, ระบุพิกัด `15, -6, 2` ส่ง Telemetry ด้วย Version `7.1.0`
"""
    with open(os.path.join(PORTABLE_DIR, "README_TEST_GUIDE.md"), "w", encoding="utf-8") as f:
        f.write(readme_md)

    # 6. Generate Checksums for portable files
    log("Computing SHA-256 checksums...")
    sums = []
    py_target_exe = os.path.join(PORTABLE_DIR, "NekoTracker", "NekoTracker.exe")
    
    if os.path.isfile(py_target_exe):
        sums.append(f"{compute_sha256(py_target_exe)}  NekoTracker/NekoTracker.exe")
        
    with open(os.path.join(PORTABLE_DIR, "SHA256SUMS.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sums) + "\n")

    # 7. Create ZIP archive
    log(f"Creating portable zip archive: {ZIP_OUTPUT} ...")
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PORTABLE_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, os.path.dirname(PORTABLE_DIR))
                zf.write(abs_path, rel_path)

    zip_size_mb = os.path.getsize(ZIP_OUTPUT) / (1024 * 1024)
    zip_sha = compute_sha256(ZIP_OUTPUT)
    
    # Save root test runner for project repository
    root_launcher = os.path.join(ROOT_DIR, "run_portable_test.bat")
    with open(root_launcher, "w", encoding="utf-8") as f:
        f.write("@echo off\r\n")
        f.write("chcp 65001 > nul\r\n")
        f.write("cd /d \"%~dp0\"\r\n")
        f.write("call \"artifacts\\portable-test-v7.1.0\\3_Quick_Test_All_In_One.bat\"\r\n")
        
    print("\n" + "="*70)
    print(" 🌸 NEKO TRACKER - PORTABLE TEST PACKAGE READY")
    print("="*70)
    print(f" Directory:   {PORTABLE_DIR}")
    print(f" Zip Archive: {ZIP_OUTPUT}")
    print(f" Zip Size:    {zip_size_mb:.2f} MB")
    print(f" SHA-256:     {zip_sha}")
    print(f" Quick Start: run_portable_test.bat")
    print("="*70 + "\n")

if __name__ == "__main__":
    force = "--rebuild" in sys.argv or "--force" in sys.argv
    ensure_binaries(force_rebuild=force)
    build_portable_package()
