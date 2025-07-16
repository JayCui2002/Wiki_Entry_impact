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

from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis_client import redis_client
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityMiddleware
from app.middleware.logging import LoggingMiddleware

# Import routers
from app.api.v1.api import api_router

# Configure structured logging
logger = structlog.get_logger()

# Security scheme
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management
    应用程序生命周期管理
    """
    # Startup
    logger.info("Starting Wiki Impact Assessment System")
    
    # Initialize Redis client
    await redis_client.initialize()

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Test Redis connection
    if redis_client.is_connected:
        logger.info("Redis connection test successful")
    else:
        logger.warning("Redis is not connected. Caching will be disabled.")
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down Wiki Impact Assessment System")
    await redis_client.close()


# Create FastAPI application
app = FastAPI(
    title="Wiki Entry Impact Assessment API",
    description="A computational model for assessing contributor impact on wiki entry formation",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
if settings.REDIS_ENABLED:
    app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add response time header to all requests
    为所有请求添加响应时间头
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    全局异常处理器
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
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
    """
    return {
        "message": "Wiki Entry Impact Assessment API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    健康检查端点
    """
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        # Test Redis connection
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected" if redis_client.is_connected else "disconnected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


# Include API routers
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_config=None,  # Use structlog instead
    ) 