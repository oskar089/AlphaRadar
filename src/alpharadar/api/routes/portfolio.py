from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from alpharadar.api.schemas import PositionCreate, PositionResponse
from alpharadar.application.ports.portfolio import PortfolioRepository

router = APIRouter()


@router.get("")
async def get_portfolio(request: Request) -> dict[str, Any]:
    repository: PortfolioRepository = request.app.state.portfolio_repository
    positions = await repository.list()
    total_value = sum(item.quantity * item.current_price for item in positions)
    total_cost = sum(item.quantity * item.avg_buy_price for item in positions)
    return {
        "portfolio": {
            "name": "My Portfolio",
            "positions": positions,
            "total_value": total_value,
            "total_pnl": total_value - total_cost,
            "storage": "process-local-non-durable",
        }
    }


@router.post("/positions", response_model=PositionResponse)
async def add_position(position: PositionCreate, request: Request) -> PositionResponse:
    repository: PortfolioRepository = request.app.state.portfolio_repository
    stored = await repository.add(
        position.symbol, position.quantity, position.avg_buy_price
    )
    return PositionResponse.model_validate(stored, from_attributes=True)


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(position_id: int, request: Request) -> None:
    repository: PortfolioRepository = request.app.state.portfolio_repository
    if not await repository.delete(position_id):
        raise HTTPException(status_code=404, detail="Position not found")
