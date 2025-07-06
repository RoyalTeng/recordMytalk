@echo off
echo ===========================================
echo 语音识别网络错误修复工具
echo ===========================================
echo.

echo 正在检查网络连接...
ping -n 1 www.google.com >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] 网络连接正常
) else (
    echo [✗] 网络连接异常
    echo 建议检查网络设置
)

echo.
echo 正在检查DNS设置...
nslookup www.google.com >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] DNS解析正常
) else (
    echo [✗] DNS解析异常
    echo 建议更换DNS服务器
)

echo.
echo ===========================================
echo 选择修复方案:
echo ===========================================
echo 1. 更换DNS服务器为8.8.8.8和8.8.4.4
echo 2. 刷新DNS缓存
echo 3. 重置网络设置
echo 4. 安装离线语音识别依赖
echo 5. 使用本地语音识别版本
echo 6. 退出
echo.

set /p choice=请选择 (1-6): 

if "%choice%"=="1" goto change_dns
if "%choice%"=="2" goto flush_dns
if "%choice%"=="3" goto reset_network
if "%choice%"=="4" goto install_offline
if "%choice%"=="5" goto use_local
if "%choice%"=="6" goto exit

echo 无效选择，请重试
pause
goto start

:change_dns
echo.
echo 正在更换DNS服务器...
echo 需要管理员权限
netsh interface ip set dns "以太网" static 8.8.8.8
netsh interface ip add dns "以太网" 8.8.4.4 index=2
netsh interface ip set dns "Wi-Fi" static 8.8.8.8
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2
echo DNS服务器已更换为Google DNS
pause
goto start

:flush_dns
echo.
echo 正在刷新DNS缓存...
ipconfig /flushdns
echo DNS缓存已刷新
pause
goto start

:reset_network
echo.
echo 正在重置网络设置...
netsh winsock reset
netsh int ip reset
echo 网络设置已重置，建议重启计算机
pause
goto start

:install_offline
echo.
echo 正在安装离线语音识别依赖...
pip install pocketsphinx
echo 离线语音识别依赖安装完成
pause
goto start

:use_local
echo.
echo 正在切换到本地语音识别版本...
copy speech_recognizer.py speech_recognizer_backup.py
copy speech_recognizer_local.py speech_recognizer.py
echo 已切换到本地语音识别版本
echo 备份文件: speech_recognizer_backup.py
pause
goto start

:exit
echo.
echo 修复完成！
echo 建议重启应用程序
pause
exit 