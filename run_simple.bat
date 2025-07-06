@echo off
echo ===================================
echo 启动极简语音转文字插件
echo ===================================
echo.

echo 正在启动...
python gui_with_engine_selector.py

if %errorlevel% neq 0 (
    echo.
    echo 启动失败！可能的原因：
    echo 1. Python环境未安装
    echo 2. 缺少依赖包
    echo 3. 请运行 install_pyaudio.bat 安装音频依赖
    echo.
    pause
) 