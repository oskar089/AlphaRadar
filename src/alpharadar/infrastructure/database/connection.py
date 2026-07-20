from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from alpharadar.config import settings


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_async_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=False)
    return _engine


def get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_async_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _session_factory


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_async_session_factory()
    async with factory() as session:
        yield session
