@echo off
chcp 65001 > nul
cd /d "%~dp0"
call "artifacts\portable-test-v7.1.0\3_Quick_Test_All_In_One.bat"
