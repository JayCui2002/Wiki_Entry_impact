"""
Database configuration and connection management
数据库配置和连接管理
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase
import structlog

from .config import settings

logger = structlog.get_logger()


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency to get database session
    获取数据库会话的依赖项
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    初始化数据库表
    """
    async with engine.begin() as conn:
        # Import all models to ensure they are registered
        from app.models import user, contributor, wiki_page, edit_history, impact_metrics
        
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


async def close_db():
    """
    Close database connections
    关闭数据库连接
    """
    await engine.dispose()
    logger.info("Database connections closed") 