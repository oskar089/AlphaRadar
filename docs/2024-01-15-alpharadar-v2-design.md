# AlphaRadar v2.0 - Design Document

**Date:** 2024-01-15  
**Status:** Approved  
**Author:** AlphaRadar Team

---

## Executive Summary

AlphaRadar v2.0 transforms the MVP stock analysis system into a fully-featured, production-ready platform with:

1. **Interactive Dashboard** - Streamlit-based visual analytics
2. **Smart Alerts** - Real-time notifications via Telegram
3. **Advanced Sentiment** - RSS + FinBERT hybrid analysis
4. **Automated Scheduler** - Celery-powered periodic tasks
5. **Persistent Storage** - PostgreSQL with dual-mode support

**Architecture:** Monolith Extended (FastAPI + Celery + Streamlit)

---

## 1. High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                            │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│    FastAPI      │   Celery Worker │   Celery Beat   │ Streamlit │
│    (API)        │   (Tasks)       │   (Scheduler)   │ (Dashboard)│
├─────────────────┴─────────────────┴─────────────────┴───────────┤
│                    PostgreSQL + Redis                            │
└─────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
src/alpharadar/
├── api/                    # FastAPI endpoints
│   ├── routes/
│   │   ├── alerts.py       # Alert CRUD
│   │   ├── dashboard.py    # Dashboard data
│   │   ├── portfolio.py    # Portfolio management
│   │   └── stocks.py       # Stock data
│   ├── schemas.py          # Pydantic models
│   └── main.py             # App factory
├── application/
│   ├── ports/
│   │   ├── alert.py        # Alert repository port
│   │   └── portfolio.py    # Portfolio repository port
│   └── services/
│       ├── alert.py        # Alert evaluation
│       ├── recommendation.py  # Analysis orchestration
│       └── sentiment.py    # Sentiment pipeline
├── dashboard/               # Streamlit app
│   ├── app.py              # Entry point
│   ├── pages/
│   │   ├── portfolio.py    # Portfolio view
│   │   ├── analysis.py     # Stock analysis
│   │   └── alerts.py       # Alert management
│   └── components/         # Reusable UI components
├── domain/
│   ├── entities/
│   │   ├── alert.py        # Alert entity
│   │   ├── portfolio.py    # Position entity
│   │   └── stock.py        # Stock entity
│   └── interfaces/
│       ├── analyzer.py     # Analyzer interfaces
│       └── notifier.py     # Notification interface
├── infrastructure/
│   ├── analyzers/
│   │   ├── fundamental.py  # Fundamental analysis
│   │   ├── sentiment.py    # Hybrid sentiment (RSS + FinBERT)
│   │   └── technical.py    # Technical indicators
│   ├── cache/
│   │   └── redis.py        # Redis cache
│   ├── database/
│   │   ├── connection.py   # Async SQLAlchemy
│   │   └── models.py       # ORM models
│   ├── data_providers/
│   │   └── yahoo_finance.py  # Yahoo Finance API
│   ├── notifications/
│   │   └── telegram.py     # Telegram bot
│   └── portfolio/
│       ├── in_memory.py    # In-memory (tests)
│       └── postgresql.py   # PostgreSQL adapter
├── worker/                  # Celery app
│   ├── __init__.py         # Celery config
│   ├── tasks.py            # Task definitions
│   └── schedules.py        # Beat schedule
└── config.py               # Settings
```

---

## 2. Dashboard (Streamlit)

### Pages

#### Portfolio Overview
- **Total Value Card**: Current portfolio value + daily change
- **Allocation Chart**: Pie chart by sector/stock
- **Positions Table**: Symbol, quantity, avg price, current price, P&L

#### Stock Analysis
- **Symbol Input**: Search bar with autocomplete
- **Price Chart**: Interactive line chart (Plotly) with 30-day history
- **Analysis Gauges**: Technical, Fundamental, Sentiment scores
- **Recommendation Card**: BUY/SELL/HOLD with confidence

#### Alert Management
- **Create Alert Form**: Type, condition, threshold
- **Active Alerts Table**: List with status
- **Test Button**: Preview alert against current data

### Components

```python
# dashboard/components/charts.py
import plotly.graph_objects as go

def create_price_chart(data: pd.DataFrame) -> go.Figure:
    """Interactive price chart with volume overlay."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=data.index, y=data['close'], name='Price'))
    fig.add_trace(go.Bar(x=data.index, y=data['volume'], name='Volume'), 
                  secondary_y=True)
    return fig

def create_gauge(value: float, title: str) -> go.Figure:
    """Score gauge (0-100)."""
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title}
    ))
```

### API Client

```python
# dashboard/api_client.py
import httpx
from alpharadar.config import settings

class AlphaRadarClient:
    def __init__(self):
        self.base_url = f"http://{settings.api_host}:{settings.api_port}"
    
    async def get_portfolio(self) -> list[Position]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/portfolio")
            return resp.json()
    
    async def analyze_stock(self, symbol: str) -> Recommendation:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/api/recommendations/{symbol}")
            return resp.json()
```

### Run Commands

```bash
# Development
streamlit run src/alpharadar/dashboard/app.py --port 8501

# Production (Docker)
docker compose up dashboard
```

---

## 3. Alerts System

### Alert Types

| Type | Condition | Example |
|------|-----------|---------|
| `price` | Price crosses threshold | AAPL > $160.00 |
| `rsi` | RSI overbought/oversold | MSFT RSI < 30 |
| `macd` | MACD crossover | GOOGL MACD cross |
| `volume` | Volume spike | AAPL volume > 2x avg |
| `sentiment` | Sentiment shift | TSLA sentiment < -0.5 |
| `recommendation` | Buy/Sell signal | Any BUY/SELL |

### Domain Model

```python
# domain/entities/alert.py
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class AlertType(Enum):
    PRICE = "price"
    RSI = "rsi"
    MACD = "macd"
    VOLUME = "volume"
    SENTIMENT = "sentiment"
    RECOMMENDATION = "recommendation"

class Condition(Enum):
    ABOVE = ">"
    BELOW = "<"
    CROSS_ABOVE = "cross_above"
    CROSS_BELOW = "cross_below"

@dataclass
class Alert:
    id: int
    symbol: str
    alert_type: AlertType
    condition: Condition
    threshold: float | None
    is_active: bool
    last_triggered: datetime | None
    created_at: datetime
```

### Evaluator

```python
# infrastructure/evaluators/alert_evaluator.py
class AlertEvaluator:
    async def evaluate(self, alert: Alert, stock_data: StockData) -> bool:
        match alert.alert_type:
            case AlertType.PRICE:
                return self._check_price(stock_data.current_price, alert)
            case AlertType.RSI:
                return self._check_rsi(stock_data.rsi, alert)
            case AlertType.VOLUME:
                return self._check_volume(stock_data.volume, alert)
            case AlertType.SENTIMENT:
                return self._check_sentiment(stock_data.sentiment, alert)
            case AlertType.RECOMMENDATION:
                return self._check_recommendation(stock_data.recommendation, alert)
        return False
    
    def _check_sentiment(self, sentiment: float, alert: Alert) -> bool:
        match alert.condition:
            case Condition.ABOVE:
                return sentiment > alert.threshold
            case Condition.BELOW:
                return sentiment < alert.threshold
        return False
    
    def _check_recommendation(self, recommendation: str, alert: Alert) -> bool:
        if alert.condition == Condition.ABOVE:
            return recommendation == "BUY"
        elif alert.condition == Condition.BELOW:
            return recommendation == "SELL"
        return False
    
    def _check_price(self, current: float, alert: Alert) -> bool:
        match alert.condition:
            case Condition.ABOVE:
                return current > alert.threshold
            case Condition.BELOW:
                return current < alert.threshold
```

### Telegram Notifier

```python
# infrastructure/notifications/telegram.py
import httpx

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    async def send(self, message: str) -> None:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            })

# Message format:
# 🔔 ALERT: AAPL
# Price crossed above $160.00
# Current: $162.50 (+1.56%)
# Time: 2024-01-15 14:30 UTC
```

### API Endpoints

```python
# api/routes/alerts.py
router = APIRouter()

@router.get("/")
async def list_alerts() -> list[AlertResponse]

@router.post("/")
async def create_alert(alert: CreateAlertRequest) -> AlertResponse

@router.put("/{alert_id}")
async def update_alert(alert_id: int, alert: UpdateAlertRequest) -> AlertResponse

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int) -> None

@router.post("/{alert_id}/test")
async def test_alert(alert_id: int) -> AlertTestResponse
```

---

## 4. Sentiment Analysis

### Architecture: RSS + FinBERT

```
┌─────────────────────────────────────────────────────────┐
│                   Sentiment Pipeline                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │ RSS Feeds   │───▶│ FinBERT     │───▶│ Aggregator  │  │
│  │ (Volume)    │    │ (Accuracy)  │    │             │  │
│  └─────────────┘    └─────────────┘    └──────┬──────┘  │
│                                               │         │
│  ┌─────────────┐    ┌─────────────┐           │         │
│  │ Fallback    │───▶│ TextBlob    │───────────┘         │
│  │ (Fallback)  │    │ (Quick)     │                     │
│  └─────────────┘    └─────────────┘                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### RSS Sources

```python
# infrastructure/sentiment/rss_fetcher.py
RSS_FEEDS = {
    "yahoo_finance": "https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}",
    "google_news": "https://news.google.com/rss/search?q={symbol}+stock",
    "reuters_business": "https://www.reuters.com/arc/outboundfeeds/v3/all/rss.xml",
}

class RSSNewsFetcher:
    async def fetch(self, symbol: str, limit: int = 10) -> list[NewsArticle]:
        articles = []
        for source, url_template in RSS_FEEDS.items():
            url = url_template.format(symbol=symbol)
            feed = await self._parse_feed(url)
            articles.extend(feed[:limit])
        return articles[:limit]
```

### FinBERT

```python
# infrastructure/sentiment/finbert.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class FinBERTAnalyzer:
    def __init__(self):
        self.model_name = "ProsusAI/finbert"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
    
    async def analyze(self, texts: list[str]) -> list[float]:
        results = []
        for text in texts:
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            sentiment = probs[0][0] - probs[0][1]  # positive - negative
            results.append(float(sentiment))
        return results
```

### Hybrid Analyzer

```python
# infrastructure/analyzers/sentiment.py
class HybridSentimentAnalyzer(SentimentAnalyzer):
    def __init__(self, rss_fetcher: RSSNewsFetcher, finbert: FinBERTAnalyzer):
        self.rss = rss_fetcher
        self.finbert = finbert
    
    async def analyze(self, symbol: str) -> float:
        # 1. Fetch news from RSS
        articles = await self.rss.fetch(symbol, limit=10)
        
        if not articles:
            return 0.0
        
        # 2. Analyze with FinBERT
        texts = [f"{a.title}. {a.summary}" for a in articles]
        sentiments = await self.finbert.analyze(texts)
        
        # 3. Weighted average (recent news weighted more)
        weights = [1.0 / (i + 1) for i in range(len(sentiments))]
        weighted_sentiment = sum(s * w for s, w in zip(sentiments, weights))
        normalized = weighted_sentiment / sum(weights)
        
        # 4. Normalize to [-1, 1]
        return max(-1.0, min(1.0, normalized))
```

### Dependencies

```toml
[project.optional-dependencies]
sentiment = [
    "feedparser>=6.0.0",
    "transformers>=4.40.0",
    "torch>=2.0.0",
    "sentencepiece>=0.2.0",
]
```

---

## 5. Scheduler (Celery + Redis)

### Beat Schedule

```python
# worker/tasks.py
from celery import Celery
from celery.schedules import crontab

app = Celery('alpharadar')
app.config_from_object('alpharadar.config.settings')

app.conf.beat_schedule = {
    'update-prices': {
        'task': 'alpharadar.worker.tasks.update_stock_prices',
        'schedule': crontab(minute='*/15'),
    },
    'update-sentiment': {
        'task': 'alpharadar.worker.tasks.update_sentiment_scores',
        'schedule': crontab(minute=0),
    },
    'update-fundamentals': {
        'task': 'alpharadar.worker.tasks.update_fundamental_scores',
        'schedule': crontab(hour=0),
    },
    'evaluate-alerts': {
        'task': 'alpharadar.worker.tasks.evaluate_all_alerts',
        'schedule': crontab(minute='*/5'),
    },
    'daily-report': {
        'task': 'alpharadar.worker.tasks.generate_daily_report',
        'schedule': crontab(hour=9, minute=0, day_of_week='1-5'),
    },
}
```

### Tasks

```python
@app.task(bind=True, max_retries=3)
def update_stock_prices(self):
    """Update prices for all active positions."""
    try:
        symbols = get_active_symbols()
        for symbol in symbols:
            stock_data = yahoo_provider.get_stock(symbol)
            update_position_price(symbol, stock_data.current_price)
            cache.delete(f"stock:{symbol}")
        logger.info("prices_updated", count=len(symbols))
    except Exception as exc:
        logger.error("price_update_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=60)

@app.task(bind=True, max_retries=3)
def evaluate_all_alerts(self):
    """Evaluate all active alerts against current data."""
    try:
        alerts = get_active_alerts()
        alerts_by_symbol = group_by_symbol(alerts)
        
        for symbol, symbol_alerts in alerts_by_symbol.items():
            stock_data = yahoo_provider.get_stock(symbol)
            for alert in symbol_alerts:
                if evaluator.evaluate(alert, stock_data):
                    trigger_alert(alert, stock_data)
        
        logger.info("alerts_evaluated", count=len(alerts))
    except Exception as exc:
        logger.error("alert_evaluation_failed", error=str(exc))
        raise self.retry(exc=exc, countdown=30)

@app.task
def generate_daily_report():
    """Generate and send daily portfolio report."""
    portfolio_summary = calculate_daily_summary()
    top_gainers = get_top_gainers(limit=3)
    top_losers = get_top_losers(limit=3)
    message = format_daily_report(portfolio_summary, top_gainers, top_losers)
    telegram_notifier.send(message)
```

### Docker Compose

```yaml
services:
  worker:
    build: .
    command: celery -A alpharadar.worker worker --loglevel=info --concurrency=2
    environment:
      DATABASE_URL: "${DATABASE_URL}"
      REDIS_URL: "${REDIS_URL}"
    depends_on:
      - db
      - redis
  
  beat:
    build: .
    command: celery -A alpharadar.worker beat --loglevel=info
    environment:
      REDIS_URL: "${REDIS_URL}"
    depends_on:
      - redis
```

---

## 6. Persistence (PostgreSQL Dual Mode)

### Configuration

```python
# config.py
class Settings(BaseSettings):
    portfolio_persistence: str = "memory"  # "postgresql" | "memory"
    # ...
```

### Factory

```python
# infrastructure/portfolio/__init__.py
def create_portfolio_repository() -> PortfolioRepository:
    if settings.portfolio_persistence == "postgresql":
        from alpharadar.infrastructure.portfolio.postgresql import (
            PostgreSQLPortfolioRepository,
        )
        return PostgreSQLPortfolioRepository()
    else:
        from alpharadar.infrastructure.portfolio.in_memory import (
            InMemoryPortfolioRepository,
        )
        return InMemoryPortfolioRepository()
```

### PostgreSQL Repository

```python
# infrastructure/portfolio/postgresql.py
class PostgreSQLPortfolioRepository(PortfolioRepository):
    async def list(self) -> list[StoredPosition]:
        async with get_async_session() as session:
            query = (
                select(PositionModel, StockModel.symbol)
                .join(StockModel, PositionModel.stock_id == StockModel.id)
            )
            result = await session.execute(query)
            return [
                StoredPosition(
                    id=row.PositionModel.id,
                    symbol=row.symbol,
                    quantity=row.PositionModel.quantity,
                    avg_buy_price=row.PositionModel.avg_buy_price,
                    current_price=row.PositionModel.current_price,
                )
                for row in result.all()
            ]
    
    async def add(
        self, symbol: str, quantity: int, avg_buy_price: float
    ) -> StoredPosition:
        async with get_async_session() as session:
            stock = await self._get_or_create_stock(session, symbol)
            position = PositionModel(
                stock_id=stock.id,
                quantity=quantity,
                avg_buy_price=avg_buy_price,
                current_price=avg_buy_price,
            )
            session.add(position)
            await session.commit()
            await session.refresh(position)
            return StoredPosition(
                id=position.id,
                symbol=symbol,
                quantity=quantity,
                avg_buy_price=avg_buy_price,
                current_price=avg_buy_price,
            )
    
    async def delete(self, position_id: int) -> bool:
        async with get_async_session() as session:
            query = select(PositionModel).where(PositionModel.id == position_id)
            result = await session.execute(query)
            position = result.scalar_one_or_none()
            if position is None:
                return False
            await session.delete(position)
            await session.commit()
            return True
```

### Test Dual Mode

```python
# tests/conftest.py
@pytest.fixture(params=["memory", "postgresql"])
def portfolio_repository(request):
    if request.param == "memory":
        from alpharadar.infrastructure.portfolio.in_memory import (
            InMemoryPortfolioRepository,
        )
        return InMemoryPortfolioRepository()
    else:
        from alpharadar.infrastructure.portfolio.postgresql import (
            PostgreSQLPortfolioRepository,
        )
        return PostgreSQLPortfolioRepository()
```

---

## 7. Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "redis>=5.0.0",
    "celery[redis]>=5.3.0",
    "pydantic-settings>=2.0.0",
    "structlog>=24.0.0",
    "httpx>=0.27.0",
]

[project.optional-dependencies]
dashboard = [
    "streamlit>=1.35.0",
    "plotly>=5.22.0",
    "pandas>=2.2.0",
]

sentiment = [
    "feedparser>=6.0.0",
    "transformers>=4.40.0",
    "torch>=2.0.0",
    "sentencepiece>=0.2.0",
]

dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.3.0",
    "mypy>=1.9.0",
]
```

---

## 8. Docker Compose (Final)

```yaml
services:
  app:
    build: .
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      DATABASE_URL: "postgresql+asyncpg://${ALPHARADAR_DB_USER}:${ALPHARADAR_DB_PASSWORD}@db:5432/alpharadar"
      REDIS_URL: "redis://:${ALPHARADAR_REDIS_PASSWORD}@redis:6379"
      PORTFOLIO_PERSISTENCE: "postgresql"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
  
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${ALPHARADAR_DB_USER}
      POSTGRES_PASSWORD: ${ALPHARADAR_DB_PASSWORD}
      POSTGRES_DB: alpharadar
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${ALPHARADAR_DB_USER} -d alpharadar"]
      interval: 5s
      timeout: 5s
      retries: 5
  
  redis:
    image: redis:7-alpine
    command: ["redis-server", "--requirepass", "${ALPHARADAR_REDIS_PASSWORD}"]
    ports:
      - "127.0.0.1:6379:6379"
    healthcheck:
      test: ["CMD-SHELL", "redis-cli -a '${ALPHARADAR_REDIS_PASSWORD}' ping | grep PONG"]
      interval: 5s
      timeout: 5s
      retries: 5
  
  worker:
    build: .
    command: celery -A alpharadar.worker worker --loglevel=info --concurrency=2
    environment:
      DATABASE_URL: "postgresql+asyncpg://${ALPHARADAR_DB_USER}:${ALPHARADAR_DB_PASSWORD}@db:5432/alpharadar"
      REDIS_URL: "redis://:${ALPHARADAR_REDIS_PASSWORD}@redis:6379"
    depends_on:
      - db
      - redis
  
  beat:
    build: .
    command: celery -A alpharadar.worker beat --loglevel=info
    environment:
      REDIS_URL: "redis://:${ALPHARADAR_REDIS_PASSWORD}@redis:6379"
    depends_on:
      - redis
  
  dashboard:
    build: .
    command: streamlit run src/alpharadar/dashboard/app.py --server.port=8501 --server.address=0.0.0.0
    ports:
      - "127.0.0.1:8501:8501"
    environment:
      API_HOST: "app"
      API_PORT: "8000"
    depends_on:
      - app

volumes:
  pgdata:
```

---

## 9. Testing Strategy

### Unit Tests
- Domain entities
- Alert evaluator
- Sentiment analyzer
- Portfolio repository (both modes)

### Integration Tests
- API endpoints
- Celery tasks
- Database operations

### E2E Tests
- Dashboard workflows
- Alert creation to notification flow

```bash
# Run tests
pytest

# With coverage
pytest --cov=alpharadar --cov-report=html

# With dual mode
pytest --portfolio-mode=memory
pytest --portfolio-mode=postgresql
```

---

## 10. Sub-Project Decomposition

### Overview

AlphaRadar v2.0 is decomposed into **3 independent sub-projects**, each with its own spec → plan → implementation cycle.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sub-Project Dependencies                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                             │
│  │ Sub-project 1   │                                             │
│  │ Foundation      │                                             │
│  │ (Persistence +  │                                             │
│  │  Scheduler)     │                                             │
│  └────────┬────────┘                                             │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ Sub-project 2   │    │ Sub-project 3   │                     │
│  │ Notifications   │    │ Visualization   │                     │
│  │ (Alerts +       │    │ (Dashboard +    │                     │
│  │  Telegram)      │    │  Sentiment)     │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

### Sub-project 1: Foundation (Persistence + Scheduler)

**Goal:** Set up PostgreSQL persistence and Celery scheduler as the base infrastructure.

**Scope:**
- PostgreSQL portfolio repository (dual mode)
- Alembic migrations
- Celery worker setup
- Beat schedule configuration
- Basic price update task

**Dependencies:** None (foundation)

**Deliverables:**
- `infrastructure/portfolio/postgresql.py`
- `alembic/` directory with migrations
- `worker/__init__.py`, `worker/tasks.py`, `worker/schedules.py`
- Updated `docker-compose.yml` with worker + beat services
- Updated `config.py` with `portfolio_persistence` setting

**Estimated Effort:** 2-3 days

**Acceptance Criteria:**
- [ ] Portfolio data persists in PostgreSQL
- [ ] In-memory mode still works for tests
- [ ] Celery worker starts and connects to Redis
- [ ] Beat schedule triggers price updates every 15 minutes
- [ ] Docker Compose runs all 5 services (app, db, redis, worker, beat)

---

### Sub-project 2: Notifications (Alerts + Telegram)

**Goal:** Implement alert system with Telegram notifications.

**Scope:**
- Alert domain entity
- Alert CRUD API endpoints
- Alert evaluator (price, RSI, MACD, volume, sentiment, recommendation)
- Telegram notifier
- Celery task for alert evaluation

**Dependencies:** Sub-project 1 (for PostgreSQL + Celery)

**Deliverables:**
- `domain/entities/alert.py`
- `application/ports/alert.py`
- `application/services/alert.py`
- `infrastructure/evaluators/alert_evaluator.py`
- `infrastructure/notifications/telegram.py`
- `api/routes/alerts.py`
- `worker/tasks.py` (alert evaluation task)

**Estimated Effort:** 2-3 days

**Acceptance Criteria:**
- [ ] Create, read, update, delete alerts via API
- [ ] Alerts evaluate correctly against stock data
- [ ] Telegram notifications send on alert trigger
- [ ] Alert evaluation runs every 5 minutes via Celery
- [ ] Test endpoint validates alert against current data

---

### Sub-project 3: Visualization (Dashboard + Sentiment)

**Goal:** Build interactive Streamlit dashboard and improve sentiment analysis.

**Scope:**
- Streamlit dashboard app
- Portfolio overview page
- Stock analysis page
- Alert management page
- RSS news fetcher
- FinBERT sentiment analyzer
- Hybrid sentiment pipeline

**Dependencies:** Sub-project 1 + Sub-project 2 (for data + alerts)

**Deliverables:**
- `dashboard/app.py`
- `dashboard/pages/portfolio.py`
- `dashboard/pages/analysis.py`
- `dashboard/pages/alerts.py`
- `dashboard/components/charts.py`
- `dashboard/api_client.py`
- `infrastructure/sentiment/rss_fetcher.py`
- `infrastructure/sentiment/finbert.py`
- Updated `infrastructure/analyzers/sentiment.py`

**Estimated Effort:** 3-4 days

**Acceptance Criteria:**
- [ ] Dashboard shows portfolio value and positions
- [ ] Interactive charts with Plotly (price history, allocation)
- [ ] Stock analysis page with gauges and recommendation
- [ ] Alert management page (create, list, test)
- [ ] RSS fetcher retrieves news from multiple sources
- [ ] FinBERT analyzes sentiment accurately
- [ ] Hybrid analyzer combines RSS + FinBERT

---

### Implementation Order

```
Week 1: Sub-project 1 (Foundation)
  ├── Day 1-2: PostgreSQL repository + migrations
  └── Day 3: Celery worker + beat schedule

Week 2: Sub-project 2 (Notifications)
  ├── Day 4-5: Alert domain + CRUD API
  └── Day 6-7: Evaluator + Telegram notifier

Week 3: Sub-project 3 (Visualization)
  ├── Day 8-9: Dashboard pages + charts
  ├── Day 10-11: RSS + FinBERT sentiment
  └── Day 12: Integration + polish
```

---

### Sub-Project Specs

Each sub-project will have its own detailed spec document:

1. **`docs/2024-01-15-sub1-foundation-spec.md`** - PostgreSQL + Celery details
2. **`docs/2024-01-15-sub2-notifications-spec.md`** - Alerts + Telegram details
3. **`docs/2024-01-15-sub3-visualization-spec.md`** - Dashboard + Sentiment details

---

## 11. Migration Plan (Original)

### Phase 1: Foundation
1. Set up Celery worker
2. Implement PostgreSQL portfolio repository
3. Add Alembic migrations

### Phase 2: Core Features
1. Implement alert system
2. Build Telegram notifier
3. Create dashboard pages

### Phase 3: Advanced
1. Implement hybrid sentiment
2. Add Celery beat schedules
3. Polish dashboard

### Phase 4: Production
1. Add monitoring
2. Optimize performance
3. Documentation

---

## 12. Open Questions

- [ ] Should we add rate limiting to Yahoo Finance calls?
- [ ] Do we need a separate worker for heavy ML tasks (FinBERT)?
- [ ] Should dashboard auto-refresh or manual refresh?

---

## 13. Appendix

### Environment Variables

```bash
# Database
ALPHARADAR_DB_USER=postgres
ALPHARADAR_DB_PASSWORD=secret

# Redis
ALPHARADAR_REDIS_PASSWORD=secret

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=123456789

# Portfolio
PORTFOLIO_PERSISTENCE=postgresql
```

### API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health/live` | Health check |
| GET | `/api/stocks/{symbol}` | Get stock data |
| GET | `/api/recommendations/{symbol}` | Get recommendation |
| GET | `/api/portfolio` | List positions |
| POST | `/api/portfolio/positions` | Add position |
| DELETE | `/api/portfolio/positions/{id}` | Remove position |
| GET | `/api/alerts` | List alerts |
| POST | `/api/alerts` | Create alert |
| PUT | `/api/alerts/{id}` | Update alert |
| DELETE | `/api/alerts/{id}` | Delete alert |
| POST | `/api/alerts/{id}/test` | Test alert |
| GET | `/api/worker/status` | Worker status |

---

**Document Version:** 1.0  
**Last Updated:** 2024-01-15  
**Status:** Approved for Implementation