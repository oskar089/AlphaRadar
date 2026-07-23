from unittest.mock import AsyncMock, patch

import pytest

from alpharadar.application.services.recommendation import RecommendationService
from alpharadar.domain.entities.recommendation import Action
from alpharadar.domain.entities.stock import Stock, StockInfo
from alpharadar.domain.interfaces.analyzer import (
    FundamentalAnalyzer,
    SentimentAnalyzer,
    TechnicalAnalyzer,
)


@pytest.fixture
def stock() -> Stock:
    return Stock("AAPL", "Apple", "NASDAQ")


async def test_buy_recommendation(stock: Stock) -> None:
    technical = AsyncMock(spec=TechnicalAnalyzer)
    fundamental = AsyncMock(spec=FundamentalAnalyzer)
    sentiment = AsyncMock(spec=SentimentAnalyzer)
    technical.analyze.return_value = 80.0
    fundamental.analyze.return_value = 75.0
    sentiment.analyze.return_value = 0.5
    service = RecommendationService(technical, fundamental, sentiment)
    recommendation = await service.generate(stock, StockInfo("AAPL"))
    assert recommendation.action is Action.BUY
    assert recommendation.score > 70


async def test_sell_recommendation(stock: Stock) -> None:
    technical = AsyncMock(spec=TechnicalAnalyzer)
    fundamental = AsyncMock(spec=FundamentalAnalyzer)
    sentiment = AsyncMock(spec=SentimentAnalyzer)
    technical.analyze.return_value = 20.0
    fundamental.analyze.return_value = 25.0
    sentiment.analyze.return_value = -0.5
    service = RecommendationService(technical, fundamental, sentiment)
    recommendation = await service.generate(stock, StockInfo("AAPL"))
    assert recommendation.action is Action.SELL
    assert recommendation.score < 30


async def test_sentiment_failure_rebalances_remaining_analyzers(stock: Stock) -> None:
    technical = AsyncMock(spec=TechnicalAnalyzer)
    fundamental = AsyncMock(spec=FundamentalAnalyzer)
    sentiment = AsyncMock(spec=SentimentAnalyzer)
    technical.analyze.return_value = 80.0
    fundamental.analyze.return_value = 60.0
    sentiment.analyze.side_effect = RuntimeError("news unavailable")
    service = RecommendationService(technical, fundamental, sentiment)
    recommendation = await service.generate(stock, StockInfo("AAPL"))
    assert recommendation.score == 70.0
    assert "weights rebalanced" in recommendation.reasoning


async def test_sentiment_failure_emits_structured_warning(stock: Stock) -> None:
    technical = AsyncMock(spec=TechnicalAnalyzer)
    fundamental = AsyncMock(spec=FundamentalAnalyzer)
    sentiment = AsyncMock(spec=SentimentAnalyzer)
    technical.analyze.return_value = 80.0
    fundamental.analyze.return_value = 60.0
    sentiment.analyze.side_effect = RuntimeError("news unavailable")
    service = RecommendationService(technical, fundamental, sentiment)

    with patch(
        "alpharadar.application.services.recommendation.logger"
    ) as logger:
        await service.generate(stock, StockInfo("AAPL"))

    logger.warning.assert_called_once_with(
        "sentiment_analysis_unavailable",
        symbol="AAPL",
        error_type="RuntimeError",
    )
