from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.config.settings import get_settings


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is required for database access.")
    return async_sessionmaker(
        create_async_engine(settings.database_url, pool_pre_ping=True),
        expire_on_commit=False,
    )


async def get_database_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session
