"""
Tests for API endpoints
API端点测试
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

from app.core.database import get_db


class TestWikipediaEndpoints:
    """
    Wikipedia API端点测试类
    """
    
    @pytest_asyncio.async_test
    async def test_analyze_wiki_page_success(self, client: AsyncClient):
        """
        测试维基百科页面分析成功场景
        """
        # 准备测试数据
        test_data = {
            "page_url": "https://zh.wikipedia.org/wiki/Python"
        }
        
        # 发送请求
        response = await client.post("/api/v1/wikipedia/analyze", json=test_data)
        
        # 验证响应
        assert response.status_code == status.HTTP_202_ACCEPTED
        
        response_data = response.json()
        assert "message" in response_data
        assert "url" in response_data
        assert response_data["url"] == test_data["page_url"]
        assert "已成功排队" in response_data["message"] or "queued" in response_data["message"]
    
    @pytest_asyncio.async_test
    async def test_analyze_wiki_page_invalid_url(self, client: AsyncClient):
        """
        测试无效URL的处理
        """
        # 无效的URL格式
        test_data = {
            "page_url": "这不是一个有效的URL"
        }
        
        response = await client.post("/api/v1/wikipedia/analyze", json=test_data)
        
        # 应该接受请求但任务会在后台失败
        assert response.status_code == status.HTTP_202_ACCEPTED
    
    @pytest_asyncio.async_test
    async def test_analyze_wiki_page_missing_url(self, client: AsyncClient):
        """
        测试缺少URL参数的情况
        """
        # 缺少page_url字段
        test_data = {}
        
        response = await client.post("/api/v1/wikipedia/analyze", json=test_data)
        
        # 应该返回验证错误
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestApplicationEndpoints:
    """
    应用程序基础端点测试类
    """
    
    @pytest_asyncio.async_test
    async def test_root_endpoint(self, client: AsyncClient):
        """
        测试根端点
        """
        response = await client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "operational"
    
    @pytest_asyncio.async_test
    async def test_health_check_endpoint(self, client: AsyncClient):
        """
        测试健康检查端点
        注意：这个测试可能因为Redis/数据库连接而失败，但API应该优雅处理
        """
        response = await client.get("/health")
        
        # 健康检查可能返回200（健康）或503（不健康）
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        
        if response.status_code == status.HTTP_200_OK:
            assert data["status"] == "healthy"
            assert "database" in data
        else:
            assert data["status"] == "unhealthy"
            assert "error" in data


class TestAPIValidation:
    """
    API验证测试类
    """
    
    @pytest_asyncio.async_test
    async def test_request_validation(self, client: AsyncClient):
        """
        测试请求验证
        """
        # 测试空的POST请求
        response = await client.post("/api/v1/wikipedia/analyze")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # 测试错误的Content-Type
        response = await client.post(
            "/api/v1/wikipedia/analyze",
            data="invalid data",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest_asyncio.async_test
    async def test_nonexistent_endpoint(self, client: AsyncClient):
        """
        测试不存在的端点
        """
        response = await client.get("/nonexistent/endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = await client.post("/api/v1/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCORSHeaders:
    """
    CORS头部测试类
    """
    
    @pytest_asyncio.async_test
    async def test_cors_headers(self, client: AsyncClient):
        """
        测试CORS头部设置
        """
        # 发送OPTIONS预检请求
        response = await client.options(
            "/api/v1/wikipedia/analyze",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # 验证CORS头部
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers 