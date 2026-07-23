from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from alpharadar.application.ports.portfolio import PortfolioRepository, StoredPosition


class Base(DeclarativeBase):
    pass


class PositionModel(Base):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    avg_buy_price: Mapped[float] = mapped_column(nullable=False)
    current_price: Mapped[float] = mapped_column(nullable=False)


class PostgreSQLPortfolioRepository(PortfolioRepository):
    """PostgreSQL adapter for the portfolio repository port."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self) -> list[StoredPosition]:
        from sqlalchemy import select

        result = await self._session.execute(select(PositionModel))
        return [
            StoredPosition(
                id=row.id,
                symbol=row.symbol,
                quantity=row.quantity,
                avg_buy_price=row.avg_buy_price,
                current_price=row.current_price,
            )
            for row in result.scalars()
        ]

    async def add(
        self, symbol: str, quantity: int, avg_buy_price: float
    ) -> StoredPosition:
        position = PositionModel(
            symbol=symbol,
            quantity=quantity,
            avg_buy_price=avg_buy_price,
            current_price=avg_buy_price,
        )
        self._session.add(position)
        await self._session.flush()
        return StoredPosition(
            id=position.id,
            symbol=position.symbol,
            quantity=position.quantity,
            avg_buy_price=position.avg_buy_price,
            current_price=position.current_price,
        )

    async def delete(self, position_id: int) -> bool:
        from sqlalchemy import delete

        result = await self._session.execute(
            delete(PositionModel).where(PositionModel.id == position_id)
        )
        rowcount: int = result.rowcount  # type: ignore[attr-defined]
        return rowcount > 0
