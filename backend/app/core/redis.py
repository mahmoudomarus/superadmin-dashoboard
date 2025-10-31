import redis.asyncio as redis
from typing import Optional, Any
import json
from app.config import settings
from app.utils.logger import logger

class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ex: int = 300):
        """Set value in cache with expiry (default 5 min)"""
        if not self.redis:
            return False
        
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                ex=ex
            )
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern"""
        if not self.redis:
            return False
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN error for pattern {pattern}: {e}")
            return False

redis_client = RedisClient()

async def get_redis() -> RedisClient:
    return redis_client

