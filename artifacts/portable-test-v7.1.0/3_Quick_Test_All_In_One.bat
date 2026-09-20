@echo off
chcp 65001 > nul
title NEKO Tracker - Quick All-In-One Test
cd /d "%~dp0"
echo ======================================================================
echo  🌸 NEKO Tracker - Automated Live Test (App + Live Mock Stream)
echo ======================================================================
echo 1. Generating fresh sample log...
python "%~dp0tools\mock_log_simulator.py" --dir "%~dp0sample_logs" --static --events 5 > nul 2>&1
echo 2. Launching background live log streamer...
start "PSO2 Live Log Streamer" cmd /k "title PSO2 NGS Log Streamer && python "%~dp0tools\mock_log_simulator.py" --dir "%~dp0sample_logs" --stream --interval 2.5"
echo 3. Launching NEKO Tracker...
echo.
echo >> คำแนะนำ: ในหน้าต่าง NEKO Tracker ให้คลิกปุ่ม "เลือกโฟลเดอร์ Log"
echo    แล้วเลือกโฟลเดอร์: %~dp0sample_logs
echo    เพื่อดูตัวเลขเงินและไอเทมอัปเดตสดแบบ Real-time ทันที!
echo ======================================================================
start "" "%~dp0NekoTracker\NekoTracker.exe"
