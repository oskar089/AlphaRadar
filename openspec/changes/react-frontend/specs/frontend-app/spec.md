# Frontend Application Specification

## Purpose

React 19 + Vite SPA consuming the AlphaRadar FastAPI backend. Desktop-first, single-user, no auth.

## API Integration

| Method | Path | Params | Response | Errors |
|--------|------|--------|----------|--------|
| GET | `/api/health/live` | — | `{status, version}` | — |
| GET | `/api/stocks/{symbol}` | symbol | `{symbol, name, exchange}` | 404, 503 |
| GET | `/api/portfolio` | — | `{portfolio: {name, positions[], total_value, total_pnl}}` | — |
| POST | `/api/portfolio/positions` | `{symbol, quantity, avg_buy_price}` | PositionResponse: `{id, symbol, quantity, avg_buy_price, current_price}` | 422 |
| DELETE | `/api/portfolio/positions/{id}` | id | 204 No Content | 404 |
| GET | `/api/recommendations/{symbol}` | symbol | `{symbol, action, score, confidence, reasoning, scores: {technical, fundamental, sentiment, final_score}}` | 404, 503 |

All error responses: `{detail: string}`. Frontend MUST map 404→"not found" message, 422→inline validation, 503→"market unavailable" + retry, 5xx→generic toast. Dev proxies `/api/*` to `localhost:8000`; production serves `frontend/dist/`.

## Pages

### Dashboard (`/`)

- GIVEN user has positions → WHEN loads → THEN shows total_value and total_pnl as currency
- GIVEN no positions → WHEN loads → THEN shows "No positions yet" empty state
- GIVEN recommendations exist → WHEN loads → THEN lists symbol, action badge, score
- GIVEN a card → WHEN clicked → THEN navigates to `/stocks/:symbol`

### Stock Detail (`/stocks/:symbol`)

- GIVEN valid symbol → WHEN loads → THEN shows name, exchange, recommendation with score
- GIVEN recommendation loaded → THEN displays technical, fundamental, sentiment scores
- GIVEN back action → WHEN triggered → THEN returns to previous page
- GIVEN invalid symbol → WHEN 404 → THEN shows "Symbol not found" with dashboard link

### Portfolio (`/portfolio`)

- GIVEN positions exist → WHEN loads → THEN shows table: symbol, quantity, avg price, current price, P&L
- GIVEN P&L positive → THEN row P&L is green; negative → red
- GIVEN valid form submission → THEN POST fires, table refreshes, form resets
- GIVEN invalid form submission → THEN inline validation errors appear
- GIVEN delete clicked → THEN confirmation prompt, DELETE fires, row removed
- GIVEN no positions → THEN empty state with add form prompt

## Components

| Component | Purpose | Props |
|-----------|---------|-------|
| Layout | Nav + content area | children |
| StockCard | Reusable stock summary card | symbol, action, score, onClick |
| RecommendationBadge | Color-coded BUY/SELL/HOLD pill | action |
| PositionRow | Portfolio table row with P&L | position, onDelete |
| AddPositionForm | Add position form | onSubmit |
| LoadingSpinner | Centered loading indicator | — |
| ErrorMessage | Error with optional retry | message, onRetry? |

## Testing

**Unit (Vitest + React Testing Library)**: Render tests for all components, user interaction tests, MSW handlers for API mocking. Target: ≥80% component coverage.

**E2E (Playwright)**: Dashboard load with data, stock detail navigation flow, add/delete position CRUD, empty state rendering. Playwright tests run against real FastAPI with seeded fixtures.

**Test Data**: JSON fixture files mirroring API shapes. MSW intercepts `/api/*` in unit tests. Playwright uses conftest-seeded backend.
