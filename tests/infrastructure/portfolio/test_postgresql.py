import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alpharadar.infrastructure.portfolio.postgresql import (
    Base,
    PostgreSQLPortfolioRepository,
)


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
async def repository(db_session: AsyncSession):
    return PostgreSQLPortfolioRepository(db_session)


@pytest.mark.asyncio
async def test_add_position_returns_correct_stored_position(repository):
    result = await repository.add("AAPL", 10, 150.0)
    assert result.id is not None
    assert result.symbol == "AAPL"
    assert result.quantity == 10
    assert result.avg_buy_price == 150.0
    assert result.current_price == 150.0


@pytest.mark.asyncio
async def test_list_positions_returns_all_added(repository):
    await repository.add("AAPL", 10, 150.0)
    await repository.add("GOOGL", 5, 2800.0)
    positions = await repository.list()
    assert len(positions) == 2
    symbols = {p.symbol for p in positions}
    assert symbols == {"AAPL", "GOOGL"}


@pytest.mark.asyncio
async def test_delete_existing_position_returns_true(repository):
    pos = await repository.add("AAPL", 10, 150.0)
    result = await repository.delete(pos.id)
    assert result is True
    positions = await repository.list()
    assert len(positions) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_position_returns_false(repository):
    result = await repository.delete(9999)
    assert result is False
