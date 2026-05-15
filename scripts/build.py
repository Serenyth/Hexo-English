import os
import sys
import shutil
import PyInstaller.__main__
from shutil import copytree, copy2
import subprocess
import argparse
import datetime
import platform

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def log(message, level="INFO"):
    """打印带时间戳和级别的日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def get_hidden_imports():
    """从 requirements.txt 中提取模块名称"""
    hidden_imports = []
    requirements_path = os.path.join(ROOT_DIR, 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        log(f"警告: requirements.txt 文件不存在: {requirements_path}", "WARNING")
        return hidden_imports
        
    log(f"正在读取依赖: {requirements_path}")
    with open(requirements_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 提取模块名（去除版本号）
            module = line.split('==')[0].split('>=')[0].strip()
            if not module:
                continue
                
            hidden_imports.append(f'--hidden-import={module}')
            # 为某些特殊模块添加子模块
            if module == 'keyboard':
                hidden_imports.extend([
                    '--hidden-import=keyboard._win32',
                    '--hidden-import=keyboard._winkeyboard',
                    '--hidden-import=cpuinfo'
                ])
            elif module == 'pystray':
                hidden_imports.append('--hidden-import=pystray._win32')
            elif module == 'fastapi':
                hidden_imports.extend([
                    '--hidden-import=fastapi.applications',
                    '--hidden-import=fastapi.responses',
                    '--hidden-import=fastapi.routing'
                ])
            elif module == 'uvicorn':
                hidden_imports.extend([
                    '--hidden-import=uvicorn.logging',
                    '--hidden-import=uvicorn.protocols',
                    '--hidden-import=uvicorn.lifespan',
                    '--hidden-import=uvicorn.lifespan.on',
                    '--hidden-import=uvicorn.lifespan.off',
                    '--hidden-import=uvicorn.protocols.http',
                    '--hidden-import=uvicorn.protocols.http.auto',
                    '--hidden-import=uvicorn.protocols.http.h11_impl',
                    '--hidden-import=uvicorn.protocols.http.httptools_impl',
                    '--hidden-import=uvicorn.protocols.websockets',
                    '--hidden-import=uvicorn.protocols.websockets.auto',
                    '--hidden-import=uvicorn.protocols.websockets.websockets_impl',
                    '--hidden-import=uvicorn.protocols.websockets.wsproto_impl',
                    '--hidden-import=uvicorn.supervisors',
                ])
            elif module == 'logging':
                hidden_imports.extend([
                    '--hidden-import=logging.config',
                    '--hidden-import=logging.handlers',
                ])
                
            # 添加额外的日志模块
            hidden_imports.extend([
                '--hidden-import=logging',
                '--hidden-import=logging.config',
                '--hidden-import=logging.handlers',
            ])

    log(f"发现 {len(hidden_imports)} 个隐式导入模块")
    return hidden_imports

def build_frontend(args):
    """构建前端应用"""
    frontend_path = os.path.join(ROOT_DIR, 'frontend')
    
    if not os.path.exists(frontend_path):
        log(f"错误: 前端目录不存在: {frontend_path}", "ERROR")
        return False
        
    log(f"前端目录: {frontend_path}")
    
    # 如果跳过前端构建
    if args.skip_frontend:
        log("跳过前端构建")
        return True
        
    # 检查是否有package.json
    if not os.path.exists(os.path.join(frontend_path, 'package.json')):
        log("错误: 前端目录中没有找到 package.json", "ERROR")
        return False
    
    try:
        # 安装依赖
        if not args.skip_npm_install:
            log("正在安装前端依赖...")
            subprocess.check_call('npm install', cwd=frontend_path, shell=True)
        
        # 构建生产版本
        log("正在构建前端...")
        build_cmd = 'npm run build'
        subprocess.check_call(build_cmd, cwd=frontend_path, shell=True)
        
        # 检查dist目录是否创建成功
        dist_path = os.path.join(frontend_path, 'dist')
        if not os.path.exists(dist_path):
            log(f"错误: 前端构建后没有生成dist目录: {dist_path}", "ERROR")
            return False
            
        log("前端构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        log(f"前端构建失败: {e}", "ERROR")
        return False

def build_backend(args):
    """使用PyInstaller打包后端应用"""
    # 确定入口文件
    entry_file = args.entry or 'backend/app.py'
    entry_path = os.path.join(ROOT_DIR, entry_file)
    
    if not os.path.exists(entry_path):
        log(f"错误: 入口文件不存在: {entry_path}", "ERROR")
        return False
    
    # 确定输出名称
    output_name = args.name or 'BLOG管理系统'
    
    # 设置图标
    icon_file = args.icon or 'backend/icon/favicon.ico'
    icon_path = os.path.join(ROOT_DIR, icon_file)
    
    if not os.path.exists(icon_path):
        log(f"警告: 图标文件不存在: {icon_path}", "WARNING")
        icon_arg = []
    else:
        icon_arg = [f'--icon={icon_path}']
    
    # 获取前端dist目录的绝对路径
    frontend_dist = os.path.join(ROOT_DIR, 'frontend', 'dist')
    backend_icon = os.path.join(ROOT_DIR, 'backend', 'icon')
    backend_api = os.path.join(ROOT_DIR, 'backend', 'app', 'api')
    
    # 检查前端dist目录是否存在
    if not os.path.exists(frontend_dist):
        log(f"错误: 前端构建目录不存在: {frontend_dist}", "ERROR")
        if not args.skip_frontend:
            log("前端可能没有成功构建，请检查npm run build是否成功执行", "ERROR")
        return False
    
    # 使用绝对路径来指定数据文件
    dist_separator = ';' if platform.system() == 'Windows' else ':'
    
    # 基本配置
    pyinstaller_args = [
        entry_path,
        '--onefile' if args.onefile else '--onedir',
        '--noconsole' if not args.console else '',
        f'--name={output_name}',
    ] + icon_arg + [
        f'--add-data={frontend_dist}{os.path.sep}*{dist_separator}frontend/dist',
    ]
    
    # 添加其他数据文件，如果目录存在
    if os.path.exists(backend_icon):
        pyinstaller_args.append(f'--add-data={backend_icon}{os.path.sep}*{dist_separator}backend/icon')
    
    if os.path.exists(backend_api):
        pyinstaller_args.append(f'--add-data={backend_api}{dist_separator}api')
    
    if os.path.exists(os.path.join(frontend_dist, 'assets')):
        pyinstaller_args.append(f'--add-data={os.path.join(frontend_dist, "assets")}{dist_separator}frontend/dist/assets')
    
    if os.path.exists(os.path.join(frontend_dist, 'index.html')):
        pyinstaller_args.append(f'--add-data={os.path.join(frontend_dist, "index.html")}{dist_separator}frontend/dist')
    
    # 根据操作系统调整路径分隔符
    if platform.system() != 'Windows':
        pyinstaller_args = [arg.replace(';', ':') for arg in pyinstaller_args]
    
    # 添加可选参数
    if args.uac_admin:
        pyinstaller_args.append('--uac-admin')
    
    if args.windowed:
        pyinstaller_args.append('--windowed')
    
    # 添加从requirements.txt提取的隐式导入
    pyinstaller_args.extend(get_hidden_imports())
    
    # 过滤掉空字符串
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    log(f"PyInstaller参数: {' '.join(pyinstaller_args)}")
    
    # 运行构建
    try:
        log("开始后端打包...")
        PyInstaller.__main__.run(pyinstaller_args)
        log("后端打包完成！")
        return True
    except Exception as e:
        log(f"后端打包失败: {e}", "ERROR")
        return False

def main():
    """主函数，处理命令行参数并执行构建流程"""
    parser = argparse.ArgumentParser(description='打包BLOG管理系统')
    parser.add_argument('--skip-frontend', action='store_true', help='跳过前端构建')
    parser.add_argument('--skip-npm-install', action='store_true', help='跳过npm install步骤')
    parser.add_argument('--entry', help='指定后端入口文件路径')
    parser.add_argument('--icon', help='指定应用图标路径')
    parser.add_argument('--name', help='指定输出文件名')
    parser.add_argument('--onefile', action='store_true', default=True, help='打包成单个文件')
    parser.add_argument('--console', action='store_true', default=True, help='显示控制台')
    parser.add_argument('--uac-admin', action='store_true', help='请求管理员权限')
    parser.add_argument('--windowed', action='store_true', help='窗口化应用')
    parser.add_argument('--clean', action='store_true', default=True, help='清理旧构建')
    args = parser.parse_args()
    
    # 显示欢迎信息
    log("=" * 50)
    log("BLOG管理系统打包工具")
    log("=" * 50)
    
    # 清理旧构建
    dist_path = os.path.join(ROOT_DIR, 'dist')
    build_path = os.path.join(ROOT_DIR, 'build')
    
    if args.clean and os.path.exists(dist_path):
        log(f"正在清理旧的dist目录: {dist_path}")
        try:
            shutil.rmtree(dist_path)
        except Exception as e:
            log(f"清理dist目录失败: {e}", "ERROR")
            
    if args.clean and os.path.exists(build_path):
        log(f"正在清理旧的build目录: {build_path}")
        try:
            shutil.rmtree(build_path)
        except Exception as e:
            log(f"清理build目录失败: {e}", "ERROR")
    
    # 构建前端
    if not build_frontend(args):
        log("前端构建失败，终止打包流程", "ERROR")
        return 1
    
    # 构建后端
    if not build_backend(args):
        log("后端打包失败", "ERROR")
        return 1
    
    # 构建完成
    log("=" * 50)
    log("BLOG管理系统打包完成！")
    log("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())