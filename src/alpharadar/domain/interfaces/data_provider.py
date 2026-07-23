from abc import ABC, abstractmethod

from alpharadar.domain.entities.stock import OHLCV, Stock, StockInfo


class DataProvider(ABC):
    @abstractmethod
    async def get_stock(self, symbol: str) -> Stock:
        """Fetch stock metadata."""

    @abstractmethod
    async def get_history(self, symbol: str, period: str = "1y") -> list[OHLCV]:
        """Fetch historical OHLCV data."""

    @abstractmethod
    async def get_stock_info(self, symbol: str) -> StockInfo:
        """Fetch fundamental stock information."""
