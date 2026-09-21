@echo off
chcp 65001 > nul
echo ========================================================
echo  NEKO Item ^& Meseta Tracker - Automated Installer Build
echo ========================================================
python installer\build_installer.py %*
if %ERRORLEVEL% NEQ 0 (
    py -3.11 installer\build_installer.py %*
)
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build pipeline failed!
    exit /b %ERRORLEVEL%
)
echo [SUCCESS] Installer build finished.
