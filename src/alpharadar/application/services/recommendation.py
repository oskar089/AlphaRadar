import asyncio

import structlog

from alpharadar.config import Settings, settings
from alpharadar.domain.entities.recommendation import (
    Action,
    AnalysisScores,
    Recommendation,
)
from alpharadar.domain.entities.stock import Stock, StockInfo
from alpharadar.domain.interfaces.analyzer import (
    FundamentalAnalyzer,
    SentimentAnalyzer,
    TechnicalAnalyzer,
)

logger = structlog.get_logger(__name__)


class RecommendationService:
    """Orchestrate independent analyzers into a bounded recommendation score."""

    def __init__(
        self,
        technical_analyzer: TechnicalAnalyzer,
        fundamental_analyzer: FundamentalAnalyzer,
        sentiment_analyzer: SentimentAnalyzer,
        configuration: Settings = settings,
    ) -> None:
        self.technical = technical_analyzer
        self.fundamental = fundamental_analyzer
        self.sentiment = sentiment_analyzer
        self.settings = configuration

    async def generate(self, stock: Stock, info: StockInfo) -> Recommendation:
        technical, fundamental = await asyncio.gather(
            self.technical.analyze(stock),
            self.fundamental.analyze(info),
        )
        sentiment_available = True
        try:
            sentiment = await self.sentiment.analyze(stock.symbol)
        except Exception as exc:
            sentiment = 0.0
            sentiment_available = False
            logger.warning(
                "sentiment_analysis_unavailable",
                symbol=stock.symbol,
                error_type=type(exc).__name__,
            )

        if sentiment_available:
            weighted_score = (
                technical * self.settings.weight_technical
                + fundamental * self.settings.weight_fundamental
                + (sentiment + 1.0) * 50.0 * self.settings.weight_sentiment
            )
        else:
            active_weight = (
                self.settings.weight_technical + self.settings.weight_fundamental
            )
            weighted_score = (
                technical * self.settings.weight_technical
                + fundamental * self.settings.weight_fundamental
            ) / active_weight
        final_score = max(0.0, min(100.0, weighted_score))

        if final_score >= self.settings.buy_threshold:
            action = Action.BUY
            confidence = min(final_score / 100.0, 0.95)
        elif final_score <= self.settings.sell_threshold:
            action = Action.SELL
            confidence = min((100.0 - final_score) / 100.0, 0.95)
        else:
            action = Action.HOLD
            confidence = 0.5
        scores = AnalysisScores(technical, fundamental, sentiment, final_score)
        sentiment_reason = (
            f"Sentiment: {sentiment:+.2f}"
            if sentiment_available
            else "Sentiment: unavailable (weights rebalanced)"
        )
        recommendation = Recommendation(
            symbol=stock.symbol,
            action=action,
            score=final_score,
            confidence=confidence,
            reasoning=(
                f"Technical: {technical:.1f}/100, "
                f"Fundamental: {fundamental:.1f}/100, "
                f"{sentiment_reason}"
            ),
            scores=scores,
        )
        logger.info(
            "recommendation_generated",
            symbol=stock.symbol,
            action=action.value,
            score=round(final_score, 2),
            sentiment_available=sentiment_available,
        )
        return recommendation
