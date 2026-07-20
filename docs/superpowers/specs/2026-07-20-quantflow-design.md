# AlphaRadar — Autonomous Stock Analysis & Recommendation System

**Date:** 2026-07-20
**Author:** Gentle AI + User
**Status:** Design Approved

---

## 1. Overview

AlphaRadar is a semi-autonomous trading bot that analyzes global stock markets (Europe, Asia, Americas) and provides investment recommendations. The system combines technical analysis, fundamental analysis, and sentiment analysis to generate buy/hold/sell recommendations. The user reviews and approves each recommendation before any action is taken.

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Autonomy Level | Semi-autonomous (recommendations) | User approves each trade |
| Markets | Global (Europe, Asia, Americas) | Broad coverage |
| Analysis Types | Technical + Fundamental + Sentiment | Comprehensive view |
| Architecture | Monolito Python (Clean Architecture) | Fast MVP, easy to refactor later |
| Stack | FastAPI + PostgreSQL + Redis + pandas | Python ecosystem for finance |
| Frontend | HTML + Tailwind + HTMX | Simple, no framework overhead |
| Deployment | Local first → Cloud later | Zero cost MVP |

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                  QuantFlow Application               │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Data      │  │  Analysis   │  │ Sentiment   │ │
│  │  Ingestion  │  │   Engine    │  │  Analyzer   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │Recommendation│  │  Portfolio  │  │   Alert     │ │
│  │   Engine     │  │   Tracker   │  │   System    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │              Scheduler (APScheduler)          │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         │              │              │
         ▼              ▼              ▼
    PostgreSQL        Redis       External APIs
    (persisted)      (cache)     (yfinance, etc.)
```

### 2.2 Project Structure

```
inversiones/
├── src/
│   ├── domain/                  # Entities and pure business rules
│   │   ├── entities/
│   │   │   ├── stock.py         # Stock, OHLCV data
│   │   │   ├── analysis.py      # AnalysisResult, signals
│   │   │   ├── recommendation.py # Buy/Hold/Sell recommendation
│   │   │   ├── portfolio.py     # Position, Holding, Portfolio
│   │   │   └── alert.py         # Alert, AlertType
│   │   └── interfaces/          # Abstract base classes (ports)
│   │       ├── data_provider.py
│   │       ├── analyzer.py
│   │       └── notifier.py
│   │
│   ├── application/             # Use cases / orchestration
│   │   ├── services/
│   │   │   ├── market_data.py    # Coordinates data fetching
│   │   │   ├── analysis.py       # Coordinates technical+fundamental
│   │   │   ├── sentiment.py      # Coordinates sentiment analysis
│   │   │   ├── recommendation.py # Generates recommendations
│   │   │   ├── portfolio.py      # Manages user portfolio
│   │   │   ├── alert.py          # Manages alerts
│   │   │   └── scheduler.py      # Schedules periodic executions
│   │   └── dto/
│   │       ├── stock_dto.py
│   │       └── analysis_dto.py
│   │
│   ├── infrastructure/          # Concrete implementations
│   │   ├── data_providers/
│   │   │   ├── yahoo_finance.py  # yfinance for market data
│   │   │   ├── alpha_vantage.py  # Alpha Vantage (free tier)
│   │   │   └── news_scraper.py   # Playwright for news scraping
│   │   ├── analyzers/
│   │   │   ├── technical.py      # pandas + pandas-ta for indicators
│   │   │   ├── fundamental.py    # Earnings, P/E, financials
│   │   │   └── sentiment.py      # TextBlob / transformers
│   │   ├── database/
│   │   │   ├── models.py         # SQLAlchemy models
│   │   │   ├── repository.py     # Repositories (SQLAlchemy)
│   │   │   └── connection.py     # DB session management
│   │   ├── cache/
│   │   │   └── redis_cache.py    # Redis for market data cache
│   │   └── notifications/
│   │       ├── email_notifier.py # SMTP for email alerts
│   │       └── telegram_bot.py   # Telegram for push alerts
│   │
│   ├── api/                     # FastAPI endpoints
│   │   ├── main.py              # App factory
│   │   ├── routes/
│   │   │   ├── stocks.py        # /api/stocks/*
│   │   │   ├── analysis.py      # /api/analysis/*
│   │   │   ├── portfolio.py     # /api/portfolio/*
│   │   │   ├── alerts.py        # /api/alerts/*
│   │   │   └── recommendations.py # /api/recommendations/*
│   │   ├── schemas.py           # Pydantic models (request/response)
│   │   └── dependencies.py      # Dependency injection
│   │
│   └── config.py                # Settings (pydantic-settings)
│
├── tests/
│   ├── unit/
│   │   ├── test_domain/
│   │   ├── test_analyzers/
│   │   └── test_services/
│   ├── integration/
│   │   ├── test_database/
│   │   └── test_api/
│   └── fixtures/
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml               # Dependencies (poetry)
└── README.md
```

---

## 3. Components

### 3.1 Data Ingestion Layer

**Purpose:** Fetch market data, financials, and news from external sources.

**Providers:**
- `YahooFinanceProvider` — Free, 15min delay, broad global coverage
- `AlphaVantageProvider` — Free tier (5 calls/min), real-time data
- `NewsScraper` — Playwright-based scraper for financial news headlines

**Data Collected:**
- **Prices:** Open, High, Low, Close, Volume (OHLCV)
- **Fundamentals:** P/E ratio, EPS, Revenue, Debt/Equity, Market Cap
- **News:** Headlines + summaries from Yahoo Finance, Reuters, Bloomberg
- **Dividends:** Yield, ex-dividend date

**Update Frequency:**
- Prices: every 15 minutes (market hours)
- Fundamentals: once daily (before market open)
- News: every 30 minutes

### 3.2 Analysis Engine

#### 3.2.1 Technical Analysis

**Indicators:**
- Trend: SMA(20), SMA(50), SMA(200), EMA(12), EMA(26)
- Momentum: RSI(14), MACD(12,26,9), Stochastic(14,3,3)
- Volatility: Bollinger(20,2), ATR(14)
- Volume: OBV, Volume Pattern
- Candlestick Patterns: Doji, Hammer, Engulfing

**Scoring (0-100):**
- Each indicator generates a signal: BUY (+1), HOLD (0), SELL (-1)
- Weighted average by indicator confidence
- Output: Technical score feeding into recommendation

#### 3.2.2 Fundamental Analysis

**Metrics:**
- Valuation: P/E, P/B, P/S, EV/EBITDA
- Profitability: ROE, ROA, Profit Margin
- Growth: Revenue Growth, EPS Growth
- Health: Debt/Equity, Current Ratio, Quick Ratio
- Dividends: Yield, Payout Ratio, Dividend Growth

**Scoring (0-100):**
- Each metric compared against sector/market average
- Classified as: Undervalued (+), Fairly Valued (0), Overvalued (-)
- Output: Fundamental score

#### 3.2.3 Sentiment Analysis

**Sources:**
- News headlines (Yahoo Finance, Reuters)
- Social media (Twitter/X, optional)
- Earnings call transcripts (when available)

**Method:**
1. Scrape recent headlines (last 24h)
2. Tokenize and clean text
3. Sentiment analysis: TextBlob (simple) or transformers (advanced)
4. Aggregate per stock

**Scoring (-1 to +1):**
- Negative < -0.3 → SELL signal
- Neutral between -0.3 and +0.3 → HOLD
- Positive > +0.3 → BUY signal

### 3.3 Recommendation Engine

**Algorithm:**
```python
def generate_recommendation(stock: Stock) -> Recommendation:
    technical = analyze_technical(stock)      # 0-100
    fundamental = analyze_fundamental(stock)   # 0-100
    sentiment = analyze_sentiment(stock)       # -1 to +1

    # Configurable weights (default: 40% technical, 40% fundamental, 20% sentiment)
    final_score = (
        technical * config.weight_technical +
        fundamental * config.weight_fundamental +
        (sentiment + 1) * 50 * config.weight_sentiment  # Normalize to 0-100
    )

    if final_score >= config.buy_threshold:   # default 70
        action = Action.BUY
        confidence = min(final_score / 100, 0.95)
    elif final_score <= config.sell_threshold: # default 30
        action = Action.SELL
        confidence = min((100 - final_score) / 100, 0.95)
    else:
        action = Action.HOLD
        confidence = 0.5

    return Recommendation(
        stock=stock,
        action=action,
        score=final_score,
        confidence=confidence,
        reasoning=build_reasoning(technical, fundamental, sentiment)
    )
```

### 3.4 Portfolio Tracker

**Model:**
- Portfolio (1 per user)
  - Position[] (stocks owned)
    - symbol: str
    - quantity: int
    - avg_buy_price: float
    - current_price: float (calculated)
  - Total Value: float (calculated)
  - Total P&L: float (calculated)
  - Allocation: dict (by sector/country)

**Endpoints:**
- `GET /api/portfolio` — Portfolio summary
- `POST /api/portfolio/positions` — Add position
- `PUT /api/portfolio/positions/{id}` — Update position
- `DELETE /api/portfolio/positions/{id}` — Remove position
- `GET /api/portfolio/performance` — Historical performance

### 3.5 Alert System

**Alert Types:**
- Price: "AAPL surpassed $200"
- Indicator: "TSLA RSI < 30 (oversold)"
- Recommendation: "BUY signal on MSFT (score: 85)"
- Portfolio: "Your portfolio dropped 5% today"
- News: "Negative news about GOOGL"

**Channels:**
- Email (SMTP via Gmail/SendGrid)
- Telegram Bot (free, instant)
- Dashboard (in-app notifications)

### 3.6 Dashboard (Frontend)

**Stack:** HTML + Tailwind CSS + HTMX (no React/Vue)

**Pages:**
- `/` — Main dashboard (portfolio summary + top recommendations)
- `/stocks` — Monitored stocks list
- `/stocks/{symbol}` — Stock detail (charts + analysis)
- `/recommendations` — All active recommendations
- `/portfolio` — Portfolio management
- `/alerts` — Alert configuration and history
- `/settings` — Weights, thresholds, notification settings

**Charts:** Chart.js or lightweight-charts (TradingView) for candlesticks and indicators.

---

## 4. Error Handling

### 4.1 Retry Strategy
- **Exponential backoff:** 3 attempts, wait 4s → 8s → 10s
- **Retry on:** ConnectionError, TimeoutError, HTTP 429 (rate limit)
- **Circuit breaker:** After 5 consecutive failures, wait 60s before retry

### 4.2 Graceful Degradation
- If sentiment analysis fails → use only technical + fundamental
- If Alpha Vantage fails → fallback to yfinance only
- If news scraping fails → skip sentiment, log warning

### 4.3 Logging
- Structured logging with `structlog`
- Log levels: DEBUG (development), INFO (normal ops), WARNING (degraded), ERROR (failure)
- Log all API calls, analysis results, and recommendation decisions

### 4.4 Error Handling by Layer
- **Infrastructure:** Retry + Circuit Breaker for external APIs
- **Application:** Log + graceful degradation
- **API:** HTTP 503 (degraded), HTTP 500 (unexpected error)
- **Database:** Transactions, rollback on error, connection pooling

---

## 5. Testing Strategy

### 5.1 Unit Tests
- Domain entities (Stock, Recommendation, Portfolio)
- Analyzers (technical indicators, fundamental scoring)
- Services (orchestration logic)

### 5.2 Integration Tests
- Database repositories (PostgreSQL via testcontainers)
- API endpoints (FastAPI TestClient)
- External API mocks (responses library)

### 5.3 Test Tools
- `pytest` — Test framework
- `pytest-asyncio` — Async test support
- `pytest-cov` — Coverage reports
- `factory_boy` — Test data factories
- `responses` — HTTP request mocking
- `testcontainers` — PostgreSQL in Docker for integration tests

### 5.4 Coverage Targets
- Domain + Application: 80%+
- Infrastructure: 60%+
- Overall: 70%+

---

## 6. Deployment

### 6.1 Local Development (MVP)
```yaml
services:
  app:
    build: .
    ports: ["8000:8000"]
    depends_on: [db, redis]
  db:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
  redis:
    image: redis:7-alpine
  scheduler:
    build: .
    command: python -m alpharadar.scheduler
    depends_on: [db, redis]
```

### 6.2 Cloud (Post-MVP)
- Railway ($5/mes) — easiest, git push deploy
- Fly.io ($0-5/mes) — more control, Docker native
- AWS ECS/Fargate ($20-50/mes) — production scale
- DigitalOcean ($12/mes) — simple VPS

### 6.3 CI/CD Pipeline
```
GitHub Actions:
1. Push → Lint (ruff) + Type Check (mypy) + Tests (pytest)
2. Merge to main → Build Docker image
3. Tag v* → Deploy to production
```

---

## 7. Configuration

```python
class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://localhost:5432/alpharadar"
    redis_url: str = "redis://localhost:6379"

    # API Keys
    yahoo_finance_api_key: str = ""
    alpha_vantage_api_key: str = ""
    telegram_bot_token: str = ""

    # Analysis weights
    weight_technical: float = 0.4
    weight_fundamental: float = 0.4
    weight_sentiment: float = 0.2

    # Thresholds
    buy_threshold: float = 70.0
    sell_threshold: float = 30.0

    # Scheduler intervals (seconds)
    price_update_interval: int = 900      # 15 min
    fundamental_update_interval: int = 86400  # 24h
    news_update_interval: int = 1800      # 30 min

    # Notification
    email_enabled: bool = False
    telegram_enabled: bool = False
```

---

## 8. Implementation Plan (3 Weeks)

### Week 1 — Foundations
- Day 1-2: Project setup, domain entities, database models
- Day 3-4: Data ingestion (yfinance + Alpha Vantage)
- Day 5: Technical analysis engine
- Day 6-7: Basic API + unit tests

### Week 2 — Core Features
- Day 8-9: Fundamental analysis
- Day 10-11: Sentiment analysis
- Day 12: Recommendation engine
- Day 13-14: Portfolio tracker + tests

### Week 3 — Polish
- Day 15-16: Alert system (email + Telegram)
- Day 17-18: Dashboard (HTMX + Tailwind)
- Day 19: Scheduler (APScheduler)
- Day 20-21: Docker compose + local deploy + documentation

---

## 9. Success Criteria

- [ ] Can fetch real-time market data from yfinance/Alpha Vantage
- [ ] Technical analysis calculates 10+ indicators correctly
- [ ] Fundamental analysis scores stocks based on financial metrics
- [ ] Sentiment analysis processes news headlines
- [ ] Recommendation engine combines all 3 analyses into actionable scores
- [ ] Portfolio tracker shows current holdings and P&L
- [ ] Alert system notifies via email/Telegram when thresholds are met
- [ ] Dashboard displays all data in a clean, readable interface
- [ ] All tests pass with 70%+ coverage
- [ ] Docker compose runs the full stack locally

---

## 10. Out of Scope (MVP)

- Automated trading (no broker integration yet)
- Machine learning models for prediction
- Backtesting engine
- Multi-user support (single user for now)
- Mobile app
- Real-time streaming data (WebSocket)
