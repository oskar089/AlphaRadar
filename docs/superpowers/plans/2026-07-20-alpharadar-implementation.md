# AlphaRadar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a semi-autonomous stock analysis system that combines technical, fundamental, and sentiment analysis to generate buy/hold/sell recommendations for global markets.

**Architecture:** Monolith Python with Clean Architecture (domain → application → infrastructure → API). Domain layer has zero dependencies. Infrastructure implements domain interfaces. API exposes application services.

**Tech Stack:** Python 3.12+, FastAPI, PostgreSQL 16, Redis 7, pandas, pandas-ta, yfinance, TextBlob, SQLAlchemy 2.0, Pydantic, HTMX, Tailwind CSS, Docker Compose

## Global Constraints

- Python 3.12+ (pyproject.toml requires-python = ">=3.12")
- All domain entities are dataclasses or Pydantic models — no ORM in domain
- Tests use pytest + pytest-asyncio; coverage target 70%+ overall
- Docker Compose for local development (PostgreSQL 16, Redis 7)
- No automated trading in MVP — recommendations only
- Single-user system — no auth in MVP
- Structured logging with structlog
- All external API calls use retry + circuit breaker (tenacity)

---

## Phase 1: Foundation (Days 1-2)

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/alpharadar/__init__.py`
- Create: `src/alpharadar/config.py`
- Create: `src/alpharadar/domain/__init__.py`
- Create: `src/alpharadar/domain/entities/__init__.py`
- Create: `src/alpharadar/domain/interfaces/__init__.py`
- Create: `src/alpharadar/application/__init__.py`
- Create: `src/alpharadar/application/services/__init__.py`
- Create: `src/alpharadar/application/dto/__init__.py`
- Create: `src/alpharadar/infrastructure/__init__.py`
- Create: `src/alpharadar/infrastructure/data_providers/__init__.py`
- Create: `src/alpharadar/infrastructure/analyzers/__init__.py`
- Create: `src/alpharadar/infrastructure/database/__init__.py`
- Create: `src/alpharadar/infrastructure/cache/__init__.py`
- Create: `src/alpharadar/infrastructure/notifications/__init__.py`
- Create: `src/alpharadar/api/__init__.py`
- Create: `src/alpharadar/api/routes/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/test_domain/__init__.py`
- Create: `tests/integration/__init__.py`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `README.md`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "alpharadar"
version = "0.1.0"
description = "Semi-autonomous stock analysis and recommendation system"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "redis[hiredis]>=5.0.0",
    "pandas>=2.2.0",
    "pandas-ta>=0.3.14b1",
    "yfinance>=0.2.40",
    "textblob>=0.18.0",
    "tenacity>=8.0.0",
    "structlog>=24.0.0",
    "httpx>=0.27.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "pytest-env>=1.0.0",
    "factory-boy>=3.0.0",
    "ruff>=0.5.0",
    "mypy>=1.10.0",
]

[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "SIM"]

[tool.mypy]
python_version = "3.12"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
env = [
    "DATABASE_URL=postgresql+asyncpg://test:test@localhost:5432/alpharadar_test",
    "REDIS_URL=redis://localhost:6379/1",
]
```

- [ ] **Step 2: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/alpharadar"
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
    price_update_interval: int = 900  # 15 min
    fundamental_update_interval: int = 86400  # 24h
    news_update_interval: int = 1800  # 30 min

    # Notification
    email_enabled: bool = False
    telegram_enabled: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 3: Create .env.example**

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/alpharadar
REDIS_URL=redis://localhost:6379
YAHOO_FINANCE_API_KEY=
ALPHA_VANTAGE_API_KEY=
TELEGRAM_BOT_TOKEN=
WEIGHT_TECHNICAL=0.4
WEIGHT_FUNDAMENTAL=0.4
WEIGHT_SENTIMENT=0.2
BUY_THRESHOLD=70.0
SELL_THRESHOLD=30.0
EMAIL_ENABLED=false
TELEGRAM_ENABLED=false
```

- [ ] **Step 4: Create .gitignore**

```
__pycache__/
*.py[cod]
*$py.class
.env
*.egg-info/
dist/
build/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
*.db
*.sqlite3
```

- [ ] **Step 5: Create all __init__.py files**

Create empty `__init__.py` in all directories listed above.

- [ ] **Step 6: Verify project structure**

Run: `find src -type f | sort`
Expected: All directories and `__init__.py` files exist.

- [ ] **Step 7: Commit**

```bash
git init
git add .
git commit -m "feat: scaffold AlphaRadar project structure"
```

---

### Task 2: Domain Entities

**Files:**
- Create: `src/alpharadar/domain/entities/stock.py`
- Create: `src/alpharadar/domain/entities/analysis.py`
- Create: `src/alpharadar/domain/entities/recommendation.py`
- Create: `src/alpharadar/domain/entities/portfolio.py`
- Create: `src/alpharadar/domain/entities/alert.py`
- Create: `tests/unit/test_domain/test_stock.py`
- Create: `tests/unit/test_domain/test_recommendation.py`
- Create: `tests/unit/test_domain/test_portfolio.py`

**Interfaces:**
- Produces: All domain entities used by application services and infrastructure

- [ ] **Step 1: Write failing tests for Stock entity**

```python
# tests/unit/test_domain/test_stock.py
from datetime import datetime
from alpharadar.domain.entities.stock import Stock, OHLCV, StockInfo


def test_stock_creation():
    stock = Stock(symbol="AAPL", name="Apple Inc.", exchange="NASDAQ")
    assert stock.symbol == "AAPL"
    assert stock.name == "Apple Inc."


def test_ohlcv_creation():
    candle = OHLCV(
        timestamp=datetime(2024, 1, 15, 10, 0),
        open=185.0,
        high=187.5,
        low=184.0,
        close=186.2,
        volume=50000000,
    )
    assert candle.close == 186.2
    assert candle.volume == 50000000


def test_stock_info_creation():
    info = StockInfo(
        symbol="AAPL",
        pe_ratio=28.5,
        eps=6.42,
        market_cap=2_900_000_000_000,
        revenue=394_000_000_000,
        debt_to_equity=1.8,
        dividend_yield=0.005,
    )
    assert info.pe_ratio == 28.5
    assert info.market_cap == 2_900_000_000_000
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_domain/test_stock.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'alpharadar'`

- [ ] **Step 3: Implement Stock entity**

```python
# src/alpharadar/domain/entities/stock.py
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class OHLCV:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class StockInfo:
    symbol: str
    pe_ratio: float | None = None
    eps: float | None = None
    market_cap: float | None = None
    revenue: float | None = None
    debt_to_equity: float | None = None
    dividend_yield: float | None = None
    sector: str | None = None
    industry: str | None = None


@dataclass
class Stock:
    symbol: str
    name: str
    exchange: str
    info: StockInfo | None = None
    history: list[OHLCV] = field(default_factory=list)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_domain/test_stock.py -v`
Expected: PASS

- [ ] **Step 5: Write failing tests for Recommendation entity**

```python
# tests/unit/test_domain/test_recommendation.py
from alpharadar.domain.entities.recommendation import (
    Recommendation,
    Action,
    AnalysisScores,
)


def test_analysis_scores_creation():
    scores = AnalysisScores(technical=75.0, fundamental=60.0, sentiment=0.3)
    assert scores.technical == 75.0
    assert scores.final_score is None  # Not calculated yet


def test_recommendation_creation():
    rec = Recommendation(
        symbol="AAPL",
        action=Action.BUY,
        score=78.5,
        confidence=0.82,
        reasoning="Strong technicals, solid fundamentals, positive sentiment",
    )
    assert rec.action == Action.BUY
    assert rec.score == 78.5


def test_action_enum():
    assert Action.BUY.value == "BUY"
    assert Action.SELL.value == "SELL"
    assert Action.HOLD.value == "HOLD"
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `pytest tests/unit/test_domain/test_recommendation.py -v`
Expected: FAIL

- [ ] **Step 7: Implement Recommendation entity**

```python
# src/alpharadar/domain/entities/recommendation.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class AnalysisScores:
    technical: float  # 0-100
    fundamental: float  # 0-100
    sentiment: float  # -1 to +1
    final_score: float | None = None


@dataclass
class Recommendation:
    symbol: str
    action: Action
    score: float
    confidence: float
    reasoning: str
    scores: AnalysisScores | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `pytest tests/unit/test_domain/test_recommendation.py -v`
Expected: PASS

- [ ] **Step 9: Write failing tests for Portfolio entity**

```python
# tests/unit/test_domain/test_portfolio.py
from alpharadar.domain.entities.portfolio import Portfolio, Position


def test_position_creation():
    pos = Position(
        symbol="AAPL",
        quantity=10,
        avg_buy_price=185.0,
        current_price=190.0,
    )
    assert pos.quantity == 10
    assert pos.unrealized_pnl == 50.0  # (190 - 185) * 10


def test_portfolio_creation():
    portfolio = Portfolio(name="My Portfolio")
    assert portfolio.name == "My Portfolio"
    assert portfolio.total_value == 0.0


def test_portfolio_add_position():
    portfolio = Portfolio(name="Test")
    pos = Position(symbol="AAPL", quantity=10, avg_buy_price=185.0, current_price=190.0)
    portfolio.positions.append(pos)
    assert len(portfolio.positions) == 1
    assert portfolio.total_value == 1900.0  # 10 * 190
```

- [ ] **Step 10: Run tests to verify they fail**

Run: `pytest tests/unit/test_domain/test_portfolio.py -v`
Expected: FAIL

- [ ] **Step 11: Implement Portfolio entity**

```python
# src/alpharadar/domain/entities/portfolio.py
from dataclasses import dataclass, field
from datetime import datetime


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
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_value(self) -> float:
        return sum(p.market_value for p in self.positions)

    @property
    def total_pnl(self) -> float:
        return sum(p.unrealized_pnl for p in self.positions)
```

- [ ] **Step 12: Run tests to verify they pass**

Run: `pytest tests/unit/test_domain/test_portfolio.py -v`
Expected: PASS

- [ ] **Step 13: Commit**

```bash
git add src/alpharadar/domain/ tests/unit/test_domain/
git commit -m "feat(domain): add Stock, Recommendation, and Portfolio entities"
```

---

### Task 3: Domain Interfaces (Ports)

**Files:**
- Create: `src/alpharadar/domain/interfaces/data_provider.py`
- Create: `src/alpharadar/domain/interfaces/analyzer.py`
- Create: `src/alpharadar/domain/interfaces/notifier.py`
- Create: `tests/unit/test_domain/test_interfaces.py`

**Interfaces:**
- Consumes: Domain entities from Task 2
- Produces: Abstract interfaces implemented by infrastructure layer

- [ ] **Step 1: Write failing tests for interfaces**

```python
# tests/unit/test_domain/test_interfaces.py
import pytest
from alpharadar.domain.interfaces.data_provider import DataProvider
from alpharadar.domain.interfaces.analyzer import TechnicalAnalyzer, FundamentalAnalyzer, SentimentAnalyzer
from alpharadar.domain.interfaces.notifier import Notifier


def test_data_provider_is_abstract():
    with pytest.raises(TypeError):
        DataProvider()


def test_notifier_is_abstract():
    with pytest.raises(TypeError):
        Notifier()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_domain/test_interfaces.py -v`
Expected: FAIL

- [ ] **Step 3: Implement interfaces**

```python
# src/alpharadar/domain/interfaces/data_provider.py
from abc import ABC, abstractmethod
from alpharadar.domain.entities.stock import Stock, OHLCV, StockInfo


class DataProvider(ABC):
    @abstractmethod
    async def get_stock(self, symbol: str) -> Stock:
        """Fetch stock metadata."""

    @abstractmethod
    async def get_history(self, symbol: str, period: str = "1y") -> list[OHLCV]:
        """Fetch historical OHLCV data."""

    @abstractmethod
    async def get_stock_info(self, symbol: str) -> StockInfo:
        """Fetch fundamental stock information."""
```

```python
# src/alpharadar/domain/interfaces/analyzer.py
from abc import ABC, abstractmethod
from alpharadar.domain.entities.stock import Stock, StockInfo
from alpharadar.domain.entities.recommendation import AnalysisScores


class TechnicalAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, stock: Stock) -> float:
        """Return technical score 0-100."""


class FundamentalAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, info: StockInfo) -> float:
        """Return fundamental score 0-100."""


class SentimentAnalyzer(ABC):
    @abstractmethod
    async def analyze(self, symbol: str) -> float:
        """Return sentiment score -1 to +1."""
```

```python
# src/alpharadar/domain/interfaces/notifier.py
from abc import ABC, abstractmethod
from alpharadar.domain.entities.recommendation import Recommendation


class Notifier(ABC):
    @abstractmethod
    async def send(self, recommendation: Recommendation) -> bool:
        """Send recommendation notification. Returns True if successful."""
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_domain/test_interfaces.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/domain/interfaces/ tests/unit/test_domain/test_interfaces.py
git commit -m "feat(domain): add abstract interfaces for providers, analyzers, notifiers"
```

---

## Phase 2: Data Layer (Days 3-5)

### Task 4: Database Models & Connection

**Files:**
- Create: `src/alpharadar/infrastructure/database/connection.py`
- Create: `src/alpharadar/infrastructure/database/models.py`
- Create: `tests/integration/test_database/test_connection.py`

**Interfaces:**
- Consumes: Domain entities from Task 2
- Produces: Async SQLAlchemy session factory, ORM models

- [ ] **Step 1: Write failing test for DB connection**

```python
# tests/integration/test_database/test_connection.py
import pytest
from alpharadar.infrastructure.database.connection import get_async_engine, get_async_session


@pytest.mark.asyncio
async def test_engine_creation():
    engine = get_async_engine()
    assert engine is not None


@pytest.mark.asyncio
async def test_session_creation():
    async for session in get_async_session():
        assert session is not None
        break
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integration/test_database/test_connection.py -v`
Expected: FAIL

- [ ] **Step 3: Implement database connection**

```python
# src/alpharadar/infrastructure/database/connection.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from alpharadar.config import settings


_engine = None
_session_factory = None


def get_async_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=False)
    return _engine


def get_async_session_factory():
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            get_async_engine(), class_=AsyncSession, expire_on_commit=False
        )
    return _session_factory


async def get_async_session():
    factory = get_async_session_factory()
    async with factory() as session:
        yield session
```

- [ ] **Step 4: Implement ORM models**

```python
# src/alpharadar/infrastructure/database/models.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class StockModel(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    exchange = Column(String(50), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    recommendations = relationship("RecommendationModel", back_populates="stock")
    positions = relationship("PositionModel", back_populates="stock")


class RecommendationModel(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    action = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    technical_score = Column(Float, nullable=True)
    fundamental_score = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("StockModel", back_populates="recommendations")


class PositionModel(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_buy_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stock = relationship("StockModel", back_populates="positions")


class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    alert_type = Column(String(50), nullable=False)  # PRICE, INDICATOR, RECOMMENDATION
    condition = Column(String(100), nullable=False)  # e.g., "price_above_200"
    threshold = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/integration/test_database/test_connection.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/alpharadar/infrastructure/database/ tests/integration/test_database/
git commit -m "feat(infra): add database models and async connection"
```

---

### Task 5: Yahoo Finance Data Provider

**Files:**
- Create: `src/alpharadar/infrastructure/data_providers/yahoo_finance.py`
- Create: `tests/unit/test_analyzers/test_yahoo_finance.py`

**Interfaces:**
- Consumes: `DataProvider` interface from Task 3
- Produces: `YahooFinanceProvider` implementing `DataProvider`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_analyzers/test_yahoo_finance.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from alpharadar.infrastructure.data_providers.yahoo_finance import YahooFinanceProvider


@pytest.mark.asyncio
async def test_get_stock():
    provider = YahooFinanceProvider()
    stock = await provider.get_stock("AAPL")
    assert stock.symbol == "AAPL"
    assert stock.name is not None


@pytest.mark.asyncio
async def test_get_history():
    provider = YahooFinanceProvider()
    history = await provider.get_history("AAPL", period="1mo")
    assert len(history) > 0
    assert history[0].close > 0


@pytest.mark.asyncio
async def test_get_stock_info():
    provider = YahooFinanceProvider()
    info = await provider.get_stock_info("AAPL")
    assert info.symbol == "AAPL"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_analyzers/test_yahoo_finance.py -v`
Expected: FAIL

- [ ] **Step 3: Implement YahooFinanceProvider**

```python
# src/alpharadar/infrastructure/data_providers/yahoo_finance.py
import yfinance as yf
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from alpharadar.domain.interfaces.data_provider import DataProvider
from alpharadar.domain.entities.stock import Stock, OHLCV, StockInfo


class YahooFinanceProvider(DataProvider):
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def get_stock(self, symbol: str) -> Stock:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return Stock(
            symbol=symbol,
            name=info.get("longName", symbol),
            exchange=info.get("exchange", "Unknown"),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def get_history(self, symbol: str, period: str = "1y") -> list[OHLCV]:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)
        return [
            OHLCV(
                timestamp=row.name.to_pydatetime(),
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"]),
            )
            for _, row in df.iterrows()
        ]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def get_stock_info(self, symbol: str) -> StockInfo:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return StockInfo(
            symbol=symbol,
            pe_ratio=info.get("trailingPE"),
            eps=info.get("trailingEps"),
            market_cap=info.get("marketCap"),
            revenue=info.get("totalRevenue"),
            debt_to_equity=info.get("debtToEquity"),
            dividend_yield=info.get("dividendYield"),
            sector=info.get("sector"),
            industry=info.get("industry"),
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_analyzers/test_yahoo_finance.py -v`
Expected: PASS (may need network access)

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/infrastructure/data_providers/yahoo_finance.py tests/unit/test_analyzers/test_yahoo_finance.py
git commit -m "feat(infra): add Yahoo Finance data provider"
```

---

### Task 6: Technical Analysis Engine

**Files:**
- Create: `src/alpharadar/infrastructure/analyzers/technical.py`
- Create: `tests/unit/test_analyzers/test_technical.py`

**Interfaces:**
- Consumes: `TechnicalAnalyzer` interface from Task 3, `Stock` entity from Task 2
- Produces: `TechnicalAnalyzerImpl` implementing `TechnicalAnalyzer`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_analyzers/test_technical.py
import pandas as pd
import pytest
from alpharadar.infrastructure.analyzers.technical import TechnicalAnalyzerImpl
from alpharadar.domain.entities.stock import Stock, OHLCV
from datetime import datetime, timedelta


def _make_stock_with_history(n: int = 200) -> Stock:
    """Create a stock with synthetic OHLCV history for testing."""
    base_price = 100.0
    history = []
    for i in range(n):
        ts = datetime(2024, 1, 1) + timedelta(days=i)
        price = base_price + (i * 0.5) + (i % 3 - 1) * 2
        history.append(
            OHLCV(
                timestamp=ts,
                open=price - 1,
                high=price + 2,
                low=price - 2,
                close=price,
                volume=1000000 + i * 10000,
            )
        )
    return Stock(symbol="TEST", name="Test Corp", exchange="NYSE", history=history)


@pytest.mark.asyncio
async def test_technical_score_in_range():
    stock = _make_stock_with_history()
    analyzer = TechnicalAnalyzerImpl()
    score = await analyzer.analyze(stock)
    assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_technical_score_with_uptrend():
    stock = _make_stock_with_history()
    analyzer = TechnicalAnalyzerImpl()
    score = await analyzer.analyze(stock)
    # Uptrend should give higher score
    assert score > 50
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_analyzers/test_technical.py -v`
Expected: FAIL

- [ ] **Step 3: Implement TechnicalAnalyzerImpl**

```python
# src/alpharadar/infrastructure/analyzers/technical.py
import pandas as pd
import pandas_ta as ta
from alpharadar.domain.interfaces.analyzer import TechnicalAnalyzer
from alpharadar.domain.entities.stock import Stock


class TechnicalAnalyzerImpl(TechnicalAnalyzer):
    async def analyze(self, stock: Stock) -> float:
        if not stock.history or len(stock.history) < 50:
            return 50.0  # Neutral if insufficient data

        df = pd.DataFrame(
            [
                {
                    "timestamp": h.timestamp,
                    "open": h.open,
                    "high": h.high,
                    "low": h.low,
                    "close": h.close,
                    "volume": h.volume,
                }
                for h in stock.history
            ]
        )
        df.set_index("timestamp", inplace=True)

        signals = []

        # RSI
        rsi = ta.rsi(df["close"], length=14)
        if rsi is not None and len(rsi) > 0:
            last_rsi = rsi.iloc[-1]
            if last_rsi < 30:
                signals.append(1.0)  # Oversold = buy signal
            elif last_rsi > 70:
                signals.append(-1.0)  # Overbought = sell signal
            else:
                signals.append(0.0)

        # MACD
        macd = ta.macd(df["close"])
        if macd is not None and len(macd) > 0:
            macd_line = macd.iloc[-1, 0]
            signal_line = macd.iloc[-1, 1]
            if macd_line > signal_line:
                signals.append(0.5)  # Bullish
            else:
                signals.append(-0.5)  # Bearish

        # Moving Average crossover (SMA 20 vs 50)
        sma20 = ta.sma(df["close"], length=20)
        sma50 = ta.sma(df["close"], length=50)
        if sma20 is not None and sma50 is not None:
            if sma20.iloc[-1] > sma50.iloc[-1]:
                signals.append(0.5)  # Golden cross territory
            else:
                signals.append(-0.5)  # Death cross territory

        if not signals:
            return 50.0

        avg_signal = sum(signals) / len(signals)
        # Normalize from [-1, 1] to [0, 100]
        score = (avg_signal + 1) * 50
        return max(0, min(100, score))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_analyzers/test_technical.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/infrastructure/analyzers/technical.py tests/unit/test_analyzers/test_technical.py
git commit -m "feat(infra): add technical analysis engine with RSI, MACD, SMA"
```

---

## Phase 3: Analysis Pipeline (Days 8-12)

### Task 7: Fundamental Analysis Engine

**Files:**
- Create: `src/alpharadar/infrastructure/analyzers/fundamental.py`
- Create: `tests/unit/test_analyzers/test_fundamental.py`

**Interfaces:**
- Consumes: `FundamentalAnalyzer` interface from Task 3, `StockInfo` from Task 2
- Produces: `FundamentalAnalyzerImpl` implementing `FundamentalAnalyzer`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_analyzers/test_fundamental.py
import pytest
from alpharadar.infrastructure.analyzers.fundamental import FundamentalAnalyzerImpl
from alpharadar.domain.entities.stock import StockInfo


@pytest.mark.asyncio
async def test_fundamental_score_in_range():
    info = StockInfo(
        symbol="AAPL",
        pe_ratio=28.5,
        eps=6.42,
        market_cap=2_900_000_000_000,
        revenue=394_000_000_000,
        debt_to_equity=1.8,
        dividend_yield=0.005,
    )
    analyzer = FundamentalAnalyzerImpl()
    score = await analyzer.analyze(info)
    assert 0 <= score <= 100


@pytest.mark.asyncio
async def test_fundamental_score_undervalued():
    info = StockInfo(symbol="TEST", pe_ratio=8.0, eps=10.0, debt_to_equity=0.5)
    analyzer = FundamentalAnalyzerImpl()
    score = await analyzer.analyze(info)
    assert score > 60  # Low P/E should be favorable


@pytest.mark.asyncio
async def test_fundamental_score_overvalued():
    info = StockInfo(symbol="TEST", pe_ratio=80.0, eps=0.5, debt_to_equity=5.0)
    analyzer = FundamentalAnalyzerImpl()
    score = await analyzer.analyze(info)
    assert score < 40  # High P/E and high debt should be unfavorable
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_analyzers/test_fundamental.py -v`
Expected: FAIL

- [ ] **Step 3: Implement FundamentalAnalyzerImpl**

```python
# src/alpharadar/infrastructure/analyzers/fundamental.py
from alpharadar.domain.interfaces.analyzer import FundamentalAnalyzer
from alpharadar.domain.entities.stock import StockInfo


class FundamentalAnalyzerImpl(FundamentalAnalyzer):
    async def analyze(self, info: StockInfo) -> float:
        scores = []

        # P/E Ratio scoring (lower is better, < 15 is cheap, > 40 is expensive)
        if info.pe_ratio is not None:
            if info.pe_ratio < 15:
                scores.append(80.0)
            elif info.pe_ratio < 25:
                scores.append(60.0)
            elif info.pe_ratio < 40:
                scores.append(40.0)
            else:
                scores.append(20.0)

        # Debt/Equity scoring (lower is better, < 1 is good, > 3 is risky)
        if info.debt_to_equity is not None:
            if info.debt_to_equity < 1:
                scores.append(80.0)
            elif info.debt_to_equity < 2:
                scores.append(60.0)
            elif info.debt_to_equity < 3:
                scores.append(40.0)
            else:
                scores.append(20.0)

        # Dividend yield scoring (higher is better)
        if info.dividend_yield is not None:
            if info.dividend_yield > 0.04:
                scores.append(80.0)
            elif info.dividend_yield > 0.02:
                scores.append(60.0)
            elif info.dividend_yield > 0:
                scores.append(40.0)
            else:
                scores.append(30.0)

        if not scores:
            return 50.0

        return sum(scores) / len(scores)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_analyzers/test_fundamental.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/infrastructure/analyzers/fundamental.py tests/unit/test_analyzers/test_fundamental.py
git commit -m "feat(infra): add fundamental analysis engine"
```

---

### Task 8: Sentiment Analysis Engine

**Files:**
- Create: `src/alpharadar/infrastructure/analyzers/sentiment.py`
- Create: `tests/unit/test_analyzers/test_sentiment.py`

**Interfaces:**
- Consumes: `SentimentAnalyzer` interface from Task 3
- Produces: `SentimentAnalyzerImpl` implementing `SentimentAnalyzer`

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_analyzers/test_sentiment.py
import pytest
from alpharadar.infrastructure.analyzers.sentiment import SentimentAnalyzerImpl


@pytest.mark.asyncio
async def test_sentiment_score_in_range():
    analyzer = SentimentAnalyzerImpl()
    score = await analyzer.analyze("AAPL")
    assert -1 <= score <= 1


@pytest.mark.asyncio
async def test_sentiment_analyze_text():
    analyzer = SentimentAnalyzerImpl()
    positive_score = analyzer._analyze_text("Great earnings, stock soaring to new highs!")
    negative_score = analyzer._analyze_text("Terrible losses, company in deep trouble")
    assert positive_score > negative_score
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_analyzers/test_sentiment.py -v`
Expected: FAIL

- [ ] **Step 3: Implement SentimentAnalyzerImpl**

```python
# src/alpharadar/infrastructure/analyzers/sentiment.py
from textblob import TextBlob
from alpharadar.domain.interfaces.analyzer import SentimentAnalyzer


class SentimentAnalyzerImpl(SentimentAnalyzer):
    async def analyze(self, symbol: str) -> float:
        # MVP: Return neutral sentiment
        # TODO: Integrate news scraping + TextBlob analysis
        return 0.0

    def _analyze_text(self, text: str) -> float:
        blob = TextBlob(text)
        return blob.sentiment.polarity  # -1 to +1
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_analyzers/test_sentiment.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/infrastructure/analyzers/sentiment.py tests/unit/test_analyzers/test_sentiment.py
git commit -m "feat(infra): add sentiment analysis engine (TextBlob)"
```

---

### Task 9: Recommendation Engine

**Files:**
- Create: `src/alpharadar/application/services/recommendation.py`
- Create: `tests/unit/test_services/test_recommendation.py`

**Interfaces:**
- Consumes: All 3 analyzers from Tasks 6-8, `Settings` from Task 1
- Produces: `RecommendationService` generating `Recommendation` entities

- [ ] **Step 1: Write failing tests**

```python
# tests/unit/test_services/test_recommendation.py
import pytest
from unittest.mock import AsyncMock
from alpharadar.application.services.recommendation import RecommendationService
from alpharadar.domain.entities.stock import Stock, StockInfo
from alpharadar.domain.entities.recommendation import Action


@pytest.mark.asyncio
async def test_recommendation_buy_signal():
    service = RecommendationService(
        technical_analyzer=AsyncMock(return_value=80.0),
        fundamental_analyzer=AsyncMock(return_value=75.0),
        sentiment_analyzer=AsyncMock(return_value=0.5),
    )
    stock = Stock(symbol="AAPL", name="Apple", exchange="NASDAQ")
    info = StockInfo(symbol="AAPL")
    rec = await service.generate(stock, info)
    assert rec.action == Action.BUY
    assert rec.score > 70


@pytest.mark.asyncio
async def test_recommendation_sell_signal():
    service = RecommendationService(
        technical_analyzer=AsyncMock(return_value=20.0),
        fundamental_analyzer=AsyncMock(return_value=25.0),
        sentiment_analyzer=AsyncMock(return_value=-0.5),
    )
    stock = Stock(symbol="TEST", name="Test", exchange="NYSE")
    info = StockInfo(symbol="TEST")
    rec = await service.generate(stock, info)
    assert rec.action == Action.SELL
    assert rec.score < 30
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_services/test_recommendation.py -v`
Expected: FAIL

- [ ] **Step 3: Implement RecommendationService**

```python
# src/alpharadar/application/services/recommendation.py
from alpharadar.domain.interfaces.analyzer import TechnicalAnalyzer, FundamentalAnalyzer, SentimentAnalyzer
from alpharadar.domain.entities.stock import Stock, StockInfo
from alpharadar.domain.entities.recommendation import Recommendation, Action, AnalysisScores
from alpharadar.config import settings


class RecommendationService:
    def __init__(
        self,
        technical_analyzer: TechnicalAnalyzer,
        fundamental_analyzer: FundamentalAnalyzer,
        sentiment_analyzer: SentimentAnalyzer,
    ):
        self.technical = technical_analyzer
        self.fundamental = fundamental_analyzer
        self.sentiment = sentiment_analyzer

    async def generate(self, stock: Stock, info: StockInfo) -> Recommendation:
        technical_score = await self.technical.analyze(stock)
        fundamental_score = await self.fundamental.analyze(info)
        sentiment_score = await self.sentiment.analyze(stock.symbol)

        # Weighted combination
        final_score = (
            technical_score * settings.weight_technical
            + fundamental_score * settings.weight_fundamental
            + (sentiment_score + 1) * 50 * settings.weight_sentiment
        )

        if final_score >= settings.buy_threshold:
            action = Action.BUY
            confidence = min(final_score / 100, 0.95)
        elif final_score <= settings.sell_threshold:
            action = Action.SELL
            confidence = min((100 - final_score) / 100, 0.95)
        else:
            action = Action.HOLD
            confidence = 0.5

        scores = AnalysisScores(
            technical=technical_score,
            fundamental=fundamental_score,
            sentiment=sentiment_score,
            final_score=final_score,
        )

        reasoning = (
            f"Technical: {technical_score:.1f}/100, "
            f"Fundamental: {fundamental_score:.1f}/100, "
            f"Sentiment: {sentiment_score:+.2f}"
        )

        return Recommendation(
            symbol=stock.symbol,
            action=action,
            score=final_score,
            confidence=confidence,
            reasoning=reasoning,
            scores=scores,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/unit/test_services/test_recommendation.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/application/services/recommendation.py tests/unit/test_services/test_recommendation.py
git commit -m "feat(app): add recommendation engine combining 3 analyzers"
```

---

## Phase 4: API & User Features (Days 13-18)

### Task 10: FastAPI Application & Stock Endpoints

**Files:**
- Create: `src/alpharadar/api/main.py`
- Create: `src/alpharadar/api/routes/stocks.py`
- Create: `src/alpharadar/api/schemas.py`
- Create: `tests/integration/test_api/test_stocks.py`

**Interfaces:**
- Consumes: Domain entities, application services
- Produces: FastAPI app with /api/stocks endpoints

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_api/test_stocks.py
import pytest
from httpx import AsyncClient, ASGITransport
from alpharadar.api.main import create_app


@pytest.mark.asyncio
async def test_health_endpoint():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_stocks_endpoint():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/stocks")
        assert response.status_code == 200
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integration/test_api/test_stocks.py -v`
Expected: FAIL

- [ ] **Step 3: Implement FastAPI app and routes**

```python
# src/alpharadar/api/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from alpharadar.api.routes import stocks, portfolio, recommendations, alerts


def create_app() -> FastAPI:
    app = FastAPI(title="AlphaRadar", version="0.1.0")

    app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
    app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
    app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
    app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "version": "0.1.0"}

    return app
```

```python
# src/alpharadar/api/routes/stocks.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_stocks():
    return {"stocks": [], "count": 0}


@router.get("/{symbol}")
async def get_stock(symbol: str):
    return {"symbol": symbol, "name": "placeholder"}
```

```python
# src/alpharadar/api/routes/portfolio.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_portfolio():
    return {"portfolio": {"name": "My Portfolio", "positions": [], "total_value": 0}}
```

```python
# src/alpharadar/api/routes/recommendations.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_recommendations():
    return {"recommendations": [], "count": 0}
```

```python
# src/alpharadar/api/routes/alerts.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_alerts():
    return {"alerts": [], "count": 0}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/integration/test_api/test_stocks.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/api/ tests/integration/test_api/
git commit -m "feat(api): add FastAPI app with health and stock endpoints"
```

---

### Task 11: Portfolio Endpoints

**Files:**
- Modify: `src/alpharadar/api/routes/portfolio.py`
- Create: `tests/integration/test_api/test_portfolio.py`

**Interfaces:**
- Consumes: `Portfolio` entity from Task 2
- Produces: CRUD endpoints for portfolio management

- [ ] **Step 1: Write failing tests**

```python
# tests/integration/test_api/test_portfolio.py
import pytest
from httpx import AsyncClient, ASGITransport
from alpharadar.api.main import create_app


@pytest.mark.asyncio
async def test_add_position():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/portfolio/positions",
            json={"symbol": "AAPL", "quantity": 10, "avg_buy_price": 185.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert data["quantity"] == 10


@pytest.mark.asyncio
async def test_get_portfolio():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/portfolio")
        assert response.status_code == 200
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/integration/test_api/test_portfolio.py -v`
Expected: FAIL

- [ ] **Step 3: Implement portfolio endpoints**

```python
# src/alpharadar/api/routes/portfolio.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory storage for MVP (single user)
_positions: list[dict] = []
_next_id = 1


class PositionCreate(BaseModel):
    symbol: str
    quantity: int
    avg_buy_price: float


@router.get("/")
async def get_portfolio():
    total_value = sum(p["quantity"] * p["avg_buy_price"] for p in _positions)
    return {
        "portfolio": {
            "name": "My Portfolio",
            "positions": _positions,
            "total_value": total_value,
            "total_pnl": 0.0,
        }
    }


@router.post("/positions")
async def add_position(position: PositionCreate):
    global _next_id
    pos = {
        "id": _next_id,
        "symbol": position.symbol,
        "quantity": position.quantity,
        "avg_buy_price": position.avg_buy_price,
        "current_price": position.avg_buy_price,
    }
    _positions.append(pos)
    _next_id += 1
    return pos


@router.delete("/positions/{position_id}")
async def delete_position(position_id: int):
    global _positions
    _positions = [p for p in _positions if p["id"] != position_id]
    return {"deleted": True}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/integration/test_api/test_portfolio.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/api/routes/portfolio.py tests/integration/test_api/test_portfolio.py
git commit -m "feat(api): add portfolio CRUD endpoints"
```

---

### Task 12: Docker Compose & Local Deployment

**Files:**
- Create: `docker-compose.yml`
- Create: `Dockerfile`
- Create: `scripts/start.sh`

**Interfaces:**
- Consumes: All previous tasks
- Produces: Running local environment with PostgreSQL + Redis + API

- [ ] **Step 1: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "alpharadar.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 2: Create docker-compose.yml**

```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/alpharadar
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./src:/app/src

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: alpharadar
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

- [ ] **Step 3: Create start script**

```bash
#!/bin/bash
# scripts/start.sh
echo "Starting AlphaRadar..."
docker compose up -d
echo "Waiting for services..."
sleep 5
echo "Running migrations..."
docker compose exec app python -c "from alpharadar.infrastructure.database.models import Base; from alpharadar.infrastructure.database.connection import get_async_engine; import asyncio; asyncio.run(Base.metadata.create_all(get_async_engine()))"
echo "AlphaRadar is running at http://localhost:8000"
```

- [ ] **Step 4: Verify Docker setup**

Run: `docker compose config`
Expected: Valid YAML output with all services defined.

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml Dockerfile scripts/
git commit -m "feat(deploy): add Docker Compose for local development"
```

---

## Summary

| Phase | Tasks | Days | Deliverable |
|-------|-------|------|-------------|
| 1. Foundation | 1-3 | 1-2 | Project structure, domain entities, interfaces |
| 2. Data Layer | 4-6 | 3-5 | Database, Yahoo Finance, Technical Analysis |
| 3. Analysis Pipeline | 7-9 | 8-12 | Fundamental, Sentiment, Recommendation Engine |
| 4. API & User Features | 10-12 | 13-18 | FastAPI endpoints, Portfolio, Docker |

**Total:** 12 tasks, ~18 working days
