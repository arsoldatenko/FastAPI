import asyncio
from app.config import REDIS_URL
import redis.asyncio as redis

redis = redis.from_url(REDIS_URL, decode_responses=True)


async def test_redis():
    pong = await redis.ping()
    print("Redis connected:", pong)


def init_redis():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_redis())
