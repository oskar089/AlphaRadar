from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from alpharadar.api.routes import portfolio, recommendations, stocks
from alpharadar.application.ports.portfolio import PortfolioRepository
from alpharadar.application.services.recommendation import RecommendationService
from alpharadar.domain.interfaces.data_provider import DataProvider
from alpharadar.infrastructure.analyzers.fundamental import RuleBasedFundamentalAnalyzer
from alpharadar.infrastructure.analyzers.sentiment import TextBlobSentimentAnalyzer
from alpharadar.infrastructure.analyzers.technical import TrendMomentumTechnicalAnalyzer
from alpharadar.infrastructure.data_providers.yahoo_finance import YahooFinanceProvider
from alpharadar.infrastructure.portfolio.in_memory import InMemoryPortfolioRepository


def create_app(
    data_provider: DataProvider | None = None,
    portfolio_repository: PortfolioRepository | None = None,
    recommendation_service: RecommendationService | None = None,
) -> FastAPI:
    """Compose the single-user, loopback-only MVP application."""
    app = FastAPI(title="AlphaRadar", version="0.1.0")
    app.state.data_provider = data_provider or YahooFinanceProvider()
    app.state.portfolio_repository = (
        portfolio_repository or InMemoryPortfolioRepository()
    )
    app.state.recommendation_service = recommendation_service or RecommendationService(
        TrendMomentumTechnicalAnalyzer(),
        RuleBasedFundamentalAnalyzer(),
        TextBlobSentimentAnalyzer(),
    )
    app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
    app.include_router(
        recommendations.router,
        prefix="/api/recommendations",
        tags=["recommendations"],
    )

    @app.get("/api/health/live")
    async def liveness() -> dict[str, str]:
        return {"status": "alive", "version": "0.1.0"}

    DIST_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
    if DIST_DIR.is_dir():
        app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="static")

    return app


app = create_app()
