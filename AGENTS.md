# Code Review Rules

## Python
- Use type hints on all public functions
- Follow PEP 8 (enforced by ruff)
- Use async/await for I/O-bound operations
- Prefer dataclasses or Pydantic models for data structures

## Architecture
- Follow hexagonal/clean architecture layers
- Domain layer has no external dependencies
- Infrastructure implements domain interfaces
- Application orchestrates domain and infrastructure

## Testing
- Unit tests for domain logic
- Integration tests for infrastructure
- Use pytest fixtures over setup/teardown
