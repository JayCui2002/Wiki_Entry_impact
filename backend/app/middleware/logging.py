"""
Logging Middleware
日志中间件
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import structlog

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs incoming requests and outgoing responses.
    记录传入的请求和传出的响应。
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        
        # Log request details
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else "unknown",
        )

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000  # in ms
        
        # Log response details
        logger.info(
            "Request finished",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time_ms=f"{process_time:.2f}",
        )
        
        response.headers["X-Request-ID"] = request_id
        return response 