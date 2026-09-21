@echo off
chcp 65001 > nul
title NEKO Item & Meseta Tracker - Test Mode
cd /d "%~dp0"

set "ROOT_DIR=%~dp0"
if exist "%~dp0..\NekoTracker.exe" set "ROOT_DIR=%~dp0..\"

echo ======================================================================
echo  🌸 NEKO Item & Meseta Tracker - Test Mode (V7.1.0)
echo ======================================================================
echo [INFO] Game process, file handle, and timestamp validations are bypassed.
echo [INFO] Safe to test with sample_logs or custom test data without PSO2 running.
echo ======================================================================
set NEKO_TEST_MODE=1
set NEKO_PROCESS_VALIDATION=0
set NEKO_FILE_HANDLE_VALIDATION=0
set NEKO_CANONICAL_PATH_GATING=0
set NEKO_CADENCE_VALIDATION=0
set NEKO_TIMESTAMP_VALIDATION=0
set NEKO_VELOCITY_VALIDATION=0

start "" "%ROOT_DIR%NekoTracker.exe" --test
