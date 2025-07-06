@echo off
chcp 65001 > nul
echo ==========================================
echo          语音转文字插件打包工具
echo ==========================================
echo.

echo 正在检查依赖包...
python -c "import PyQt5, speech_recognition, pyaudio" 2>nul
if %errorlevel% neq 0 (
    echo 错误：缺少必要的依赖包！
    echo 请先运行：pip install -r requirements.txt
    pause
    exit /b 1
)

echo 依赖包检查完成！
echo.

echo 正在打包应用程序...
echo 这可能需要几分钟时间，请耐心等待...
echo.

pyinstaller --onefile --windowed --name "语音转文字插件" --distpath dist --workpath build --specpath build main.py

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo              打包成功！
    echo ==========================================
    echo.
    echo 可执行文件位置：dist\语音转文字插件.exe
    echo.
    echo 您可以将该文件复制到任何 Windows 电脑上运行
    echo 无需安装 Python 环境
    echo.
) else (
    echo.
    echo ==========================================
    echo              打包失败！
    echo ==========================================
    echo.
    echo 请检查错误信息并重试
    echo.
)

pause 