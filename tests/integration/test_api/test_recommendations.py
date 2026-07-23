from datetime import UTC, datetime
from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from alpharadar.api.main import create_app
from alpharadar.application.services.recommendation import RecommendationService
from alpharadar.domain.entities.recommendation import (
    Action,
    AnalysisScores,
    Recommendation,
)
from alpharadar.domain.entities.stock import OHLCV, Stock, StockInfo
from alpharadar.domain.interfaces.data_provider import DataProvider


async def test_recommendation_route_wires_provider_to_service() -> None:
    provider = AsyncMock(spec=DataProvider)
    provider.get_stock.return_value = Stock("AAPL", "Apple", "NASDAQ")
    provider.get_history.return_value = [
        OHLCV(datetime.now(UTC), 1.0, 2.0, 0.5, 1.5, 100)
    ]
    provider.get_stock_info.return_value = StockInfo("AAPL", pe_ratio=20.0)
    service = AsyncMock(spec=RecommendationService)
    service.generate.return_value = Recommendation(
        symbol="AAPL",
        action=Action.BUY,
        score=75.0,
        confidence=0.75,
        reasoning="Strong combined score",
        scores=AnalysisScores(80.0, 70.0, 0.5, 75.0),
    )
    app = create_app(provider, recommendation_service=service)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/recommendations/AAPL")
    assert response.status_code == 200
    assert response.json()["action"] == "BUY"
    stock = service.generate.await_args.args[0]
    assert len(stock.history) == 1
