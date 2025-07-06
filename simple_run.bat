@echo off
chcp 65001 > nul
echo ==========================================
echo       语音转文字插件简化启动器
echo ==========================================
echo.

echo 正在检查 Python 环境...
python --version 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到 Python 环境！
    pause
    exit /b 1
)

echo.
echo 正在安装基础依赖包...
pip install PyQt5 SpeechRecognition

echo.
echo 正在启动程序...
echo 注意：如果出现 PyAudio 错误，请运行 install_pyaudio.bat
echo.

python main.py

echo.
echo 程序已退出
pause 