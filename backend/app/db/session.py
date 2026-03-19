from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Async engine for FastAPI
async_engine = create_async_engine(
    settings.database_url,
    echo=(not settings.is_production),
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args={"statement_cache_size": 0}
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Sync engine for Celery workers
sync_engine = create_engine(
    settings.database_url_sync,
    echo=(not settings.is_production),
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

SyncSessionLocal = sessionmaker(bind=sync_engine)


async def get_async_session() -> AsyncSession:
    """Dependency for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        yield session


def get_sync_session():
    """Session factory for Celery workers (synchronous)."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
