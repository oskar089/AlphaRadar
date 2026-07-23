# Task 4: Celery Worker Setup

## Task Description

Set up Celery worker with task stubs and beat schedule for periodic tasks.

## Files to Create

1. `worker/__init__.py`
2. `worker/celery_app.py`
3. `worker/tasks.py`
4. `worker/schedules.py`
5. `tests/worker/__init__.py`
6. `tests/worker/test_tasks.py`

## Requirements

1. Create `worker/celery_app.py` with:
   - Celery app named "alpharadar"
   - Broker and result backend: `redis://localhost:6379/0`
   - JSON serialization
   - Timezone: `America/Argentina/Buenos_Aires`
   - Task time limits (300s hard, 240s soft)
   - Autodiscover tasks in `worker` package

2. Create `worker/tasks.py` with task stubs:
   - `update_stock_prices(symbols: list[str])` - updates prices
   - `evaluate_alerts()` - evaluates alerts
   - `analyze_sentiment(symbols: list[str])` - analyzes sentiment

3. Create `worker/schedules.py` with beat schedule:
   - `update-prices-15min`: every 15min during market hours (9-16, mon-fri)
   - `evaluate-alerts-5min`: every 5min during market hours
   - `analyze-sentiment-hourly`: hourly during market hours

4. Write tests that verify:
   - Celery app has correct configuration
   - All tasks are registered

## Interfaces

- Consumes: Redis broker, Settings from Task 3
- Produces: Celery app instance, task stubs, beat schedule

## Global Constraints

- Python 3.11+
- Celery 5.3+
- Redis 7+

## Success Criteria

- [ ] Celery app created with correct config
- [ ] Task stubs created
- [ ] Beat schedule configured
- [ ] Tests pass
