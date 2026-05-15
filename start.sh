#!/bin/bash

echo "正在启动博客管理系统服务..."

# 设置当前目录为脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

# 定义后端虚拟环境路径
VENV_PATH="$SCRIPT_DIR/backend/venv"

# 检查后端目录和关键文件
if [ ! -d "$SCRIPT_DIR/backend" ] || [ ! -f "$SCRIPT_DIR/backend/app.py" ]; then
    echo "错误：未找到后端目录或app.py文件"
    read -p "按任意键退出... " -n1 -s
    exit 1
fi

# 启动后端服务（增加tkinter检查）
echo "启动后端服务..."
gnome-terminal --title="Backend Server" -- bash -c "
    cd '$SCRIPT_DIR/backend';
    if [ -f '$VENV_PATH/bin/activate' ]; then
        echo '激活虚拟环境...';
        source '$VENV_PATH/bin/activate';
        
        # 检查tkinter是否安装
        if ! python -c 'import tkinter' &>/dev/null; then
            echo '错误：缺少tkinter模块！';
            echo '请先安装系统级tkinter包：';
            echo 'sudo apt update && sudo apt install -y python3-tk';
            echo '（注意：这是系统级包，不是通过pip安装）';
            read -p '按任意键关闭窗口...' -n1 -s;
            exit 1;
        fi;
        
        # 检查uvicorn是否安装
        if ! python -c 'import uvicorn' &>/dev/null; then
            echo '错误：缺少uvicorn依赖！';
            echo '请在虚拟环境中安装：pip install -r requirements.txt';
            read -p '按任意键关闭窗口...' -n1 -s;
            exit 1;
        fi;
    else
        echo '错误：未找到虚拟环境 $VENV_PATH';
        read -p '按任意键关闭窗口...' -n1 -s;
        exit 1;
    fi;
    
    echo '启动后端服务...';
    python app.py;
    exec bash;
" &

# 等待2秒确保后端启动
sleep 2

# 启动前端开发服务器
echo "启动前端服务..."
gnome-terminal --title="Frontend Dev Server" -- bash -c "
    cd '$SCRIPT_DIR/frontend';
    
    if [ ! -d 'node_modules' ]; then
        echo '错误：未找到前端依赖（node_modules）';
        echo '请先安装：npm install';
        read -p '按任意键关闭窗口...' -n1 -s;
        exit 1;
    fi;
    
    echo '启动前端开发服务器...';
    npm run dev;
    exec bash;
" &

echo "服务启动中...";
echo "后端API地址: http://localhost:8000";
echo "前端地址将在启动后显示在前端窗口";
echo;
echo "按任意键退出本窗口...";
read -n 1 -s
    
