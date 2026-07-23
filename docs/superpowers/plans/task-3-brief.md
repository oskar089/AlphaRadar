# Task 3: Configuration Updates

## Task Description

Update the configuration to support portfolio persistence mode and Celery settings.

## Files to Modify

1. `src/alpharadar/config.py` - add new settings

## Requirements

1. Add the following fields to the `Settings` class:
   - `portfolio_persistence: str = "memory"` - "memory" or "postgresql"
   - `database_url: str = "postgresql+asyncpg://alpharadar:alpharadar@localhost:5432/alpharadar"`
   - `celery_broker_url: str = "redis://localhost:6379/0"`
   - `celery_result_backend: str = "redis://localhost:6379/0"`
   - `redis_url: str = "redis://localhost:6379/0"`

2. Write tests that verify:
   - Settings can be created with `portfolio_persistence="memory"`
   - Settings can be created with `portfolio_persistence="postgresql"`
   - Default `celery_broker_url` contains "redis"

## Interfaces

- Consumes: Existing `Settings` class
- Produces: Updated `Settings` class with new fields

## Global Constraints

- Python 3.11+
- Pydantic Settings
- Follow existing patterns in `src/alpharadar/config.py`

## Success Criteria

- [ ] New fields added to Settings class
- [ ] Tests pass
- [ ] Existing functionality not broken
