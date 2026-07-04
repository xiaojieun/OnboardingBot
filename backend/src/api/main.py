"""入职智引系统 - FastAPI服务入口

运行方式：
    cd backend
    python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
"""

import os
import sys
from pathlib import Path

# 确保backend目录在Python路径中
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes.auth import router as auth_router
from src.api.routes.chat import router as chat_router
from src.api.routes.management import router as management_router

# 创建FastAPI应用
app = FastAPI(
    title="入职智引系统 API",
    description="基于RAG架构的新员工入职智能助手后端服务",
    version="1.0.0",
)

# CORS中间件配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(management_router)


@app.get("/")
def root():
    """根路径，返回服务状态"""
    return {
        "service": "入职智引系统",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "ok"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": f"服务器内部错误: {str(exc)}"},
    )
