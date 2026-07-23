from alpharadar.domain.entities.stock import StockInfo
from alpharadar.infrastructure.analyzers.fundamental import RuleBasedFundamentalAnalyzer


async def test_fundamental_score_is_bounded() -> None:
    info = StockInfo("AAPL", 28.5, 6.42, debt_to_equity=1.8, dividend_yield=0.005)
    score = await RuleBasedFundamentalAnalyzer().analyze(info)
    assert 0 <= score <= 100


async def test_undervalued_company_scores_well() -> None:
    info = StockInfo("TEST", pe_ratio=8.0, eps=10.0, debt_to_equity=0.5)
    assert await RuleBasedFundamentalAnalyzer().analyze(info) > 60


async def test_overvalued_company_scores_poorly() -> None:
    info = StockInfo("TEST", pe_ratio=80.0, eps=-0.5, debt_to_equity=5.0)
    assert await RuleBasedFundamentalAnalyzer().analyze(info) < 40
