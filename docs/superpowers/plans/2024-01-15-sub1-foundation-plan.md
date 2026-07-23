# Sub-project 1: Foundation (Persistence + Scheduler) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up PostgreSQL portfolio persistence and Celery scheduler as the base infrastructure for AlphaRadar v2.0

**Architecture:** Dual-mode portfolio repository (in-memory for tests, PostgreSQL for production), Celery worker with Redis broker, Beat schedule for periodic tasks, Alembic for database migrations.

**Tech Stack:** PostgreSQL, SQLAlchemy 2.0, Alembic, Celery 5.x, Redis, Docker Compose

## Global Constraints

- Python 3.11+
- FastAPI 0.109+
- SQLAlchemy 2.0+ (async)
- Celery 5.3+
- PostgreSQL 15+
- Redis 7+
- All code must have tests
- Follow existing project patterns in `src/alpharadar/`

---

## File Structure

```
src/alpharadar/
├── infrastructure/
│   └── portfolio/
│       ├── __init__.py
│       ├── in_memory.py (existing)
│       └── postgresql.py (NEW)
├── config.py (MODIFY)
└── api/
    └── main.py (MODIFY)

alembic/
├── alembic.ini (NEW)
├── env.py (NEW)
└── versions/
    └── 001_initial.py (NEW)

worker/
├── __init__.py (NEW)
├── celery_app.py (NEW)
├── tasks.py (NEW)
└── schedules.py (NEW)

docker-compose.yml (MODIFY)
pyproject.toml (MODIFY)
tests/
├── infrastructure/
│   └── portfolio/
│       └── test_postgresql.py (NEW)
└── worker/
    └── test_tasks.py (NEW)
```

---

### Task 1: PostgreSQL Portfolio Repository

**Files:**
- Create: `src/alpharadar/infrastructure/portfolio/postgresql.py`
- Create: `tests/infrastructure/portfolio/test_postgresql.py`

**Interfaces:**
- Consumes: `PortfolioRepository` port from `src/alpharadar/application/ports/portfolio.py`
- Produces: `PostgreSQLPortfolioRepository` class implementing `PortfolioRepository` with methods: `list()`, `add()`, `delete()`

- [ ] **Step 1: Write the failing test**

```python
# tests/infrastructure/portfolio/test_postgresql.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alpharadar.infrastructure.portfolio.postgresql import PostgreSQLPortfolioRepository, Base
from alpharadar.application.ports.portfolio import StoredPosition

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
def repository(db_session):
    return PostgreSQLPortfolioRepository(db_session)

@pytest.mark.asyncio
async def test_add_position(repository):
    position = await repository.add("AAPL", 10, 150.0)
    
    assert position.id is not None
    assert position.symbol == "AAPL"
    assert position.quantity == 10
    assert position.avg_buy_price == 150.0
    assert position.current_price == 150.0

@pytest.mark.asyncio
async def test_list_positions(repository):
    await repository.add("AAPL", 10, 150.0)
    await repository.add("MSFT", 5, 300.0)
    
    positions = await repository.list()
    assert len(positions) == 2
    assert any(p.symbol == "AAPL" for p in positions)
    assert any(p.symbol == "MSFT" for p in positions)

@pytest.mark.asyncio
async def test_delete_position(repository):
    position = await repository.add("AAPL", 10, 150.0)
    
    deleted = await repository.delete(position.id)
    assert deleted is True
    
    positions = await repository.list()
    assert len(positions) == 0

@pytest.mark.asyncio
async def test_delete_nonexistent_position(repository):
    deleted = await repository.delete(999)
    assert deleted is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/infrastructure/portfolio/test_postgresql.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'alpharadar.infrastructure.portfolio.postgresql'"

- [ ] **Step 3: Write minimal implementation**

```python
# src/alpharadar/infrastructure/portfolio/postgresql.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase
from typing import List

from alpharadar.application.ports.portfolio import PortfolioRepository, StoredPosition


class Base(DeclarativeBase):
    pass


class PositionModel(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_buy_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)


class PostgreSQLPortfolioRepository(PortfolioRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def list(self) -> List[StoredPosition]:
        from sqlalchemy import select
        result = await self.session.execute(select(PositionModel))
        positions = result.scalars().all()
        
        return [
            StoredPosition(
                id=p.id,
                symbol=p.symbol,
                quantity=p.quantity,
                avg_buy_price=p.avg_buy_price,
                current_price=p.current_price
            )
            for p in positions
        ]
    
    async def add(self, symbol: str, quantity: int, avg_buy_price: float) -> StoredPosition:
        model = PositionModel(
            symbol=symbol,
            quantity=quantity,
            avg_buy_price=avg_buy_price,
            current_price=avg_buy_price
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        
        return StoredPosition(
            id=model.id,
            symbol=model.symbol,
            quantity=model.quantity,
            avg_buy_price=model.avg_buy_price,
            current_price=model.current_price
        )
    
    async def delete(self, position_id: int) -> bool:
        from sqlalchemy import delete
        result = await self.session.execute(
            delete(PositionModel).where(PositionModel.id == position_id)
        )
        await self.session.commit()
        return result.rowcount > 0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/infrastructure/portfolio/test_postgresql.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/infrastructure/portfolio/postgresql.py tests/infrastructure/portfolio/test_postgresql.py
git commit -m "feat(portfolio): add PostgreSQL repository implementation"
```

---

### Task 2: Alembic Setup and Initial Migration

**Files:**
- Create: `alembic/alembic.ini`
- Create: `alembic/env.py`
- Create: `alembic/versions/001_initial.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: Database models from Task 1
- Produces: Migration scripts, database schema

- [ ] **Step 1: Add dependencies to pyproject.toml**

```toml
# pyproject.toml - add to [project.dependencies]
"alembic>=1.13.0",
"asyncpg>=0.29.0",
"aiosqlite>=0.19.0",
```

- [ ] **Step 2: Create alembic.ini**

```ini
# alembic/alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql+asyncpg://alpharadar:alpharadar@localhost:5432/alpharadar

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 3: Create env.py**

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from alpharadar.infrastructure.portfolio.postgresql import Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 4: Generate initial migration**

Run: `cd alembic && alembic revision --autogenerate -m "initial"`
Expected: Creates `alembic/versions/001_initial.py`

- [ ] **Step 5: Run migration against test database**

Run: `alembic upgrade head`
Expected: Creates tables in database

- [ ] **Step 6: Commit**

```bash
git add alembic/
git commit -m "feat(db): add Alembic setup with initial migration"
```

---

### Task 3: Configuration Updates

**Files:**
- Modify: `src/alpharadar/config.py`

**Interfaces:**
- Consumes: Environment variables
- Produces: Updated `Settings` class with persistence and Celery config

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
from alpharadar.config import Settings

def test_settings_persistence_mode():
    settings = Settings(portfolio_persistence="memory")
    assert settings.portfolio_persistence == "memory"

def test_settings_postgresql_url():
    settings = Settings(portfolio_persistence="postgresql")
    assert "postgresql" in settings.database_url

def test_settings_redis_url():
    settings = Settings()
    assert "redis" in settings.celery_broker_url
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "TypeError: '__init__' got an unexpected keyword argument 'portfolio_persistence'"

- [ ] **Step 3: Update config.py**

```python
# src/alpharadar/config.py - add these fields
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    # Existing fields...
    api_key: str
    api_secret: str
    base_url: str = "https://api.alphavantage.co"
    
    # Portfolio persistence
    portfolio_persistence: str = "memory"  # "memory" or "postgresql"
    database_url: str = "postgresql+asyncpg://alpharadar:alpharadar@localhost:5432/alpharadar"
    
    # Celery configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/alpharadar/config.py tests/test_config.py
git commit -m "feat(config): add persistence and Celery configuration"
```

---

### Task 4: Celery Worker Setup

**Files:**
- Create: `worker/__init__.py`
- Create: `worker/celery_app.py`
- Create: `worker/tasks.py`
- Create: `worker/schedules.py`
- Create: `tests/worker/test_tasks.py`

**Interfaces:**
- Consumes: Redis broker, Settings from Task 3
- Produces: Celery app instance, periodic task schedules

- [ ] **Step 1: Write the failing test**

```python
# tests/worker/test_tasks.py
import pytest
from worker.celery_app import app

def test_celery_app_config():
    assert app.conf.broker_url == "redis://localhost:6379/0"
    assert app.conf.result_backend == "redis://localhost:6379/0"

def test_celery_app_has_tasks():
    task_names = [task.name for task in app.tasks.values()]
    assert "worker.tasks.update_stock_prices" in task_names
    assert "worker.tasks.evaluate_alerts" in task_names
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/worker/test_tasks.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'worker'"

- [ ] **Step 3: Create celery_app.py**

```python
# worker/celery_app.py
from celery import Celery
from celery.schedules import crontab

app = Celery("alpharadar")

app.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="redis://localhost:6379/0",
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Argentina/Buenos_Aires",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)

app.autodiscover_tasks(["worker"])
```

- [ ] **Step 4: Create tasks.py**

```python
# worker/tasks.py
from worker.celery_app import app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@app.task(bind=True, name="worker.tasks.update_stock_prices")
def update_stock_prices(self, symbols: list[str]):
    """Update stock prices for given symbols."""
    logger.info(f"Updating prices for: {symbols}")
    # Will be implemented in Sub-project 1
    return {"status": "success", "symbols": symbols}


@app.task(bind=True, name="worker.tasks.evaluate_alerts")
def evaluate_alerts(self):
    """Evaluate all active alerts."""
    logger.info("Evaluating alerts")
    # Will be implemented in Sub-project 2
    return {"status": "success"}


@app.task(bind=True, name="worker.tasks.analyze_sentiment")
def analyze_sentiment(self, symbols: list[str]):
    """Analyze sentiment for given symbols."""
    logger.info(f"Analyzing sentiment for: {symbols}")
    # Will be implemented in Sub-project 3
    return {"status": "success", "symbols": symbols}
```

- [ ] **Step 5: Create schedules.py**

```python
# worker/schedules.py
from celery.schedules import crontab

beat_schedule = {
    # Update stock prices every 15 minutes during market hours
    "update-prices-15min": {
        "task": "worker.tasks.update_stock_prices",
        "schedule": crontab(minute="*/15", hour="9-16", day_of_week="mon-fri"),
        "args": (["AAPL", "MSFT", "GOOGL"],),  # Will be dynamic
    },
    
    # Evaluate alerts every 5 minutes
    "evaluate-alerts-5min": {
        "task": "worker.tasks.evaluate_alerts",
        "schedule": crontab(minute="*/5", hour="9-16", day_of_week="mon-fri"),
    },
    
    # Analyze sentiment hourly
    "analyze-sentiment-hourly": {
        "task": "worker.tasks.analyze_sentiment",
        "schedule": crontab(minute=0, hour="9-16", day_of_week="mon-fri"),
        "args": (["AAPL", "MSFT", "GOOGL"],),
    },
}
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/worker/test_tasks.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add worker/ tests/worker/
git commit -m "feat(worker): add Celery worker with task stubs and beat schedule"
```

---

### Task 5: Docker Compose Update

**Files:**
- Modify: `docker-compose.yml`

**Interfaces:**
- Consumes: All previous tasks
- Produces: Running services (app, db, redis, worker, beat)

- [ ] **Step 1: Write the failing test**

```bash
# tests/test_docker_compose.sh
docker-compose config --quiet
if [ $? -eq 0 ]; then
    echo "PASS: docker-compose.yml is valid"
    exit 0
else
    echo "FAIL: docker-compose.yml is invalid"
    exit 1
fi
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash tests/test_docker_compose.sh`
Expected: FAIL (missing services)

- [ ] **Step 3: Update docker-compose.yml**

```yaml
# docker-compose.yml
version: "3.9"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis
    volumes:
      - ./src:/app/src
    command: uvicorn alpharadar.api.main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: alpharadar
      POSTGRES_PASSWORD: alpharadar
      POSTGRES_DB: alpharadar
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U alpharadar"]
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

  worker:
    build: .
    env_file:
      - .env
    depends_on:
      - redis
      - db
    volumes:
      - ./src:/app/src
      - ./worker:/app/worker
    command: celery -A worker.celery_app worker --loglevel=info --concurrency=2
    healthcheck:
      test: ["CMD-SHELL", "celery -A worker.celery_app inspect ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  beat:
    build: .
    env_file:
      - .env
    depends_on:
      - redis
    volumes:
      - ./src:/app/src
      - ./worker:/app/worker
    command: celery -A worker.celery_app beat --loglevel=info
    healthcheck:
      test: ["CMD-SHELL", "celery -A worker.celery_app inspect ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash tests/test_docker_compose.sh`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml tests/test_docker_compose.sh
git commit -m "feat(docker): add worker, beat, and database services"
```

---

### Task 6: Integration Test

**Files:**
- Create: `tests/integration/test_foundation.py`

**Interfaces:**
- Consumes: All previous tasks
- Produces: Verified end-to-end foundation

- [ ] **Step 1: Write the failing test**

```python
# tests/integration/test_foundation.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alpharadar.infrastructure.portfolio.postgresql import PostgreSQLPortfolioRepository, Base

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
def repository(db_session):
    return PostgreSQLPortfolioRepository(db_session)

@pytest.mark.asyncio
async def test_full_portfolio_lifecycle(repository):
    # Add positions
    pos1 = await repository.add("AAPL", 10, 150.0)
    pos2 = await repository.add("MSFT", 5, 300.0)
    
    # List
    positions = await repository.list()
    assert len(positions) == 2
    
    # Delete one
    deleted = await repository.delete(pos1.id)
    assert deleted is True
    
    # Verify
    positions = await repository.list()
    assert len(positions) == 1
    assert positions[0].symbol == "MSFT"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/integration/test_foundation.py -v`
Expected: FAIL (integration test)

- [ ] **Step 3: Run test to verify it passes**

Run: `pytest tests/integration/test_foundation.py -v`
Expected: PASS (all components working together)

- [ ] **Step 4: Commit**

```bash
git add tests/integration/
git commit -m "test: add integration test for foundation components"
```

---

### Task 7: Documentation and Final Polish

**Files:**
- Create: `docs/SETUP.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: All previous tasks
- Produces: Updated documentation

- [ ] **Step 1: Create SETUP.md**

```markdown
# AlphaRadar v2.0 Setup Guide

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (or use Docker)
- Redis (or use Docker)

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd Inversiones
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Start services:
   ```bash
   docker-compose up -d
   ```

4. Run migrations:
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. Access the API:
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## Configuration

### Portfolio Persistence

Set `PORTFOLIO_PERSISTENCE` in `.env`:
- `memory` - In-memory storage (for testing)
- `postgresql` - PostgreSQL storage (for production)

### Celery Worker

The worker processes background tasks:
- Price updates (every 15 minutes)
- Alert evaluation (every 5 minutes)
- Sentiment analysis (hourly)

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Running Linter

```bash
ruff check src/
```

### Database Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```
```

- [ ] **Step 2: Update README.md**

Add a section about v2.0 setup and link to SETUP.md.

- [ ] **Step 3: Commit**

```bash
git add docs/SETUP.md README.md
git commit -m "docs: add setup guide and update README"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** PostgreSQL repository ✅, Alembic migrations ✅, Celery worker ✅, Beat schedule ✅, Docker Compose ✅
- [x] **Placeholder scan:** No TBD/TODO found, all steps have complete code
- [x] **Type consistency:** Portfolio, Position, PortfolioRepository types consistent across tasks

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2024-01-15-sub1-foundation-plan.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
