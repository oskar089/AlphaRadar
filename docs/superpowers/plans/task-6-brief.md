# Task 6: Integration Test

## Task Description

Write an integration test that verifies the foundation components work together.

## Files to Create

1. `tests/integration/test_foundation.py`

## Requirements

1. Write a test that:
   - Creates an in-memory database
   - Initializes the PostgreSQL portfolio repository
   - Adds positions
   - Lists positions
   - Deletes a position
   - Verifies the final state

2. Test should use pytest fixtures for database session and repository

## Interfaces

- Consumes: All previous tasks
- Produces: Verified end-to-end foundation

## Global Constraints

- Python 3.11+
- pytest-asyncio
- SQLite in-memory for tests

## Success Criteria

- [ ] Integration test created
- [ ] Test passes
- [ ] All components work together
