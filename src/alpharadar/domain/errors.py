class MarketDataError(Exception):
    """Base error exposed by market-data ports."""


class SymbolNotFoundError(MarketDataError):
    """The provider has no metadata for the requested symbol."""


class HistoricalDataNotFoundError(MarketDataError):
    """The provider has no price history for the requested symbol and period."""


class MarketDataUnavailableError(MarketDataError):
    """The upstream provider failed temporarily after retry."""


class MarketDataCircuitOpenError(MarketDataUnavailableError):
    """Calls are temporarily blocked after repeated upstream failures."""
