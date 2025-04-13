from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, BackgroundTasks, Body
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import json
import subprocess
import signal
import psutil
import aiofiles
from pathlib import Path
from pydantic import BaseModel

router = APIRouter()

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'blog_config.json')
BLOG_SERVER_PID_FILE = os.path.join(CONFIG_DIR, 'blog_server.pid')

# 确保配置目录存在
os.makedirs(CONFIG_DIR, exist_ok=True)

class DirectoryPath(BaseModel):
    directory_path: str

def save_config(directory: str):
    """保存博客目录配置到文件"""
    config = {'directory': directory}
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_config() -> Optional[str]:
    """从文件加载博客目录配置"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('directory')
    except Exception:
        return None
    return None

def save_server_pid(pid: int):
    """保存服务器进程ID到文件"""
    with open(BLOG_SERVER_PID_FILE, 'w') as f:
        f.write(str(pid))

def load_server_pid() -> Optional[int]:
    """从文件加载服务器进程ID"""
    try:
        if os.path.exists(BLOG_SERVER_PID_FILE):
            with open(BLOG_SERVER_PID_FILE, 'r') as f:
                return int(f.read().strip())
    except Exception:
        return None
    return None

def is_server_running() -> bool:
    """检查博客服务器是否正在运行"""
    pid = load_server_pid()
    if pid is None:
        return False
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.name() == 'node'
    except psutil.NoSuchProcess:
        return False

def kill_server():
    """终止博客服务器进程"""
    pid = load_server_pid()
    if pid is not None:
        try:
            os.kill(pid, signal.SIGTERM)
            os.remove(BLOG_SERVER_PID_FILE)
        except ProcessLookupError:
            if os.path.exists(BLOG_SERVER_PID_FILE):
                os.remove(BLOG_SERVER_PID_FILE)

@router.post("/select-directory")
async def select_directory(directory: DirectoryPath):
    """选择博客目录"""
    if not os.path.exists(directory.directory_path):
        raise HTTPException(status_code=404, detail="目录不存在")
    
    if not os.path.exists(os.path.join(directory.directory_path, '_config.yml')):
        raise HTTPException(status_code=400, detail="无效的Hexo博客目录")
    
    save_config(directory.directory_path)
    return {"message": "博客目录设置成功"}

@router.get("/current-directory")
async def get_current_directory():
    """获取当前博客目录"""
    directory = load_config()
    if directory is None:
        raise HTTPException(status_code=404, detail="未设置博客目录")
    return {"directory": directory}

@router.get("/server/status")
async def get_server_status():
    """获取服务器运行状态"""
    return {"running": is_server_running()}

@router.post("/server/start")
async def start_server():
    """启动博客服务器"""
    if is_server_running():
        raise HTTPException(status_code=400, detail="服务器已在运行")
    
    directory = load_config()
    if directory is None:
        raise HTTPException(status_code=404, detail="未设置博客目录")
    
    # 检查博客目录是否存在
    if not os.path.exists(directory):
        raise HTTPException(status_code=404, detail=f"博客目录不存在: {directory}")
    
    try:
        # 创建启动脚本
        script_content = f"""
@echo off
cd /d "{directory}"
echo 切换到博客目录: {directory}
echo 执行 hexo clean...
call hexo clean
echo 执行 hexo generate...
call hexo generate
echo 启动服务器...
call hexo server
pause
"""
        script_path = os.path.join(CONFIG_DIR, "start_server.bat")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # 在新的终端窗口中运行脚本
        process = subprocess.Popen(
            ["start", "cmd", "/k", script_path],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # 保存进程ID
        save_server_pid(process.pid)
        
        return {"message": "服务器启动成功"}
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/server/stop")
async def stop_server():
    """停止博客服务器"""
    if not is_server_running():
        raise HTTPException(status_code=400, detail="服务器未运行")
    
    try:
        kill_server()
        return {"message": "服务器已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止服务器失败: {str(e)}")

@router.post("/deploy")
async def deploy_blog():
    """部署博客到远程"""
    directory = load_config()
    if directory is None:
        raise HTTPException(status_code=404, detail="未设置博客目录")
    
    try:
        # 创建部署脚本
        script_content = f"""
@echo off
cd /d "{directory}"
echo 切换到博客目录: {directory}
echo 执行 hexo clean...
call hexo clean
echo 执行 hexo generate...
call hexo generate
echo 开始部署...
call hexo deploy
echo 部署完成！
pause
"""
        script_path = os.path.join(CONFIG_DIR, "deploy_blog.bat")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # 在新的终端窗口中运行脚本
        process = subprocess.Popen(
            ["start", "cmd", "/k", script_path],
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        return {"message": "正在部署博客，请查看新打开的窗口了解进度"}
    except Exception as e:
        error_msg = f"发生错误: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/structure")
async def get_blog_structure(request: Request = None):
    """
    获取博客目录结构
    """
    blog_path = getattr(request.app.state, 'blog_path', None) or load_config()
    if not blog_path:
        raise HTTPException(status_code=404, detail="尚未选择博客目录")
    
    # 获取博客目录结构
    structure = {
        "source": get_directory_structure(os.path.join(blog_path, "source")),
        "themes": get_directory_structure(os.path.join(blog_path, "themes")),
        "config": os.path.exists(os.path.join(blog_path, "_config.yml"))
    }
    
    return structure

def get_directory_structure(directory):
    """
    递归获取目录结构
    """
    if not os.path.exists(directory):
        return None
    
    result = {}
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            result[item] = get_directory_structure(item_path)
        else:
            result[item] = "file"
    
    return result

def save_blog_directory(directory_path: str):
    """保存博客目录路径到配置文件"""
    # 使用全局定义的CONFIG_DIR和CONFIG_FILE
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    config = {"directory": directory_path}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_blog_directory() -> Optional[str]:
    """从配置文件加载博客目录路径"""
    # 使用全局定义的CONFIG_FILE
    if not os.path.exists(CONFIG_FILE):
        return None
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        return config.get("directory")

def save_server_pid(pid: int):
    """保存服务器进程ID到配置文件"""
    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "server.json")
    
    config = {"pid": pid}
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_server_pid() -> Optional[int]:
    """从配置文件加载服务器进程ID"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "server.json")
    if not os.path.exists(config_path):
        return None
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        return config.get("pid")

@router.post("/select-directory")
async def select_directory(directory: DirectoryPath):
    """选择博客目录"""
    if not os.path.exists(directory.directory_path):
        raise HTTPException(status_code=404, detail="目录不存在")
    
    if not os.path.exists(os.path.join(directory.directory_path, '_config.yml')):
        raise HTTPException(status_code=400, detail="无效的Hexo博客目录")
    
    save_config(directory.directory_path)
    return {"message": "博客目录设置成功"}

@router.get("/current-directory")
async def get_current_directory():
    """获取当前博客目录"""
    directory = load_config()
    if directory is None:
        raise HTTPException(status_code=404, detail="未设置博客目录")
    return {"directory": directory}

@router.get("/server/status")
async def get_server_status():
    """获取服务器状态"""
    pid = load_server_pid()
    if not pid:
        return {"running": False}
    
    try:
        process = psutil.Process(pid)
        if process.is_running():
            return {"running": True}
        else:
            # 如果进程不存在，清除PID记录
            save_server_pid(0)
            return {"running": False}
    except psutil.NoSuchProcess:
        # 如果进程不存在，清除PID记录
        save_server_pid(0)
        return {"running": False}

@router.post("/server/start")
async def start_server():
    """启动博客服务器"""
    blog_path = load_config()
    if not blog_path:
        raise HTTPException(status_code=404, detail="请先选择博客目录")
    
    # 检查博客目录是否存在
    if not os.path.exists(blog_path):
        raise HTTPException(status_code=404, detail=f"博客目录不存在: {blog_path}")
    
    # 检查服务器是否已经在运行
    status = await get_server_status()
    if status["running"]:
        raise HTTPException(status_code=400, detail="服务器已经在运行")
    
    try:
        # 检查hexo命令是否可用
        try:
            # 使用where命令查找hexo可执行文件路径
            hexo_path = subprocess.check_output(["where", "hexo"], shell=True, text=True).strip()
            print(f"找到hexo命令: {hexo_path}")
        except subprocess.CalledProcessError:
            # hexo命令不在PATH中，尝试使用npm查找
            print("hexo命令不在PATH中，尝试使用npm查找")
            hexo_path = "npx hexo"
        
        # 切换到博客目录
        print(f"切换到博客目录: {blog_path}")
        os.chdir(blog_path)
        
        # 启动Hexo服务器
        print("启动Hexo服务器...")
        if hexo_path == "npx hexo":
            process = subprocess.Popen(
                ["npx", "hexo", "server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            process = subprocess.Popen(
                ["hexo", "server"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        
        # 保存进程ID
        save_server_pid(process.pid)
        
        return {"message": "服务器启动成功", "pid": process.pid}
    except Exception as e:
        error_msg = f"启动服务器失败: {str(e)}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/server/stop")
async def stop_server():
    """停止博客服务器"""
    pid = load_server_pid()
    if not pid:
        raise HTTPException(status_code=400, detail="服务器未运行")
    
    try:
        # 获取进程组
        process = psutil.Process(pid)
        process_group = process.group()
        
        # 终止进程组中的所有进程
        os.killpg(process_group, signal.SIGTERM)
        
        # 清除PID记录
        save_server_pid(0)
        
        return {"message": "服务器已停止"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"停止服务器失败: {str(e)}")

@router.post("/deploy")
async def deploy_blog():
    """部署博客"""
    blog_path = load_config()
    if not blog_path:
        raise HTTPException(status_code=404, detail="请先选择博客目录")
    
    try:
        # 切换到博客目录
        os.chdir(blog_path)
        
        # 执行部署命令
        process = subprocess.Popen(
            ["hexo", "deploy", "--generate"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # 等待部署完成
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"部署失败: {stderr.decode()}")
        
        return {"message": "博客部署成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"部署失败: {str(e)}")