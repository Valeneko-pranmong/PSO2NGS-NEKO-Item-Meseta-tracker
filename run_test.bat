@echo off
chcp 65001 > nul
echo ========================================================
echo  NEKO Tracker - Running Modular Tests
echo ========================================================
py -m pytest -v
if %ERRORLEVEL% NEQ 0 (
    python -m pytest -v
)
pause
