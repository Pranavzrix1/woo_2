import redis.asyncio as redis
import json
import hashlib
from typing import Any, Optional
from app.config import settings

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes
    
    async def close(self):
        """Close Redis connection"""
        try:
            await self.redis.close()
        except Exception as e:
            print(f"RedisService.close error: {e}")
    
    def _generate_key(self, prefix: str, query: str, limit: int = 10) -> str:
        """Generate cache key from query parameters"""
        key_data = f"{prefix}:{query.lower().strip()}:{limit}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_cached_search(self, query: str, limit: int = 10) -> Optional[list]:
        """Get cached search results"""
        try:
            key = self._generate_key("search", query, limit)
            cached = await self.redis.get(key)
            if cached:
                print(f"[CACHE HIT] Query: {query}, Key: {key}")
                return json.loads(cached)
            else:
                print(f"[CACHE MISS] Query: {query}, Key: {key}")
                return None
        except Exception as e:
            print(f"[CACHE ERROR] {e}")
            return None
    
    async def cache_search(self, query: str, results: list, limit: int = 10, ttl: int = None):
        """Cache search results"""
        try:
            key = self._generate_key("search", query, limit)
            await self.redis.setex(key, ttl or self.default_ttl, json.dumps(results))
            print(f"[CACHE SET] Query: {query}, Results: {len(results)}, TTL: {ttl or self.default_ttl}s")
        except Exception as e:
            print(f"[CACHE SET ERROR] {e}")
    
    async def invalidate_search_cache(self):
        """Clear all search cache"""
        try:
            keys = await self.redis.keys("search:*")
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            print(f"Cache invalidation error: {e}")