from alpharadar.domain.entities.portfolio import Portfolio, Position


def test_position_creation():
    pos = Position(
        symbol="AAPL",
        quantity=10,
        avg_buy_price=185.0,
        current_price=190.0,
    )
    assert pos.quantity == 10
    assert pos.unrealized_pnl == 50.0


def test_portfolio_creation():
    portfolio = Portfolio(name="My Portfolio")
    assert portfolio.name == "My Portfolio"
    assert portfolio.total_value == 0.0


def test_portfolio_add_position():
    portfolio = Portfolio(name="Test")
    pos = Position(symbol="AAPL", quantity=10, avg_buy_price=185.0, current_price=190.0)
    portfolio.positions.append(pos)
    assert len(portfolio.positions) == 1
    assert portfolio.total_value == 1900.0
