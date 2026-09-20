@echo off
chcp 65001 > nul
title NEKO Item & Meseta Tracker - Portable Test Mode
cd /d "%~dp0"
echo ======================================================================
echo  🌸 NEKO Item & Meseta Tracker - Standalone Test Runner (V7.1.0)
echo ======================================================================
echo [INFO] Starting Primary Python Tracker (CustomTkinter + War Room)...
echo [INFO] Zero-Login: Operative identity will be detected from ActionLog.
echo ======================================================================
start "" "%~dp0NekoTracker\NekoTracker.exe"
