@echo off
chcp 65001 > nul
echo Starting NEKO Item & Meseta Tracker...
py meseta_tracker.py
if %ERRORLEVEL% NEQ 0 (
    python meseta_tracker.py
)
