from abc import ABC, abstractmethod

from alpharadar.domain.entities.stock import Stock, StockInfo


class TechnicalAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, stock: Stock) -> float:
        """Return technical score 0-100."""


class FundamentalAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, info: StockInfo) -> float:
        """Return fundamental score 0-100."""


class SentimentAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, symbol: str) -> float:
        """Return sentiment score -1 to +1."""
