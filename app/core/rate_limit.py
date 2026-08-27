from fastapi import Depends, HTTPException, Request, status

from app.core.config import settings
from app.core.redis_pool import get_arq_pool


async def rate_limiter(request: Request):
    pool = await get_arq_pool()

    client_id = request.headers.get("authorization", request.client.host if request.client else "unknown")
    key = f"rate_limit:{client_id}:{request.url.path}"

    current = await pool.incr(key)
    if current == 1:
        await pool.expire(key, 60)

    if current > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {settings.rate_limit_per_minute} requests per minute",
        )