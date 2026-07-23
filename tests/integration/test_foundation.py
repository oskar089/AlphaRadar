"""Integration test: verify foundation components work together.

Uses SQLite in-memory to test the PostgreSQL portfolio repository
adapter with a real (but lightweight) database backend.
"""

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
async def test_foundation_full_lifecycle(repository):
    """Add positions, list, delete, and verify final state."""
    # Start empty
    positions = await repository.list()
    assert positions == []

    # Add positions
    aapl = await repository.add("AAPL", 10, 150.0)
    googl = await repository.add("GOOGL", 5, 2800.0)
    msft = await repository.add("MSFT", 8, 350.0)

    # Verify added positions have correct data
    assert aapl.symbol == "AAPL"
    assert aapl.quantity == 10
    assert aapl.avg_buy_price == 150.0
    assert aapl.current_price == 150.0
    assert aapl.id is not None

    assert googl.symbol == "GOOGL"
    assert msft.symbol == "MSFT"

    # List all positions
    positions = await repository.list()
    assert len(positions) == 3
    symbols = {p.symbol for p in positions}
    assert symbols == {"AAPL", "GOOGL", "MSFT"}

    # Delete one position
    deleted = await repository.delete(googl.id)
    assert deleted is True

    # Verify deletion
    positions = await repository.list()
    assert len(positions) == 2
    remaining_symbols = {p.symbol for p in positions}
    assert remaining_symbols == {"AAPL", "MSFT"}

    # Delete non-existent returns False
    deleted_again = await repository.delete(googl.id)
    assert deleted_again is False

    # Final state: 2 positions remaining
    final = await repository.list()
    assert len(final) == 2
