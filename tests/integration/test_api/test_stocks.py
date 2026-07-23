from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from alpharadar.api.main import create_app
from alpharadar.domain.entities.stock import Stock
from alpharadar.domain.errors import (
    MarketDataCircuitOpenError,
    MarketDataUnavailableError,
    SymbolNotFoundError,
)
from alpharadar.domain.interfaces.data_provider import DataProvider


@pytest.fixture
def provider() -> AsyncMock:
    result = AsyncMock(spec=DataProvider)
    result.get_stock.return_value = Stock("AAPL", "Apple Inc.", "NASDAQ")
    return result


async def test_liveness_endpoint(provider: DataProvider) -> None:
    transport = ASGITransport(app=create_app(provider))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


async def test_stock_collection_placeholder_was_removed(provider: DataProvider) -> None:
    transport = ASGITransport(app=create_app(provider))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stocks")
    assert response.status_code == 404


async def test_get_stock_uses_provider(provider: DataProvider) -> None:
    transport = ASGITransport(app=create_app(provider))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stocks/aapl")
    assert response.status_code == 200
    assert response.json()["name"] == "Apple Inc."


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (SymbolNotFoundError(), 404),
        (MarketDataCircuitOpenError(), 503),
        (MarketDataUnavailableError(), 503),
    ],
)
async def test_stock_maps_market_data_errors(
    provider: AsyncMock, error: Exception, expected_status: int
) -> None:
    provider.get_stock.side_effect = error
    transport = ASGITransport(app=create_app(provider))
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stocks/AAPL")
    assert response.status_code == expected_status
