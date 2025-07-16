"""
Redis client wrapper
Redis客户端的封装
"""

import redis.asyncio as redis
from redis import exceptions as redis_exceptions
import structlog
from typing import Optional, Any, Dict, List
import json

from .config import settings

logger = structlog.get_logger()

class RedisClient:
    """
    A wrapper class for the Redis client to handle connections and operations.
    一个封装了Redis客户端的类，用于处理连接和操作。
    """
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.is_connected: bool = False

    async def initialize(self):
        """
        Initialize the Redis connection if Redis is enabled in the settings.
        如果设置中启用了Redis，则初始化连接。
        """
        if not settings.REDIS_ENABLED:
            logger.warning("Redis is disabled in settings. Skipping connection.")
            return

        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
            )
            await self.ping()
            self.is_connected = True
            logger.info("Successfully connected to Redis.")
        except redis_exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
            self.is_connected = False
        except Exception as e:
            logger.error(f"An unexpected error occurred during Redis initialization: {e}")
            self.client = None
            self.is_connected = False

    async def close(self):
        """
        Gracefully close the Redis connection.
        优雅地关闭Redis连接。
        """
        if self.client and self.is_connected:
            await self.client.close()
            self.is_connected = False
            logger.info("Redis connection closed.")

    async def ping(self) -> bool:
        """
        Ping the Redis server to check the connection.
        Ping Redis服务器以检查连接。
        """
        if self.client and self.is_connected:
            return await self.client.ping()
        return False

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from Redis and decode it from JSON.
        从Redis获取一个值并从JSON解码。
        """
        if not (self.client and self.is_connected):
            return None
        
        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Dict[str, Any], expire: int = 3600):
        """
        Set a value in Redis, encoding it to JSON.
        在Redis中设置一个值，将其编码为JSON。
        """
        if not (self.client and self.is_connected):
            return
            
        await self.client.set(key, json.dumps(value), ex=expire)

    async def delete(self, keys: List[str]):
        """
        Delete one or more keys from Redis.
        从Redis中删除一个或多个键。
        """
        if not (self.client and self.is_connected):
            return
            
        if keys:
            await self.client.delete(*keys)

    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """
        LRANGE operation for lists.
        列表的LRANGE操作。
        """
        if self.client and self.is_connected:
            return await self.client.lrange(key, start, end)
        return []

# Global Redis client instance
redis_client = RedisClient() 