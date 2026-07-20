import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy import text

from alpharadar.infrastructure.database.connection import (
    get_async_engine,
    get_async_session_factory,
)


@pytest.fixture()
def engine() -> AsyncEngine:
    return get_async_engine()


@pytest.fixture()
def session_factory() -> async_sessionmaker[AsyncSession]:
    return get_async_session_factory()


def test_engine_creation(engine: AsyncEngine) -> None:
    assert engine is not None


def test_session_factory_creation(session_factory: async_sessionmaker[AsyncSession]) -> None:
    assert session_factory is not None


@pytest.mark.asyncio()
async def test_async_session_yields_session(session_factory: async_sessionmaker[AsyncSession]) -> None:
    from alpharadar.infrastructure.database.connection import get_async_session

    gen = get_async_session()
    session = await gen.__anext__()
    try:
        assert isinstance(session, AsyncSession)
    finally:
        await gen.aclose()
