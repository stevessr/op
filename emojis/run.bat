@echo off
chcp 65001 >nul
echo 图片智能重命名工具
echo ==================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo 🔍 检查依赖包...
pip show google-generativeai >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
)

echo ✅ 依赖检查完成
echo.

REM 运行脚本
echo 🚀 启动图片重命名工具...
python simple_rename.py

echo.
echo 按任意键退出...
pause >nul
