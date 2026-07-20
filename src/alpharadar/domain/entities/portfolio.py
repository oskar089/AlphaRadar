from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Position:
    symbol: str
    quantity: int
    avg_buy_price: float
    current_price: float

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.avg_buy_price) * self.quantity

    @property
    def market_value(self) -> float:
        return self.current_price * self.quantity


@dataclass
class Portfolio:
    name: str
    positions: list[Position] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total_value(self) -> float:
        return sum(p.market_value for p in self.positions)

    @property
    def total_pnl(self) -> float:
        return sum(p.unrealized_pnl for p in self.positions)
