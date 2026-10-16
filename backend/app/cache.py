import json
from redis.asyncio import Redis
from redis.exceptions import RedisError
from app.config import settings


cache = Redis.from_url(settings.redis_url, decode_responses=True,
                       socket_connect_timeout=2,socket_timeout=2)


async def get_cache(key: str):
    try:
        value = await cache.get(key)
        return json.loads(value) if value is not None else None
    except (RedisError, ValueError):
        return None


async def set_cache(key: str, value: dict, ttl: int = 30):
    try:
        await cache.set(key, json.dumps(value), ex=ttl)
    except RedisError:
        pass


async def clear_cache(*keys: str):
    try:
        if keys:
            await cache.delete(*keys)
    except RedisError:
        pass


async def close_cache():
    await cache.aclose()
