@echo off
title Uninstall NEKO Item & Meseta Tracker
echo ==============================================================================
echo  NEKO Item ^& Meseta Tracker - Uninstall Launcher
echo ==============================================================================
echo.

set "APP_DIR=%~dp0"
set "UNINSTALLER=%APP_DIR%unins000.exe"

if exist "%UNINSTALLER%" (
    echo Launching uninstaller...
    start "" "%UNINSTALLER%"
) else (
    echo [ERROR] unins000.exe was not found in:
    echo "%APP_DIR%"
    echo.
    echo Please uninstall via Windows Settings ^> Apps ^> Installed apps.
    pause
)
