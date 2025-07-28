"""
Pytest configuration and fixtures for Wiki Impact Assessment System
维基影响评估系统的Pytest配置和fixtures
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from faker import Faker

from app.core.database import Base, get_db
from app.core.config import settings
from main import app

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

fake = Faker("zh_CN")  # 使用中文fake数据


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    创建事件循环用于异步测试
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    """
    创建测试数据库引擎
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    创建测试数据库会话
    """
    async_session = async_sessionmaker(
        bind=test_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试HTTP客户端
    """
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """
    生成示例用户数据
    """
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "full_name": fake.name(),
        "password": "test_password_123"
    }


@pytest.fixture
def sample_edit_data():
    """
    生成示例编辑数据
    """
    return {
        "contributor_id": 1,
        "page_id": 1,
        "timestamp": fake.date_time(),
        "size_change": fake.random_int(-500, 1000),
        "is_new_page": fake.boolean(chance_of_getting_true=10),
        "is_revert": fake.boolean(chance_of_getting_true=5),
        "is_minor": fake.boolean(chance_of_getting_true=30),
        "comment": fake.sentence(),
        "content_added": fake.random_int(0, 1000),
        "content_removed": fake.random_int(0, 200),
        "text_complexity_score": fake.random.uniform(0, 1),
        "semantic_significance": fake.random.uniform(0, 1)
    }


@pytest.fixture
def sample_discussion_data():
    """
    生成示例讨论数据
    """
    return {
        "talk_page_edits": fake.random_int(0, 50),
        "discussion_initiations": fake.random_int(0, 20),
        "discussion_responses": fake.random_int(0, 100),
        "consensus_building_score": fake.random.uniform(0, 1),
        "conflict_resolution_score": fake.random.uniform(0, 1)
    } 