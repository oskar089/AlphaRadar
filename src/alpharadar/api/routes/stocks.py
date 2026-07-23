from fastapi import APIRouter, HTTPException, Request

from alpharadar.api.schemas import StockResponse
from alpharadar.domain.errors import MarketDataUnavailableError, SymbolNotFoundError
from alpharadar.domain.interfaces.data_provider import DataProvider

router = APIRouter()


@router.get("/{symbol}", response_model=StockResponse)
async def get_stock(symbol: str, request: Request) -> StockResponse:
    provider: DataProvider = request.app.state.data_provider
    try:
        stock = await provider.get_stock(symbol)
    except SymbolNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Symbol not found") from exc
    except MarketDataUnavailableError as exc:
        raise HTTPException(status_code=503, detail="Market data unavailable") from exc
    return StockResponse(symbol=stock.symbol, name=stock.name, exchange=stock.exchange)
