import os
from pathlib import Path
import redis
from dotenv import load_dotenv

_BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(_BASE_DIR / ".env", encoding="utf-8-sig")

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
)

def get_redis() -> redis.Redis:
    return redis_client