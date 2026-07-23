import asyncio
import time
from collections.abc import Callable, Mapping
from typing import Any, TypeVar

import structlog
import yfinance as yf
from curl_cffi.requests.exceptions import RequestException
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from yfinance.exceptions import YFException, YFRateLimitError, YFTickerMissingError

from alpharadar.domain.entities.stock import OHLCV, Stock, StockInfo
from alpharadar.domain.errors import (
    HistoricalDataNotFoundError,
    MarketDataCircuitOpenError,
    MarketDataUnavailableError,
    SymbolNotFoundError,
)
from alpharadar.domain.interfaces.data_provider import DataProvider

T = TypeVar("T")
_RETRIABLE = (ConnectionError, TimeoutError, RequestException, YFRateLimitError)
logger = structlog.get_logger(__name__)


class YahooFinanceProvider(DataProvider):
    """Async, retrying adapter with a small process-local circuit breaker."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_seconds: float = 60.0,
        retry_attempts: int = 3,
        minimum_retry_wait: float = 4.0,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._retry_attempts = retry_attempts
        self._minimum_retry_wait = minimum_retry_wait
        self._failures = 0
        self._opened_until = 0.0

    @staticmethod
    def _ticker(symbol: str) -> Any:
        return yf.Ticker(symbol)

    async def _execute(
        self, operation: Callable[[], T], operation_name: str, symbol: str
    ) -> T:
        self._ensure_circuit_closed()
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(self._retry_attempts),
                wait=wait_exponential(
                    multiplier=1, min=self._minimum_retry_wait, max=10
                ),
                retry=retry_if_exception_type(MarketDataUnavailableError),
                reraise=True,
            ):
                with attempt:
                    self._ensure_circuit_closed()
                    try:
                        result = await asyncio.to_thread(operation)
                    except _RETRIABLE as exc:
                        self._record_failure()
                        logger.warning(
                            "market_data_retry",
                            operation=operation_name,
                            symbol=symbol,
                            error_type=type(exc).__name__,
                            attempt=attempt.retry_state.attempt_number,
                        )
                        raise MarketDataUnavailableError(
                            "Yahoo Finance is temporarily unavailable"
                        ) from exc
                    except YFTickerMissingError as exc:
                        logger.info(
                            "market_data_symbol_not_found",
                            operation=operation_name,
                            symbol=symbol,
                            error_type=type(exc).__name__,
                        )
                        raise SymbolNotFoundError(str(exc)) from exc
                    except YFException as exc:
                        self._record_failure()
                        logger.error(
                            "market_data_provider_failure",
                            operation=operation_name,
                            symbol=symbol,
                            error_type=type(exc).__name__,
                        )
                        raise MarketDataUnavailableError(
                            "Yahoo Finance provider failed"
                        ) from exc
        except MarketDataUnavailableError:
            raise
        self._failures = 0
        return result

    def _ensure_circuit_closed(self) -> None:
        now = time.monotonic()
        if self._opened_until > now:
            raise MarketDataCircuitOpenError(
                "Yahoo Finance circuit is temporarily open"
            )
        if self._opened_until:
            self._opened_until = 0.0
            self._failures = 0

    def _record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._opened_until = time.monotonic() + self._recovery_seconds

    async def get_stock(self, symbol: str) -> Stock:
        normalized = symbol.strip().upper()

        def fetch() -> Stock:
            info: Mapping[str, Any] = self._ticker(normalized).info
            name = info.get("longName") or info.get("shortName")
            if not info or not name:
                raise SymbolNotFoundError(f"Unknown symbol: {normalized}")
            return Stock(
                symbol=normalized,
                name=str(name),
                exchange=str(info.get("exchange") or "Unknown"),
            )

        return await self._execute(fetch, "get_stock", normalized)

    async def get_history(self, symbol: str, period: str = "1y") -> list[OHLCV]:
        normalized = symbol.strip().upper()

        def fetch() -> list[OHLCV]:
            frame = self._ticker(normalized).history(period=period)
            if frame.empty:
                raise HistoricalDataNotFoundError(
                    f"No history for {normalized} over {period}"
                )
            return [
                OHLCV(
                    timestamp=index.to_pydatetime(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
                for index, row in frame.iterrows()
            ]

        return await self._execute(fetch, "get_history", normalized)

    async def get_stock_info(self, symbol: str) -> StockInfo:
        normalized = symbol.strip().upper()

        def fetch() -> StockInfo:
            info: Mapping[str, Any] = self._ticker(normalized).info
            if not info:
                raise SymbolNotFoundError(f"Unknown symbol: {normalized}")
            debt_percentage = info.get("debtToEquity")
            debt_ratio = (
                float(debt_percentage) / 100.0 if debt_percentage is not None else None
            )
            return StockInfo(
                symbol=normalized,
                pe_ratio=info.get("trailingPE"),
                eps=info.get("trailingEps"),
                market_cap=info.get("marketCap"),
                revenue=info.get("totalRevenue"),
                debt_to_equity=debt_ratio,
                dividend_yield=info.get("dividendYield"),
                sector=info.get("sector"),
                industry=info.get("industry"),
            )

        return await self._execute(fetch, "get_stock_info", normalized)
