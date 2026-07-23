from fastapi import APIRouter, HTTPException, Request

from alpharadar.api.schemas import AnalysisScoresResponse, RecommendationResponse
from alpharadar.application.services.recommendation import RecommendationService
from alpharadar.domain.errors import (
    HistoricalDataNotFoundError,
    MarketDataUnavailableError,
    SymbolNotFoundError,
)
from alpharadar.domain.interfaces.data_provider import DataProvider

router = APIRouter()


@router.get("/{symbol}", response_model=RecommendationResponse)
async def generate_recommendation(
    symbol: str, request: Request
) -> RecommendationResponse:
    provider: DataProvider = request.app.state.data_provider
    service: RecommendationService = request.app.state.recommendation_service
    try:
        stock = await provider.get_stock(symbol)
        stock.history = await provider.get_history(symbol)
        info = await provider.get_stock_info(symbol)
    except (SymbolNotFoundError, HistoricalDataNotFoundError) as exc:
        raise HTTPException(status_code=404, detail="Symbol data not found") from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Market data unavailable") from exc
    recommendation = await service.generate(stock, info)
    assert recommendation.scores is not None
    return RecommendationResponse(
        symbol=recommendation.symbol,
        action=recommendation.action.value,
        score=recommendation.score,
        confidence=recommendation.confidence,
        reasoning=recommendation.reasoning,
        scores=AnalysisScoresResponse(
            technical=recommendation.scores.technical,
            fundamental=recommendation.scores.fundamental,
            sentiment=recommendation.scores.sentiment,
            final_score=recommendation.scores.final_score or 0.0,
        ),
    )
