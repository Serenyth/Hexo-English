import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.blog import router as blog_router
from app.api.posts import router as posts_router
from app.api.file_dialog import router as file_dialog_router
from app.api.essays import router as essays_router


# 创建FastAPI应用
app = FastAPI(
    title="Hexo博客管理系统",
    description="用于本地管理和编辑Hexo博客文章的API",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5173"],  # 允许前端开发服务器访问
    allow_origins=["*"],  # 允许所有源访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(blog_router, prefix="/api/blog", tags=["博客目录"])
app.include_router(posts_router, prefix="/api/posts", tags=["文章管理"])
app.include_router(file_dialog_router, prefix="/api/file-dialog", tags=["文件对话框"])
app.include_router(essays_router, prefix="/api", tags=["即刻说说"]) # 添加 essays 路由

# 根路由
@app.get("/")
async def root():
    return {"message": "正常运行中..., 请访问 /docs 测试api, 或 /redoc 查看api状态"}

# 启动服务器
if __name__ == "__main__":
    # 在打包后的环境中，禁用彩色日志和文件监视
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=7888, 
    )
