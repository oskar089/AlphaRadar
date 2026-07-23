# Proposal: React + Vite Frontend for AlphaRadar

## Intent

Replace the default Swagger UI with a modern React SPA that provides a proper user experience for stock analysis, recommendations, and portfolio management.

## Target Users

Personal use — the developer/investor using AlphaRadar for their own stock analysis workflow.

## Scope

### Pages

1. **Dashboard** (`/`) — Overview with recent recommendations, portfolio summary
2. **Stock Detail** (`/stocks/:symbol`) — Individual stock info + buy/sell recommendation
3. **Portfolio** (`/portfolio`) — List of positions + add position form

### Components

- Layout with navigation sidebar/header
- Stock card component (reusable across dashboard and portfolio)
- Recommendation badge (BUY/SELL/HOLD)
- Portfolio position row with P&L display
- Add position form (symbol, quantity, average price)

### Integration

- Vite dev server proxies `/api/*` to FastAPI at `localhost:8000`
- Production: FastAPI serves built static files from `frontend/dist/`
- OpenAPI types generated from backend schema

## Non-Goals

- Authentication/authorization (single user)
- Real-time WebSocket updates
- Mobile responsive (desktop-first)
- Charts/trading views (future enhancement)

## First Slice

Dashboard + Stock Detail — highest value, demonstrates full stack integration.

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | React 19 + TypeScript | Modern, type-safe, large ecosystem |
| Build | Vite | Fast dev server, native ESM |
| Styling | Tailwind CSS 4 | Utility-first, fast to prototype |
| Routing | React Router v7 | Standard for React SPAs |
| State | Zustand | Lightweight, no boilerplate |
| Data fetching | TanStack Query | Caching, loading states, error handling |
| HTTP client | fetch API | Native, no extra deps |
| E2E testing | Playwright | Industry standard, fast |
| Unit testing | Vitest | Native Vite integration |

## Risks

- API schema may evolve — mitigate with OpenAPI type generation
- No design system — simple Tailwind utility classes for now
- Single-user portfolio is in-memory — frontend must handle empty state gracefully
