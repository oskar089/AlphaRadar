from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class OHLCV:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class StockInfo:
    symbol: str
    pe_ratio: float | None = None
    eps: float | None = None
    market_cap: float | None = None
    revenue: float | None = None
    debt_to_equity: float | None = None
    dividend_yield: float | None = None
    sector: str | None = None
    industry: str | None = None


@dataclass
class Stock:
    symbol: str
    name: str
    exchange: str
    info: StockInfo | None = None
    history: list[OHLCV] = field(default_factory=list)
