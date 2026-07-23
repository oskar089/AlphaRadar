# Task 5: Docker Compose Update

## Task Description

Update Docker Compose to include worker, beat, and database services.

## Files to Modify

1. `docker-compose.yml`

## Requirements

1. Add the following services:
   - `db`: PostgreSQL 15 with healthcheck
   - `redis`: Redis 7 with healthcheck
   - `worker`: Celery worker with healthcheck
   - `beat`: Celery beat with healthcheck

2. Update `app` service to depend on `db` and `redis`

3. Add named volume `postgres_data` for database persistence

4. Write a test script that validates docker-compose.yml

## Interfaces

- Consumes: All previous tasks
- Produces: Running services (app, db, redis, worker, beat)

## Global Constraints

- Docker Compose 3.9
- PostgreSQL 15+
- Redis 7+

## Success Criteria

- [ ] All services defined
- [ ] Healthchecks configured
- [ ] Volumes configured
- [ ] Test script validates config
