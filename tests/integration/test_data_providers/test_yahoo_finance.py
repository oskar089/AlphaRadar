from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from curl_cffi.requests.exceptions import RequestException
from yfinance.exceptions import YFException

from alpharadar.domain.errors import (
    HistoricalDataNotFoundError,
    MarketDataCircuitOpenError,
    MarketDataUnavailableError,
    SymbolNotFoundError,
)
from alpharadar.infrastructure.data_providers.yahoo_finance import YahooFinanceProvider


@pytest.fixture
def ticker() -> MagicMock:
    result = MagicMock()
    result.info = {
        "longName": "Apple Inc.",
        "exchange": "NASDAQ",
        "trailingPE": 28.5,
        "trailingEps": 6.42,
        "marketCap": 2_900_000_000_000,
        "totalRevenue": 394_000_000_000,
        "debtToEquity": 180.0,
        "dividendYield": 0.005,
        "sector": "Technology",
        "industry": "Consumer Electronics",
    }
    result.history.return_value = pd.DataFrame(
        {
            "Open": [210.0],
            "High": [214.0],
            "Low": [209.0],
            "Close": [213.0],
            "Volume": [42_000_000],
        },
        index=pd.DatetimeIndex([datetime(2026, 7, 17, tzinfo=UTC)]),
    )
    return result


@pytest.fixture
def provider(ticker: MagicMock):
    provider = YahooFinanceProvider(minimum_retry_wait=0)
    with patch.object(provider, "_ticker", return_value=ticker):  # noqa: SIM117
        yield provider


async def test_get_stock(provider: YahooFinanceProvider) -> None:
    stock = await provider.get_stock(" aapl ")
    assert (stock.symbol, stock.name, stock.exchange) == (
        "AAPL",
        "Apple Inc.",
        "NASDAQ",
    )


async def test_get_history(provider: YahooFinanceProvider) -> None:
    history = await provider.get_history("AAPL", "1mo")
    assert len(history) == 1
    assert history[0].close == 213.0


async def test_normalizes_yahoo_debt_percentage_to_ratio(
    provider: YahooFinanceProvider,
) -> None:
    info = await provider.get_stock_info("AAPL")
    assert info.debt_to_equity == 1.8


async def test_empty_metadata_is_not_a_valid_symbol(ticker: MagicMock) -> None:
    ticker.info = {}
    provider = YahooFinanceProvider(minimum_retry_wait=0)
    with patch.object(provider, "_ticker", return_value=ticker):  # noqa: SIM117
        with pytest.raises(SymbolNotFoundError):
            await provider.get_stock("MISSING")


async def test_empty_history_is_distinct_from_transport_failure(
    ticker: MagicMock,
) -> None:
    ticker.history.return_value = pd.DataFrame()
    provider = YahooFinanceProvider(minimum_retry_wait=0)
    with patch.object(provider, "_ticker", return_value=ticker):  # noqa: SIM117
        with pytest.raises(HistoricalDataNotFoundError):
            await provider.get_history("AAPL")


async def test_generic_yahoo_failure_is_temporarily_unavailable() -> None:
    provider = YahooFinanceProvider(retry_attempts=1, minimum_retry_wait=0)
    with patch.object(
        provider, "_ticker", side_effect=YFException("provider outage")
    ), patch(
        "alpharadar.infrastructure.data_providers.yahoo_finance.logger"
    ) as logger, pytest.raises(MarketDataUnavailableError):
        await provider.get_stock("AAPL")

    logger.error.assert_called_once_with(
        "market_data_provider_failure",
        operation="get_stock",
        symbol="AAPL",
        error_type="YFException",
    )


async def test_transport_failures_retry_then_open_circuit() -> None:
    provider = YahooFinanceProvider(
        failure_threshold=2, retry_attempts=3, minimum_retry_wait=0
    )
    with patch.object(
        provider, "_ticker", side_effect=RequestException("offline")
    ) as ticker_factory:
        with pytest.raises(MarketDataCircuitOpenError):
            await provider.get_stock("AAPL")
        assert ticker_factory.call_count == 2
        with pytest.raises(MarketDataCircuitOpenError):
            await provider.get_stock("AAPL")
        assert ticker_factory.call_count == 2
