from alpharadar.application.ports.portfolio import PortfolioRepository, StoredPosition


class InMemoryPortfolioRepository(PortfolioRepository):
    """Non-durable, process-local adapter for the single-user MVP."""

    def __init__(self) -> None:
        self._positions: dict[int, StoredPosition] = {}
        self._next_id = 1

    async def list(self) -> list[StoredPosition]:
        return list(self._positions.values())

    async def add(
        self, symbol: str, quantity: int, avg_buy_price: float
    ) -> StoredPosition:
        position = StoredPosition(
            id=self._next_id,
            symbol=symbol,
            quantity=quantity,
            avg_buy_price=avg_buy_price,
            current_price=avg_buy_price,
        )
        self._positions[position.id] = position
        self._next_id += 1
        return position

    async def delete(self, position_id: int) -> bool:
        return self._positions.pop(position_id, None) is not None
