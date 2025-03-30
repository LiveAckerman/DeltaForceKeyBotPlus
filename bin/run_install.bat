@echo off
chcp 65001 >nul

cd /d "%~dp0"
cd ..
pip install -r requirement.txt
pause