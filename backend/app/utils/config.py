import os
import json
import shutil
from pathlib import Path

# 应用数据目录
APP_NAME = "BlogManager"
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)
CONFIG_DIR = os.path.join(APP_DATA_DIR, "config")
TEMP_DIR = os.path.join(APP_DATA_DIR, "temp")
LOG_DIR = os.path.join(APP_DATA_DIR, "logs")

# 配置文件路径
BLOG_CONFIG_FILE = os.path.join(CONFIG_DIR, "blog_config.json")
DEPLOY_BAT_FILE = os.path.join(CONFIG_DIR, "deploy_blog.bat")
START_SERVER_BAT_FILE = os.path.join(CONFIG_DIR, "start_server.bat")

def init_app_dirs():
    """初始化应用目录结构"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

def copy_default_configs():
    """复制默认配置文件到应用数据目录"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        base_path = sys._MEIPASS
    else:
        # 开发环境路径
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    default_config_dir = os.path.join(base_path, "config")
    
    # 复制配置文件
    for file in ["blog_config.json", "deploy_blog.bat", "start_server.bat"]:
        src = os.path.join(default_config_dir, file)
        dst = os.path.join(CONFIG_DIR, file)
        if os.path.exists(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)

def get_config_path(filename):
    """获取配置文件路径"""
    return os.path.join(CONFIG_DIR, filename)

def load_blog_config():
    """加载博客配置"""
    try:
        if os.path.exists(BLOG_CONFIG_FILE):
            with open(BLOG_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {"directory": ""}

def save_blog_config(config):
    """保存博客配置"""
    with open(BLOG_CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)