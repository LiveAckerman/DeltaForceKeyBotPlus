@echo off
chcp 65001 >nul
net session >nul 2>&1

if %errorlevel%==0 (
    REM 如果有管理员权限，切换到脚本所在目录并运行 Python 脚本
    cd /d "%~dp0"
    cd ..
    python ./main.py
) else (
    echo 请以管理员身份运行此脚本！
    echo.
    echo 例如：右键点击此脚本，选择“以管理员身份运行”。
    echo.
    pause
    exit /b
)

REM 运行完毕后暂停，等待用户按任意键继续
pause