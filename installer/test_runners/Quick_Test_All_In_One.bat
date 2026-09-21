@echo off
chcp 65001 > nul
title NEKO Tracker - Quick All-In-One Test
cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
if exist "%~dp0..\NekoTracker.exe" set "ROOT_DIR=%~dp0..\"

echo ======================================================================
echo  🌸 NEKO Item & Meseta Tracker - Automated Live Test Runner (V7.1.0)
echo ======================================================================
echo [1/3] Preparing fresh sample data...
if exist "%ROOT_DIR%tools\NekoLogSimulator.exe" (
    "%ROOT_DIR%tools\NekoLogSimulator.exe" --dir "%ROOT_DIR%sample_logs" --static --events 10 > nul 2>&1
    echo [2/3] Launching background live log streamer...
    start "PSO2 NGS Live Streamer" cmd /k "title PSO2 NGS Live Streamer && \"%ROOT_DIR%tools\NekoLogSimulator.exe\" --dir \"%ROOT_DIR%sample_logs\" --stream --interval 2.5"
) else (
    python "%ROOT_DIR%tools\mock_log_simulator.py" --dir "%ROOT_DIR%sample_logs" --static --events 10 > nul 2>&1
    echo [2/3] Launching background live log streamer...
    start "PSO2 NGS Live Streamer" cmd /k "title PSO2 NGS Live Streamer && python \"%ROOT_DIR%tools\mock_log_simulator.py\" --dir \"%ROOT_DIR%sample_logs\" --stream --interval 2.5"
)

echo [3/3] Setting test mode environment (offline/mock bypass)...
set NEKO_TEST_MODE=1
set NEKO_PROCESS_VALIDATION=0
set NEKO_FILE_HANDLE_VALIDATION=0
set NEKO_CANONICAL_PATH_GATING=0
set NEKO_CADENCE_VALIDATION=0
set NEKO_TIMESTAMP_VALIDATION=0
set NEKO_VELOCITY_VALIDATION=0

echo Launching NEKO Tracker in Test Mode...
echo.
echo ======================================================================
echo  >> คำแนะนำสำหรับผู้ทดสอบ (Tester Instructions):
echo     1. ในหน้าต่างโปรแกรม ให้คลิกปุ่ม "เลือกโฟลเดอร์ Log"
echo     2. เลือกโฟลเดอร์: "%ROOT_DIR%sample_logs"
echo     3. ตัวเลข N-Meseta, M/hr และรายการไอเทมจะวิ่งขึ้นสดทันที!
echo     4. เข้า ARKS War Room เพื่อทดสอบการส่งยอด Meseta ขึ้นเซิร์ฟเวอร์
echo ======================================================================
start "" "%ROOT_DIR%NekoTracker.exe" --test
