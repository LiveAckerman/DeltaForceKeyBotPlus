@echo off
REM 设置控制台编码为 UTF-8
chcp 65001 >nul

cd /d "%~dp0\.."
python main.py

pause