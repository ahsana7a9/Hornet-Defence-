import redis
import json
import logging

logger = logging.getLogger(__name__)

_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            client = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=2)
            client.ping()
            _redis_client = client
            logger.info("[Redis] Connected successfully")
        except Exception as e:
            logger.warning(f"[Redis] Not available: {e} — running without Redis")
            _redis_client = None
    return _redis_client

def publish(channel: str, data: dict):
    r = get_redis()
    if r:
        try:
            r.publish(channel, json.dumps(data))
        except Exception as e:
            logger.warning(f"[Redis] Publish failed: {e}")

def subscribe(channel: str):
    r = get_redis()
    if r:
        try:
            pubsub = r.pubsub()
            pubsub.subscribe(channel)
            return pubsub
        except Exception as e:
            logger.warning(f"[Redis] Subscribe failed: {e}")
    return None
