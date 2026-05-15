import os
import shutil
import subprocess
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
FRONTEND_DIR = ROOT_DIR / 'frontend'
BACKEND_DIR = ROOT_DIR / 'backend'
DIST_DIR = ROOT_DIR / 'dist'

def build_frontend():
    """构建前端项目"""
    print("开始构建前端...")
    try:
        # 确保 node_modules 存在
        if not os.path.exists(FRONTEND_DIR / 'node_modules'):
            subprocess.run('npm install', shell=True, cwd=FRONTEND_DIR, check=True)
        
        # 构建前端
        subprocess.run('npm run build', shell=True, cwd=FRONTEND_DIR, check=True)
        print("前端构建成功!")
        
        # 复制构建后的文件到后端的static目录
        static_dir = BACKEND_DIR / 'static'
        if static_dir.exists():
            shutil.rmtree(static_dir)
        shutil.copytree(FRONTEND_DIR / 'dist', static_dir)
        print("前端文件已复制到后端static目录")
        
    except subprocess.CalledProcessError as e:
        print(f"前端构建失败: {e}")
        sys.exit(1)

def build_backend():
    """构建后端项目"""
    print("开始构建后端...")
    try:
        # 创建spec文件
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    [r'{str(BACKEND_DIR / "app.py").replace(os.sep, "/")}'],
    pathex=[],
    binaries=[],
    datas=[
        (r'{str(BACKEND_DIR / "static")}', 'static'),  # 包含静态文件
        (r'{str(BACKEND_DIR / "app")}', 'app'),        # 包含 app 模块
        (r'{str(BACKEND_DIR / "config")}', 'config'),  # 包含默认配置文件
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'starlette',
        'pydantic',
        'pystray', # 添加 pystray
        'PIL',     # 添加 PIL
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False, # 改回 False，因为我们不再需要手动解压
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BlogManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # 设置为 False 以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # 添加图标
    icon=r'{str(BACKEND_DIR / "static" / "favicon.ico").replace(os.sep, "/")}'
)
"""
        spec_file = BACKEND_DIR / 'BlogManager.spec'
        spec_file.write_text(spec_content, encoding='utf-8')

        # 使用 PyInstaller 构建
        subprocess.run(
            f'pyinstaller "{spec_file}" --clean --noconfirm', # 使用 spec 文件构建
            shell=True,
            cwd=BACKEND_DIR,
            check=True
        )
        print("后端构建成功!")

    except subprocess.CalledProcessError as e:
        print(f"后端构建失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    try:
        # 清理旧的构建文件
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        
        # 构建前端和后端
        build_frontend()
        build_backend()
        
        print("\n构建完成!")
        print(f"可执行文件位置: {BACKEND_DIR / 'dist' / 'BlogManager.exe'}")
        
    except Exception as e:
        print(f"构建过程中出现错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()