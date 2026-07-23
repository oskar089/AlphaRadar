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
    """Single-user portfolio persistence port."""

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
