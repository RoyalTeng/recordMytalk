@echo off
echo =================================
echo  正在启动现代化语音助手...
echo =================================

REM 检查是否已安装依赖
pip freeze | find "PyQt5" > nul
if errorlevel 1 (
    echo.
    echo [!] 正在安装所需的依赖库...
    pip install -r requirements.txt
)

echo.
echo [+] 依赖检查完成，正在运行主程序...
python main_ui.py

echo.
echo 程序已退出。
pause 