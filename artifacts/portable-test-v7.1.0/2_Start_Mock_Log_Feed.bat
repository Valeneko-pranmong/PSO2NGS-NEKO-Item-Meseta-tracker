@echo off
chcp 65001 > nul
title NEKO Tracker - PSO2 NGS ActionLog Mock Streamer
cd /d "%~dp0"
echo ======================================================================
echo  🎮 PSO2:NGS ActionLog Live Mock Streamer
echo ======================================================================
echo [INFO] Streaming live events into: sample_logs
echo [INFO] In NekoTracker, click "เลือกโฟลเดอร์ Log" and select:
echo        %~dp0sample_logs
echo ======================================================================
if exist "%~dp0tools\NekoLogSimulator.exe" (
    "%~dp0tools\NekoLogSimulator.exe" --dir "%~dp0sample_logs" --stream --interval 2.5
) else (
    python "%~dp0tools\mock_log_simulator.py" --dir "%~dp0sample_logs" --stream --interval 2.5
    if %ERRORLEVEL% NEQ 0 (
        py "%~dp0tools\mock_log_simulator.py" --dir "%~dp0sample_logs" --stream --interval 2.5
    )
)
pause
