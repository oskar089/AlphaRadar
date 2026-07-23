from httpx import ASGITransport, AsyncClient

from alpharadar.api.main import create_app


async def test_portfolio_crud_is_isolated_per_app() -> None:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/portfolio/positions",
            json={"symbol": "aapl", "quantity": 10, "avg_buy_price": 185.0},
        )
        portfolio = await client.get("/api/portfolio")
        deleted = await client.delete("/api/portfolio/positions/1")
    assert created.status_code == 200
    assert created.json()["symbol"] == "AAPL"
    assert portfolio.json()["portfolio"]["total_value"] == 1850.0
    assert portfolio.json()["portfolio"]["storage"] == "process-local-non-durable"
    assert deleted.status_code == 204


async def test_portfolio_rejects_non_finite_and_blank_values() -> None:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        blank = await client.post(
            "/api/portfolio/positions",
            json={"symbol": "   ", "quantity": 1, "avg_buy_price": 10.0},
        )
        infinite = await client.post(
            "/api/portfolio/positions",
            json={"symbol": "AAPL", "quantity": 1, "avg_buy_price": "Infinity"},
        )
    assert blank.status_code == 422
    assert infinite.status_code == 422


async def test_delete_unknown_position_returns_not_found() -> None:
    transport = ASGITransport(app=create_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/api/portfolio/positions/999")
    assert response.status_code == 404
