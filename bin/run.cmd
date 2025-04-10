@echo off
REM 设置控制台编码为 UTF-8
chcp 65001 >nul

REM 检查是否具有管理员权限
net session >nul 2>&1
if %errorlevel%==0 (
    REM 如果有管理员权限，则切换到脚本目录并运行 Python 脚本
    cd /d "%~dp0\.."
    python ./main.py
) else (
    echo 当前未以管理员权限运行
    echo.
    echo 请以管理员身份重新运行此脚本！
    echo.
    pause
    exit /b
)

REM 暂停以查看输出
pause