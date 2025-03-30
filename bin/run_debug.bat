@echo off
chcp 65001 >nul

cd /d "%~dp0"
cd ..
python ./debug.py

pause