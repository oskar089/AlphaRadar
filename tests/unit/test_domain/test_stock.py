from datetime import datetime

from alpharadar.domain.entities.stock import OHLCV, Stock, StockInfo


def test_stock_creation():
    stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
    assert stock.symbol == "AAPL"
    assert stock.name == "Apple Inc."


def test_ohlcv_creation():
    candle = OHLCV(
        timestamp=datetime(2024, 1, 15, 10, 0),
        open=185.0,
        high=187.5,
        low=184.0,
        close=186.2,
        volume=50000000,
    )
    assert candle.close == 186.2
    assert candle.volume == 50000000


def test_stock_info_creation():
    info = StockInfo(
        symbol="AAPL",
        pe_ratio=28.5,
        eps=6.42,
        market_cap=2_900_000_000_000,
        revenue=394_000_000_000,
        debt_to_equity=1.8,
        dividend_yield=0.005,
    )
    assert info.pe_ratio == 28.5
    assert info.market_cap == 2_900_000_000_000
