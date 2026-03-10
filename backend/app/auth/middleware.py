import time
import logging
import uuid
from typing import Optional
from fastapi import Request, HTTPException, Header, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..db.session import get_async_session
from ..db.models import User, ApiKey
from .jwt import decode_access_token, hash_api_key

logger = logging.getLogger(__name__)

# In-memory rate limit store (use Redis in production for distributed deployments)
_rate_limit_store: dict = {}

EXEMPT_PATHS = {"/health", "/ready", "/docs", "/openapi.json", "/redoc"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter using in-memory store (Redis in production)."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # Use client IP as identifier for unauthenticated requests
        client_id = request.client.host if request.client else "unknown"
        now = time.time()
        minute_bucket = int(now // 60)
        key = f"{client_id}:{minute_bucket}"

        count = _rate_limit_store.get(key, 0)
        if count >= settings.RATE_LIMIT_REQUESTS_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"},
                headers={"Retry-After": str(60 - int(now % 60))},
            )

        _rate_limit_store[key] = count + 1
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status code, and latency for every request."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        latency_ms = (time.time() - start) * 1000
        logger.info(f"{request.method} {request.url.path} → {response.status_code} ({latency_ms:.1f}ms)")
        return response


async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_factanchor_key: Optional[str] = Header(None, alias=settings.API_KEY_HEADER),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Authenticate via JWT Bearer token or API key.
    JWT is tried first; if absent, API key is tried.
    Both fail → 401.
    """
    # Try JWT
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        user_id = decode_access_token(token)
        if user_id:
            result = await session.execute(select(User).where(User.id == uuid.UUID(user_id)))
            user = result.scalar_one_or_none()
            if user and user.is_active:
                return user

    # Try API key
    if x_factanchor_key:
        key_hash = hash_api_key(x_factanchor_key)
        result = await session.execute(select(ApiKey).where(ApiKey.key_hash == key_hash))
        api_key = result.scalar_one_or_none()
        if api_key:
            # Check expiry
            if api_key.expires_at and api_key.expires_at < time.time():
                raise HTTPException(status_code=401, detail="API key expired")
            # Fetch user
            result = await session.execute(select(User).where(User.id == api_key.user_id))
            user = result.scalar_one_or_none()
            if user and user.is_active:
                return user

    raise HTTPException(status_code=401, detail="Authentication required")
