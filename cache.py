import os

from dotenv import load_dotenv
from redis.asyncio import Redis

from typing import Any

load_dotenv()

REDIS_URL: str = os.getenv("REDIS_URL")

redis: Redis = Redis.from_url(REDIS_URL)

async def get_cache_data(cid: str) -> Any:
    try:
        return await redis.get(cid)
    except Exception as e:
        return None

async def set_cache_data(cid: str, data: str | dict | list, es: int) -> None:
    try:
        await redis.set(cid, value=data, ex=es)
    except:
        raise ValueError("Something went wrong in saving cache data")

async def delete_cache(cid: str) -> None:
    try:
        await redis.delete(cid)
    except Exception as e:
        return None