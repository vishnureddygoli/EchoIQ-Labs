import json
from typing import Any
from redis import Redis
from .config import get_settings

QUEUE_NAME = "echoiq:outbound_calls"

def get_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)

def enqueue_call(payload: dict[str, Any], queue_name: str = QUEUE_NAME) -> int:
    return get_redis().rpush(queue_name, json.dumps(payload, default=str))

def dequeue_call(timeout: int = 5, queue_name: str = QUEUE_NAME) -> dict[str, Any] | None:
    item = get_redis().blpop([queue_name], timeout=timeout)
    if not item:
        return None
    _, raw = item
    return json.loads(raw)

def redis_health() -> str:
    try:
        return "ok" if get_redis().ping() else "error"
    except Exception:
        return "error"
