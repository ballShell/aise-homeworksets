from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1 import trips
import os

app = FastAPI(
    title="AI Travel Planner API",
    description="AI-powered travel planning application (Public Access)",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 公开访问，允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由（必须在静态文件之前注册）
app.include_router(trips.router, prefix="/api/v1")

# 静态文件服务（用于生产环境）
# 在开发环境中，前端由 Vite 开发服务器提供
static_dir = os.path.join(os.path.dirname(__file__), "../../static")
if os.path.exists(static_dir):
    # 挂载静态资源目录（CSS、JS、图片等）
    static_files_dir = os.path.join(static_dir, "assets")
    if os.path.exists(static_files_dir):
        app.mount("/assets", StaticFiles(directory=static_files_dir), name="assets")
    
    # SPA 路由：返回 index.html（必须在最后注册）
    # 注意：这个路由会匹配所有未匹配的路径，所以 API 路由必须在此之前注册
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # 排除 API 路由
        if full_path.startswith("api/") or full_path == "api":
            raise HTTPException(status_code=404, detail="Not found")
        
        # 对于所有其他路径，返回 index.html（SPA 路由）
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}

