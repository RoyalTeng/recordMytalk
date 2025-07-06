@echo off
chcp 65001 > nul
echo ==========================================
echo          语音转文字插件启动器
echo ==========================================
echo.

echo 正在检查 Python 环境...
python --version 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到 Python 环境！
    echo 请确保已安装 Python 3.7 或更高版本
    pause
    exit /b 1
)

echo 正在检查依赖包...
python -c "import PyQt5, speech_recognition" 2>nul
if %errorlevel% neq 0 (
    echo 正在安装基础依赖包...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 基础依赖包安装失败！
        pause
        exit /b 1
    )
)

echo 正在检查 PyAudio...
python -c "import pyaudio" 2>nul
if %errorlevel% neq 0 (
    echo PyAudio 未安装，正在尝试安装...
    echo.
    echo 方法1：使用 pipwin 安装预编译版本...
    pip install pipwin
    pipwin install pyaudio
    
    python -c "import pyaudio" 2>nul
    if %errorlevel% neq 0 (
        echo 方法1失败，尝试方法2：直接 pip 安装...
        pip install pyaudio
        
        python -c "import pyaudio" 2>nul
        if %errorlevel% neq 0 (
            echo.
            echo ==========================================
            echo          PyAudio 安装失败！
            echo ==========================================
            echo.
            echo 请手动安装 PyAudio：
            echo.
            echo 方法1：访问 https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
            echo        下载对应 Python 版本的 .whl 文件
            echo        然后运行：pip install 下载的文件名.whl
            echo.
            echo 方法2：使用 conda 安装：
            echo        conda install pyaudio
            echo.
            echo 方法3：安装 Microsoft Visual C++ 构建工具后重试
            echo.
            pause
            exit /b 1
        )
    )
)

echo 环境检查完成！
echo.
echo 正在启动语音转文字插件...
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)

echo.
echo 程序已退出
pause 