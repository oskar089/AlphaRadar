# Task 5: Docker Compose Update — Report

## What I Implemented

Updated `docker-compose.yml` to include all five services (app, db, redis, worker, beat) with healthchecks, dependencies, and proper volume configuration.

### Changes to `docker-compose.yml`
- Added `worker` service: builds from same Dockerfile, runs `celery -A alpharadar.worker.celery_app worker --loglevel=info`, depends on `redis` (healthy), healthcheck via `celery inspect ping` with `start_period: 10s`
- Added `beat` service: builds from same Dockerfile, runs `celery -A alpharadar.worker.celery_app beat --loglevel=info`, depends on `redis` (healthy), healthcheck via `celery inspect ping` with `start_period: 10s`
- Renamed volume from `pgdata` to `postgres_data` per spec
- Worker and beat both receive `DATABASE_URL` and `REDIS_URL` environment variables

### Test file: `tests/infrastructure/test_docker_compose.py`
- 22 tests across 5 test classes covering: services defined, healthchecks present, dependency chain, volume configuration, worker/beat build config
- Uses pytest fixtures (`compose`, `services`) for DRY test data access
- Full type annotations (`-> None` on all test methods)

## TDD Evidence

### RED
Ran 22 tests before implementation — 11 passed (existing app/db/redis config), 11 failed (missing worker, beat, wrong volume name). Key failures:
- `test_worker_service_defined` — `KeyError: 'worker'`
- `test_beat_service_defined` — `KeyError: 'beat'`
- `test_postgres_data_volume_defined` — `'postgres_data' not in {'pgdata': None}`

### GREEN
After implementation, all 22 tests passed in 0.30s.

## Files Changed
- `docker-compose.yml` — added worker/beat services, renamed volume
- `tests/infrastructure/test_docker_compose.py` — new test file (22 tests)

## Test Results
22/22 passing, output pristine. Lint clean (ruff).

## Self-Review Findings
- Healthcheck uses `start_period: 10s` for worker/beat to allow Celery boot time
- Both worker and beat depend only on `redis` (not `db`) — Celery broker is Redis, DB access happens inside task code
- Volume renamed from `pgdata` to `postgres_data` to match spec
