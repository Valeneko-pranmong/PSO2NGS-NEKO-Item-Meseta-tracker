@echo off
chcp 65001 > nul
title ARKS War Room - Database Setup Utility
cd /d "%~dp0"

set "PY_CMD="
py -3 --version > nul 2>&1 && set "PY_CMD=py -3"
if "%PY_CMD%"=="" py --version > nul 2>&1 && set "PY_CMD=py"
if "%PY_CMD%"=="" python --version > nul 2>&1 && set "PY_CMD=python"
if "%PY_CMD%"=="" python3 --version > nul 2>&1 && set "PY_CMD=python3"

if "%PY_CMD%"=="" (
    echo [ERROR] Python not found in system. Please install Python 3.8+
    pause
    exit /b 1
)

%PY_CMD% tools\setup_database.py %*

echo.
pause
