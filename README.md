# AlphaRadar

Semi-autonomous stock analysis and recommendation system.

## Tech Stack
- Python 3.12+
- FastAPI
- PostgreSQL 16
- Redis 7
- pandas + pandas-ta
- yfinance

## Quick Start
```bash
# Install dependencies
pip install -e ".[dev]"

# Start services
docker compose up -d

# Run the app
uvicorn alpharadar.api.main:app --reload
```

## Testing
```bash
pytest
```
