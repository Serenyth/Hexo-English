#!/bin/bash

echo "正在启动博客管理系统..."

# 设置当前目录为脚本所在目录
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
cd "$SCRIPT_DIR"

# 定义后端虚拟环境路径
VENV_PATH="$SCRIPT_DIR/backend/venv"

# 安装后端依赖（使用虚拟环境）
echo "检查并安装后端依赖..."
if [ -d "$SCRIPT_DIR/backend" ] && [ -f "$SCRIPT_DIR/backend/requirements.txt" ]; then
    gnome-terminal --title="Backend Dependencies" -- bash -c "
        set -e  # 遇到错误立即退出
        echo '准备后端环境...';
        cd '$SCRIPT_DIR/backend';
        
        # 检查Python3是否安装
        if ! command -v python3 &>/dev/null; then
            echo '未找到Python3，正在安装...';
            sudo apt update;
            sudo apt install -y python3;
        fi
        
        # 检查并安装python3-venv
        if ! dpkg -s python3-venv &>/dev/null; then
            echo '安装python3-venv...';
            sudo apt update;
            sudo apt install -y python3-venv;
        fi
        
        # 彻底清理可能存在的损坏虚拟环境
        if [ -d "$VENV_PATH" ]; then
            echo '发现旧的虚拟环境，正在清理...';
            rm -rf "$VENV_PATH";
        fi
        
        # 创建虚拟环境（带详细输出）
        echo '创建虚拟环境...';
        if ! python3 -m venv "$VENV_PATH"; then
            echo '错误：虚拟环境创建失败！';
            echo '尝试安装python3-full解决依赖问题...';
            sudo apt install -y python3-full;
            # 再次尝试创建
            if ! python3 -m venv "$VENV_PATH"; then
                echo '严重错误：无法创建虚拟环境，请手动检查系统配置';
                read -p '按任意键关闭窗口...' -n1 -s;
                exit 1;
            fi
        fi
        
        # 验证虚拟环境是否创建成功
        if [ ! -f "$VENV_PATH/bin/activate" ]; then
            echo '错误：虚拟环境激活脚本不存在！';
            read -p '按任意键关闭窗口...' -n1 -s;
            exit 1;
        fi
        
        echo '激活虚拟环境并安装依赖...';
        source "$VENV_PATH/bin/activate";
        
        # 升级pip
        pip install --upgrade pip;
        
        # 安装依赖
        if ! pip install -r requirements.txt; then
            echo '依赖安装失败，尝试使用--break-system-packages（不推荐）...';
            pip install --break-system-packages -r requirements.txt;
        fi
        
        echo '后端依赖安装完成';
        read -p '按任意键关闭窗口...' -n1 -s;
    " &
    
    # 等待依赖安装完成
    echo "等待后端依赖安装..."
    sleep 15
else
    echo "警告：未找到后端目录或requirements.txt文件"
    read -p "按任意键继续...(可能导致服务启动失败) " -n1 -s
    echo
fi

# 安装前端依赖
echo "检查并安装前端依赖..."
if [ -d "$SCRIPT_DIR/frontend" ] && [ -f "$SCRIPT_DIR/frontend/package.json" ]; then
    gnome-terminal --title="Frontend Dependencies" -- bash -c "
        echo '安装前端依赖...';
        cd '$SCRIPT_DIR/frontend';
        if ! command -v npm &>/dev/null; then
            echo '未找到npm，尝试安装Node.js...';
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -;
            sudo apt install -y nodejs;
        fi;
        npm install;
        echo '前端依赖安装完成';
        read -p '按任意键关闭窗口...' -n1 -s;
    " &
    
    # 等待依赖安装完成
    echo "等待前端依赖安装..."
    sleep 15
else
    echo "警告：未找到前端目录或package.json文件"
    read -p "按任意键继续...(可能导致服务启动失败) " -n1 -s
    echo
fi

# 等待所有依赖安装完成
echo "等待所有依赖安装完成..."
sleep 30

# 启动后端服务（使用虚拟环境）
echo "启动后端服务..."
gnome-terminal --title="Backend Server" -- bash -c "
    cd '$SCRIPT_DIR/backend';
    if [ -f '$VENV_PATH/bin/activate' ]; then
        source '$VENV_PATH/bin/activate';
        python app.py;
    else
        echo '错误：虚拟环境不存在！';
        read -p '按任意键关闭窗口...' -n1 -s;
    fi;
    exec bash;
" &

# 等待2秒确保后端启动
sleep 2

# 启动前端开发服务器
echo "启动前端服务..."
gnome-terminal --title="Frontend Dev Server" -- bash -c "
    cd '$SCRIPT_DIR/frontend';
    npm run dev;
    exec bash;
" &

echo "服务已启动！"
echo "后端API地址: http://localhost:8000"
echo "前端地址将在新窗口中显示"
echo
echo "按任意键退出本窗口..."
read -n 1 -s
    
