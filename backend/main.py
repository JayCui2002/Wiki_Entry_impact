"""
Wiki Entry Impact Assessment System - Main Application
主要的FastAPI应用程序入口
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import uvicorn
import structlog
from contextlib import asynccontextmanager
import time
from sqlalchemy import text
from datetime import datetime

from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis_client import redis_client
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityMiddleware
from app.middleware.logging import LoggingMiddleware

# 导入路由器 / Import routers
from app.api.v1.api import api_router

# 配置结构化日志 / Configure structured logging
logger = structlog.get_logger()

# 安全认证方案 / Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management
    应用程序生命周期管理
    
    管理应用程序的启动和关闭过程，包括数据库连接、Redis连接等
    """
    # 启动 / Startup
    logger.info("Starting Wiki Impact Assessment System")
    
    # 初始化Redis客户端 / Initialize Redis client
    await redis_client.initialize()

    # 创建数据库表 / Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 测试Redis连接 / Test Redis connection
    if redis_client.is_connected:
        logger.info("Redis connection test successful")
    else:
        logger.warning("Redis is not connected. Caching will be disabled.")
    
    logger.info("Application startup complete")
    yield
    
    # 关闭 / Shutdown
    logger.info("Shutting down Wiki Impact Assessment System")
    await redis_client.close()


# 创建FastAPI应用程序 / Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Wiki Entry Impact Assessment / 维基条目影响评估API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# 设置CORS中间件 / Set up CORS middleware
# 这允许前端（运行在不同端口）与后端通信 / This allows the frontend (running on a different port) to communicate with the backend
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 添加中间件 / Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Gzip压缩中间件
if settings.REDIS_ENABLED:
    app.add_middleware(RateLimitMiddleware)  # 速率限制中间件
# app.add_middleware(SecurityMiddleware) # 暂时禁用以调试CORS问题
app.add_middleware(LoggingMiddleware)  # 日志记录中间件


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add response time header to all requests
    为所有请求添加响应时间头
    
    用于性能监控和调试
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler
    全局异常处理器
    
    捕获所有未处理的异常并返回统一的错误响应
    """
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None)
        }
    )


@app.get("/")
async def root():
    """
    Root endpoint - API status
    根端点 - API状态
    
    返回API的基本状态信息
    """
    return {
        "message": "Wiki Entry Impact Assessment API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled in production"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    健康检查端点
    
    用于容器编排和负载均衡器的健康检查
    """
    # 基本健康检查 / Basic health check
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "unknown",
        "redis": "unknown"
    }
    
    try:
        # 检查数据库连接 / Check database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # 检查Redis连接 / Check Redis connection
    try:
        if redis_client.is_connected:
            health_status["redis"] = "connected"
        else:
            health_status["redis"] = "disconnected"
    except Exception as e:
        health_status["redis"] = f"error: {str(e)}"
    
    return health_status


# 包含API路由 / Include API routers
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    # 直接运行的开发模式 / Development mode when run directly
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=None
    ) 