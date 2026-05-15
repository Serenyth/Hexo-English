# 博客管理系统

这是一个使用 Vue 3 (前端) 和 Python FastAPI (后端) 构建的 Hexo 博客管理工具。

## 功能

*   选择本地 Hexo 博客目录
*   管理文章（创建、编辑、删除、查看列表）
*   管理草稿
*   （待补充其他功能...）

## 如何运行 (开发模式)

你需要同时运行前端和后端服务。

**1. 运行后端服务:**

```bash
# 进入后端目录
cd backend

# (建议) 创建并激活虚拟环境
# python -m venv venv
# venv\Scripts\activate  (Windows)
# source venv/bin/activate (Linux/macOS)

# 安装依赖
pip install -r requirements.txt

# 启动 FastAPI 服务
python app.py
```
后端服务默认运行在 `http://127.0.0.1:8000`。

**2. 运行前端服务:**

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动 Vite 开发服务器
npm run dev
```
前端开发服务器通常会运行在 `http://localhost:5173` 或类似地址，它会自动代理 API 请求到后端。

## 如何打包

可以将整个应用打包成一个可执行文件，方便分发。

1.  **打包前端:**
    ```bash
    cd frontend
    npm install
    npm run build
    ```
    这会在 `frontend/dist` 生成静态文件。

2.  **复制静态文件:**
    *   在 `backend` 目录下创建 `static` 文件夹。
    *   将 `frontend/dist` 目录下的 **所有内容** 复制到 `backend/static` 文件夹。

3.  **打包后端 (使用 PyInstaller):**
    ```bash
    cd backend
    pip install pyinstaller
    pyinstaller --name BlogManager --onefile --add-data "static;static" --add-data "app;app" --add-data "config;config" app.py
    ```
    这会在 `backend/dist` 目录下生成 `BlogManager.exe`。

## 如何运行打包后的程序

1.  找到 `backend/dist/BlogManager.exe` 文件。
2.  双击运行它。
3.  打开浏览器，访问 `http://127.0.0.1:8000`。

## 注意事项

*   打包后的程序依赖 `backend/config` 目录下的配置文件（如 `blog_config.json`），请确保配置文件存在且路径正确。
*   如果移动了 `.exe` 文件，可能需要将 `config` 目录也一并移动，或者确保程序能找到配置文件。 