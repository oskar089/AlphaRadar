# Task 1: PostgreSQL Portfolio Repository

## Task Description

Implement a PostgreSQL-based portfolio repository that follows the existing `PortfolioRepository` interface.

## Files to Create

1. `src/alpharadar/infrastructure/portfolio/postgresql.py`
2. `tests/infrastructure/portfolio/test_postgresql.py`

## Existing Interface

The `PortfolioRepository` interface is defined in `src/alpharadar/application/ports/portfolio.py`:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class StoredPosition:
    id: int
    symbol: str
    quantity: int
    avg_buy_price: float
    current_price: float

class PortfolioRepository(ABC):
    @abstractmethod
    async def list(self) -> list[StoredPosition]:
        """Return every position in the process-local portfolio."""

    @abstractmethod
    async def add(
        self, symbol: str, quantity: int, avg_buy_price: float
    ) -> StoredPosition:
        """Add a position and return its generated identity."""

    @abstractmethod
    async def delete(self, position_id: int) -> bool:
        """Delete a position, returning whether it existed."""
```

## Reference Implementation

See `src/alpharadar/infrastructure/portfolio/in_memory.py` for an example implementation.

## Requirements

1. Create a `PositionModel` SQLAlchemy model with columns:
   - `id` (Integer, primary key, autoincrement)
   - `symbol` (String, nullable=False)
   - `quantity` (Integer, nullable=False)
   - `avg_buy_price` (Float, nullable=False)
   - `current_price` (Float, nullable=False)

2. Create a `Base` class using `DeclarativeBase`

3. Implement `PostgreSQLPortfolioRepository` class that:
   - Takes `AsyncSession` in constructor
   - Implements `list()` - returns all positions as `StoredPosition` objects
   - Implements `add()` - creates position and returns `StoredPosition`
   - Implements `delete()` - deletes position by ID, returns True if deleted

4. Write tests that verify:
   - Adding a position returns correct `StoredPosition`
   - Listing positions returns all added positions
   - Deleting an existing position returns True
   - Deleting a non-existent position returns False

## Test Requirements

- Use `sqlite+aiosqlite:///:memory:` for test database
- Use `pytest.mark.asyncio` for async tests
- Create fixtures for `db_session` and `repository`

## Interfaces

- Consumes: `PortfolioRepository` port, `StoredPosition` dataclass
- Produces: `PostgreSQLPortfolioRepository` class, `PositionModel` model, `Base` class

## Global Constraints

- Python 3.11+
- SQLAlchemy 2.0+ (async)
- All code must have tests
- Follow existing project patterns in `src/alpharadar/`

## Success Criteria

- [ ] All tests pass
- [ ] Code follows existing patterns
- [ ] No overbuilding (YAGNI)
