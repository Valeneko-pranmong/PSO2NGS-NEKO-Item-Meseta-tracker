@echo off
chcp 65001 > nul
title PSO2 NGS ActionLog Mock Streamer
cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
if exist "%~dp0..\NekoTracker.exe" set "ROOT_DIR=%~dp0..\"

echo ======================================================================
echo  🎮 PSO2:NGS ActionLog Live Mock Streamer (V7.1.0)
echo ======================================================================
echo [INFO] Streaming live events into: "%ROOT_DIR%sample_logs"
echo [INFO] In NekoTracker, click "เลือกโฟลเดอร์ Log" and select:
echo        "%ROOT_DIR%sample_logs"
echo ======================================================================
if exist "%ROOT_DIR%tools\NekoLogSimulator.exe" (
    "%ROOT_DIR%tools\NekoLogSimulator.exe" --dir "%ROOT_DIR%sample_logs" --stream --interval 2.5
) else (
    python "%ROOT_DIR%tools\mock_log_simulator.py" --dir "%ROOT_DIR%sample_logs" --stream --interval 2.5
)
pause
