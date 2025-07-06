@echo off
chcp 65001 > nul
echo ==========================================
echo        PyAudio 专用安装工具
echo ==========================================
echo.

echo 正在检查 Python 版本...
python --version

echo.
echo 正在尝试安装 PyAudio...
echo.

echo 方法1：使用 pipwin 安装预编译版本...
pip install pipwin
pipwin install pyaudio

echo.
echo 测试 PyAudio 是否安装成功...
python -c "import pyaudio; print('PyAudio 安装成功！')" 2>nul
if %errorlevel% equ 0 (
    echo ==========================================
    echo       PyAudio 安装成功！
    echo ==========================================
    echo.
    echo 现在可以运行 run.bat 启动程序了
    echo.
    pause
    exit /b 0
)

echo.
echo 方法1失败，尝试方法2：直接 pip 安装...
pip install pyaudio

echo.
echo 再次测试 PyAudio...
python -c "import pyaudio; print('PyAudio 安装成功！')" 2>nul
if %errorlevel% equ 0 (
    echo ==========================================
    echo       PyAudio 安装成功！
    echo ==========================================
    echo.
    echo 现在可以运行 run.bat 启动程序了
    echo.
    pause
    exit /b 0
)

echo.
echo ==========================================
echo     自动安装失败，请手动安装
echo ==========================================
echo.
echo 请选择以下方法之一：
echo.
echo 方法1：下载预编译文件（推荐）
echo   1. 访问：https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
echo   2. 根据你的 Python 版本下载对应的 .whl 文件
echo   3. 例如：PyAudio-0.2.11-cp39-cp39-win_amd64.whl
echo   4. 在下载目录打开命令提示符，运行：
echo      pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl
echo.
echo 方法2：使用 Anaconda（如果已安装）
echo   conda install pyaudio
echo.
echo 方法3：安装 Visual Studio 构建工具
echo   1. 下载 Visual Studio Build Tools
echo   2. 安装 C++ 构建工具
echo   3. 然后重新运行：pip install pyaudio
echo.

pause 