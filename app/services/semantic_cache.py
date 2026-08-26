import json
import math

import redis.asyncio as redis

from app.core.config import settings

CACHE_KEY_PREFIX = "semantic_cache"
SIMILARITY_THRESHOLD = 0.92
MAX_CACHE_ENTRIES_PER_USER = 50

_redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


async def get_cached_answer(user_id: str, question_embedding: list[float]) -> dict | None:
    client = await get_redis_client()
    key = f"{CACHE_KEY_PREFIX}:{user_id}"
    raw_entries = await client.lrange(key, 0, -1)

    for raw in raw_entries:
        entry = json.loads(raw)
        similarity = _cosine_similarity(question_embedding, entry["embedding"])
        if similarity >= SIMILARITY_THRESHOLD:
            return {"answer": entry["answer"], "sources": entry["sources"], "similarity": similarity}

    return None


async def store_answer(
    user_id: str, question_embedding: list[float], answer: str, sources: list[dict]
) -> None:
    client = await get_redis_client()
    key = f"{CACHE_KEY_PREFIX}:{user_id}"

    entry = json.dumps({"embedding": question_embedding, "answer": answer, "sources": sources})
    await client.lpush(key, entry)
    await client.ltrim(key, 0, MAX_CACHE_ENTRIES_PER_USER - 1)