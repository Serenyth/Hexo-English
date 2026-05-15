@echo off
echo 正在启动博客管理系统...

REM 设置当前目录为脚本所在目录
cd /d "%~dp0"

REM 启动后端服务
start "Backend Server" cmd /k "cd /d "%~dp0backend" && python app.py"

REM 等待2秒确保后端启动
timeout /t 2 /nobreak >nul

REM 启动前端开发服务器
start "Frontend Dev Server" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo 服务已启动！
echo 后端API地址: http://localhost:8000
echo 前端地址将在新窗口中显示
echo.
echo 按任意键退出本窗口...
pause >nul