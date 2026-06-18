import os
import json
import redis
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

def _create_redis_client():
    url = os.getenv("REDIS_URL")
    if url:
        return redis.from_url(url, decode_responses=True)
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True
    )

redis_client = _create_redis_client()

def check_redis() -> bool:
    try:
        redis_client.ping()
        logger.info("Redis connected")
        return True
    except Exception as e:
        logger.warning(f"Redis unavailable: {e}")
        return False

def get_cache(key: str):
    try:
        value = redis_client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception as e:
        logger.warning(f"Redis GET error [{key}]: {e}")
        return None

def set_cache(key: str, value, ttl: int=300):
    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    except Exception as e:
        logger.warning(f"Redis SET error [{key}]: {e}")

def delete_cache(key: str):
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.warning(f"Redis DELETE error [{key}]: {e}")