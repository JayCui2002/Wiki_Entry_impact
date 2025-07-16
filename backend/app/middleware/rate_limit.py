"""
Rate Limiting Middleware
速率限制中间件
"""
import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response, JSONResponse
import structlog

from app.core.redis_client import redis_client
from app.core.config import settings

logger = structlog.get_logger()

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to limit requests based on IP address.
    基于IP地址限制请求的中间件。
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Whitelist certain paths if needed
        if path.startswith("/docs") or path.startswith("/redoc"):
            return await call_next(request)

        # Use a pipeline for atomic operations
        pipeline = await redis_client.pipeline()
        
        # Use a simple fixed window algorithm
        key = f"rate_limit:{client_ip}:{path}"
        current = await redis_client.get(key)
        
        if current and int(current) >= settings.RATE_LIMIT_REQUESTS:
            logger.warning("Rate limit exceeded", client_ip=client_ip, path=path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too Many Requests"},
            )
        
        await pipeline.incr(key)
        await pipeline.expire(key, settings.RATE_LIMIT_WINDOW)
        await pipeline.execute()
        
        response = await call_next(request)
        return response 