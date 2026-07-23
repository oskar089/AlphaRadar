from datetime import datetime, timedelta

import pytest

from alpharadar.domain.entities.stock import OHLCV, Stock
from alpharadar.infrastructure.analyzers.technical import TrendMomentumTechnicalAnalyzer


@pytest.fixture
def rising_stock() -> Stock:
    history = []
    for index in range(200):
        price = 100.0 + index * 0.5 + (index % 3 - 1) * 2
        history.append(
            OHLCV(
                datetime(2024, 1, 1) + timedelta(days=index),
                price - 1,
                price + 2,
                price - 2,
                price,
                1_000_000 + index * 10_000,
            )
        )
    return Stock("TEST", "Test Corp", "NYSE", history=history)


async def test_technical_score_is_bounded(rising_stock: Stock) -> None:
    score = await TrendMomentumTechnicalAnalyzer().analyze(rising_stock)
    assert 0 <= score <= 100


async def test_uptrend_scores_above_neutral(rising_stock: Stock) -> None:
    assert await TrendMomentumTechnicalAnalyzer().analyze(rising_stock) > 50


async def test_insufficient_history_is_neutral() -> None:
    stock = Stock("TEST", "Test", "NYSE")
    assert await TrendMomentumTechnicalAnalyzer().analyze(stock) == 50


def test_calculate_indicators_includes_the_mvp_indicator_set(
    rising_stock: Stock,
) -> None:
    analyzer = TrendMomentumTechnicalAnalyzer()
    indicators = analyzer.calculate_indicators(rising_stock)

    assert indicators.sma20 == pytest.approx(
        sum(c.close for c in rising_stock.history[-20:]) / 20
    )
    assert indicators.sma50 == pytest.approx(
        sum(c.close for c in rising_stock.history[-50:]) / 50
    )
    assert indicators.sma200 is not None
    assert indicators.ema12 is not None
    assert indicators.ema12 == pytest.approx(196.64838337182448)
    assert indicators.ema26 is not None
    assert indicators.rsi is not None
    assert 0.0 <= indicators.rsi <= 100.0
    assert indicators.macd is not None
    assert indicators.macd_signal is not None
    assert indicators.macd_histogram == pytest.approx(
        indicators.macd - indicators.macd_signal
    )
    assert indicators.stoch_k is not None
    assert indicators.stoch_d is not None
    assert indicators.bb_upper is not None
    assert indicators.bb_middle is not None
    assert indicators.bb_lower is not None
    assert indicators.bb_upper > indicators.bb_middle > indicators.bb_lower
    assert indicators.atr is not None
    assert indicators.obv is not None
    assert indicators.volume_ratio is not None


def test_calculate_indicators_detects_bullish_engulfing() -> None:
    history = [
        OHLCV(datetime(2024, 1, 1), 105.0, 106.0, 99.0, 100.0, 1_000),
        OHLCV(datetime(2024, 1, 2), 98.0, 110.0, 97.0, 108.0, 1_500),
    ]

    indicators = TrendMomentumTechnicalAnalyzer().calculate_indicators(
        Stock("TEST", "Test", "NYSE", history=history)
    )

    assert indicators.bullish_engulfing is True
