@echo off
chcp 65001
echo 正在打包语音转文字插件...
echo.

echo 检查依赖...
pip install pyinstaller
echo.

echo 开始打包...
pyinstaller --clean speech_app_final.spec
echo.

if exist "dist\语音转文字插件.exe" (
    echo 打包成功！
    echo exe文件位置：dist\语音转文字插件.exe
    echo.
    echo 正在启动文件浏览器...
    explorer dist
) else (
    echo 打包失败，请检查错误信息
)

pause 