import json
from typing import Optional, Any
import redis.asyncio as redis
from bot.config import REDIS_URL

class Cache:
    def __init__(self):
        self.redis_url = REDIS_URL
        self._client: Optional[redis.Redis] = None
    
    async def get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client
    
    async def get(self, key: str) -> Optional[str]:
        client = await self.get_client()
        return await client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600):
        client = await self.get_client()
        await client.set(key, value, ex=expire)
    
    async def set_json(self, key: str, value: Any, expire: int = 3600):
        client = await self.get_client()
        await client.set(key, json.dumps(value), ex=expire)
    
    async def get_json(self, key: str) -> Optional[Any]:
        client = await self.get_client()
        data = await client.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def delete(self, key: str):
        client = await self.get_client()
        await client.delete(key)
    
    async def clear_pattern(self, pattern: str):
        client = await self.get_client()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)
    
    async def close(self):
        if self._client:
            await self._client.close()

_cache: Optional[Cache] = None

def get_cache() -> Cache:
    global _cache
    if _cache is None:
        _cache = Cache()
    return _cache

async def get_cached_video_list(key: str) -> Optional[list]:
    cache = get_cache()
    return await cache.get_json(f"videos:{key}")

async def set_cached_video_list(key: str, videos: list, expire: int = 1800):
    cache = get_cache()
    await cache.set_json(f"videos:{key}", videos, expire)
