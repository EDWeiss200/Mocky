import redis.asyncio as redis
from config import REDIS_URL_TGTOKEN

redis_client = redis.Redis.from_url(REDIS_URL_TGTOKEN, decode_responses=True)