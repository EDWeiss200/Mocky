import redis.asyncio as redis
from config import REDIS_URL_TGTOKEN,REDIS_URL_FORGOTPASS

redis_client_tgtoken = redis.Redis.from_url(REDIS_URL_TGTOKEN, decode_responses=True)
redis_client_forgotpass = redis.Redis.from_url(REDIS_URL_FORGOTPASS, decode_responses=True)