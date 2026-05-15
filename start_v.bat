@echo off
:: 设置控制台编码为UTF-8
chcp 65001 >nul 2>&1

echo 正在启动博客管理系统...
echo ==============================================
echo 路径诊断信息:

:: 设置当前目录为脚本所在目录
cd /d "%~dp0"
echo 1. 脚本所在目录: "%cd%"

:: 定义后端目录路径
set "backend_dir=%~dp0backend"
echo 2. 后端目录路径: "%backend_dir%"

:: 检查后端目录是否存在
if exist "%backend_dir%" (
    echo    后端目录存在
) else (
    echo    错误: 后端目录不存在!
    pause
    exit /b 1
)

:: 定义虚拟环境路径
set "venv_dir=%backend_dir%\venv"
echo 3. 虚拟环境路径: "%venv_dir%"

:: 检查虚拟环境目录是否存在
if exist "%venv_dir%" (
    echo    虚拟环境目录存在
) else (
    echo    错误: 虚拟环境目录不存在!
    pause
    exit /b 1
)

:: 定义激活脚本路径
set "activate_script=%venv_dir%\Scripts\activate.bat"
echo 4. 激活脚本路径: "%activate_script%"

:: 检查激活脚本是否存在
if exist "%activate_script%" (
    echo    激活脚本存在
) else (
    echo    错误: 激活脚本不存在!
    pause
    exit /b 1
)

:: 定义app.py路径
set "app_py=%backend_dir%\app.py"
echo 5. app.py路径: "%app_py%"

:: 检查app.py是否存在
if exist "%app_py%" (
    echo    app.py存在
) else (
    echo    错误: app.py不存在!
    pause
    exit /b 1
)

echo ==============================================

:: 启动后端服务
start "Backend Server" cmd /k "cd /d %backend_dir% && call %activate_script% && python -m pip install python-multipart && python app.py && pause"

:: 等待2秒确保后端启动
timeout /t 2 /nobreak >nul

:: 启动前端开发服务器
start "Frontend Dev Server" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo 服务已启动！
echo 后端API地址: http://localhost:7888
echo 前端地址将在新窗口中显示
echo.
echo 按任意键退出本窗口...
pause >nul
