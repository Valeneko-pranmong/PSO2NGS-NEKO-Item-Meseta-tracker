@echo off
chcp 65001 > nul
title NEKO Item & Meseta Tracker - Portable Test Mode
cd /d "%~dp0"
echo ======================================================================
echo  🌸 NEKO Item & Meseta Tracker - Standalone Test Runner (V7.1.0)
echo ======================================================================
echo [INFO] Starting Primary Python Tracker (CustomTkinter + War Room)...
echo [INFO] Zero-Login: Operative identity will be detected from ActionLog.
echo [INFO] Standalone Test Mode: Local test environment active.
echo ======================================================================
set NEKO_PROCESS_VALIDATION=0
set NEKO_FILE_HANDLE_VALIDATION=0
set NEKO_CADENCE_VALIDATION=0
start "" "%~dp0NekoTracker\NekoTracker.exe"
