# AlphaRadar

Semi-autonomous stock analysis and recommendation system for local, single-user use.

## MVP security and persistence boundary

The Compose stack binds the API, PostgreSQL, and Redis exclusively to `127.0.0.1`.
It has no authentication and MUST NOT be exposed to a LAN or the public internet.
Portfolio positions use a process-local in-memory adapter: restarting the API loses them.
PostgreSQL and Redis are local infrastructure prepared for later persistence work; the
current portfolio endpoints do not claim durable storage.

Copy `.env.example` to `.env` and set non-empty values for
`ALPHARADAR_DB_PASSWORD` and `ALPHARADAR_REDIS_PASSWORD` before starting. Compose
rejects missing or empty credentials instead of applying a committed default. If you
run the API outside Compose, update `DATABASE_URL` and `REDIS_URL` to use the same
local credentials.

## Quick start

```bash
pip install -e ".[dev]"
docker compose config --quiet
docker compose up --build -d
```

With `.env` configured, `docker compose config --quiet` must exit successfully. If
the credential variables are unset or empty, it must fail before any service starts.

The API liveness endpoint is `GET /api/health/live`.

## MVP API boundary

The concrete MVP exposes only the routes below:

| Method | Route | Purpose |
| --- | --- | --- |
| GET | `/api/health/live` | Process liveness |
| GET | `/api/stocks/{symbol}` | Fetch one stock from Yahoo Finance |
| GET | `/api/recommendations/{symbol}` | Generate one recommendation |
| GET | `/api/portfolio` | Read the process-local portfolio |
| POST | `/api/portfolio/positions` | Add a position |
| DELETE | `/api/portfolio/positions/{id}` | Remove a position |

Collection routes, portfolio update/performance routes, alerts, dashboard,
scheduler, notifications, and durable portfolio persistence are deferred. The
portfolio boundary is intentionally single-user, loopback-only, and process-local.

## Analysis

Technical analysis uses deterministic pandas-ta-style calculations for SMA20/50/200,
EMA12/26, RSI14, MACD, stochastic, Bollinger bands, ATR14, OBV, volume ratio, and
basic candlestick signals. Fundamental scoring and TextBlob sentiment remain
separate analyzers, and a sentiment failure rebalances the technical and
fundamental weights. Settings require the technical and fundamental weight sum to be
greater than zero, so that fallback remains deterministic.

## Testing

```bash
python -m pytest
ruff check src tests
mypy src
```

The pytest configuration enables the Windows-safe coverage report and fails below
the 70% MVP target without broad exclusions.
