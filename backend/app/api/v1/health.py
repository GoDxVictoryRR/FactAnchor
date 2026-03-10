from fastapi import APIRouter
from sqlalchemy import text
from ...db.session import async_engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Basic liveness probe."""
    return {"status": "ok"}


@router.get("/ready")
async def ready():
    """Readiness probe — verifies DB connectivity."""
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "db": "ok"}
    except Exception as e:
        return {"status": "not_ready", "db": str(e)}
