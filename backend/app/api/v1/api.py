"""
API Router for version 1
V1版本的API路由器
"""
from fastapi import APIRouter

from .endpoints import auth, contributors, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(contributors.router, prefix="/contributors", tags=["Contributors"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"]) 