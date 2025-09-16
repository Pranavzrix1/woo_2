import redis.asyncio as redis
import json
import hashlib
from typing import Any, Optional
from app.config import settings

class CacheService:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes
    
    def _make_key(self, prefix: str, *args) -> str:
        """Create cache key from prefix and arguments"""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def get_search_results(self, query: str, limit: int) -> Optional[list]:
        """Get cached search results"""
        key = self._make_key("search", query, limit)
        return await self.get(key)
    
    async def cache_search_results(self, query: str, limit: int, results: list) -> bool:
        """Cache search results"""
        key = self._make_key("search", query, limit)
        return await self.set(key, results, ttl=180)  # 3 minutes for search
    
    async def close(self):
        """Close Redis connection"""
        try:
            await self.redis.close()
        except Exception:
            pass