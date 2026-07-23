# Tasks: React + Vite Frontend for AlphaRadar

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1150 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 → PR 4 → PR 5 → PR 6 |
| Delivery strategy | single-pr-default |
| Chain strategy | pending |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Project scaffolding + Vite + Tailwind + types | PR 1 (~150 lines) | `npm run dev` starts | Dev server spins up, shows blank page | `frontend/` dir — full revert |
| 2 | API client + data hooks | PR 2 (~250 lines) | `npm run build` | `curl localhost:5173` — no crash | `frontend/src/lib/` + `frontend/src/hooks/` |
| 3 | Reusable components | PR 3 (~250 lines) | `npm run build` | Components render in isolation | `frontend/src/components/` |
| 4 | Pages + routing | PR 4 (~350 lines) | `npm run build` | Dev server → 3 routes render | `frontend/src/pages/` + `App.tsx` |
| 5 | Backend integration + Docker | PR 5 (~60 lines) | `docker build .` | `docker compose up` serves SPA at `:8000` | `main.py` + `Dockerfile` (revert = no SPA serving) |
| 6 | Unit + E2E tests | PR 6 (~300 lines) | `npm run test && npx playwright test` | Full test suite green | `frontend/tests/` |

## Phase 1: Foundation — Project Scaffolding

- [x] 1.1 Create `frontend/package.json` with React 19, Vite, TypeScript, Tailwind CSS 4, React Router v7, Zustand, TanStack Query, vitest, playwright, msw, react-testing-library dependencies (~30 lines)
- [x] 1.2 Create `frontend/vite.config.ts` — Vite config with React plugin, dev proxy `/api` → `localhost:8000` (~15 lines)
- [x] 1.3 Create `frontend/tsconfig.json` — strict TypeScript, path aliases (`@/` → `src/`) (~25 lines)
- [x] 1.4 Create `frontend/tailwind.config.ts` — Tailwind 4 theme config with AlphaRadar color tokens (~20 lines)
- [x] 1.5 Create `frontend/index.html` — SPA entry with `<div id="root">` + script tag (~10 lines)
- [x] 1.6 Create `frontend/src/main.tsx` — React root, QueryClientProvider, BrowserRouter (~20 lines)
- [x] 1.7 Create `frontend/src/lib/types.ts` — Manual TypeScript interfaces matching OpenAPI schemas: `StockResponse`, `RecommendationResponse`, `AnalysisScoresResponse`, `PositionCreate`, `PositionResponse`, `PortfolioResponse` (~50 lines)

## Phase 2: API Layer — Client + Hooks

- [x] 2.1 Create `frontend/src/lib/api-client.ts` — typed fetch wrapper: `apiClient.get<T>(path)`, `apiClient.post<T>(path, body)`, `apiClient.delete(path)`, error handling mapping 404/422/503/5xx (~50 lines)
- [x] 2.2 Create `frontend/src/hooks/use-stock.ts` — TanStack Query hook `useStock(symbol)` for `GET /api/stocks/{symbol}` (~15 lines)
- [x] 2.3 Create `frontend/src/hooks/use-recommendation.ts` — TanStack Query hook `useRecommendation(symbol)` for `GET /api/recommendations/{symbol}`, 5min staleTime (~20 lines)
- [x] 2.4 Create `frontend/src/hooks/use-portfolio.ts` — TanStack Query hooks: `usePortfolio()` (query), `useAddPosition()` (mutation with invalidate), `useDeletePosition()` (mutation with invalidate) (~80 lines)
- [x] 2.5 Create `frontend/src/stores/stock-store.ts` — Zustand store for stock UI state (`selectedSymbol`) (~15 lines)
- [x] 2.6 Create `frontend/src/stores/portfolio-store.ts` — Zustand store for portfolio UI state (`isAddFormOpen`, toggle) (~15 lines)

## Phase 3: Components — Bottom-Up

- [x] 3.1 Create `frontend/src/components/Layout.tsx` — sidebar/header nav shell with links to Dashboard, Portfolio (~40 lines)
- [x] 3.2 Create `frontend/src/components/RecommendationBadge.tsx` — color-coded pill: BUY=green, SELL=red, HOLD=yellow (~20 lines)
- [x] 3.3 Create `frontend/src/components/StockCard.tsx` — reusable card: symbol, name, action badge, score, clickable → onClick (~35 lines)
- [x] 3.4 Create `frontend/src/components/PositionRow.tsx` — table row: symbol, quantity, avg price, current price, P&L (green/red), delete button (~40 lines)
- [x] 3.5 Create `frontend/src/components/AddPositionForm.tsx` — form with symbol, quantity, avg_buy_price inputs, inline validation (required, >0), submit handler (~50 lines)
- [x] 3.6 Create `frontend/src/components/LoadingSpinner.tsx` — centered loading indicator (~10 lines)
- [x] 3.7 Create `frontend/src/components/ErrorMessage.tsx` — error display with optional retry button (~15 lines)

## Phase 4: Pages + Routing

- [x] 4.1 Create `frontend/src/App.tsx` — React Router config: `/` → Dashboard, `/stocks/:symbol` → StockDetail, `/portfolio` → Portfolio, all wrapped in Layout (~30 lines)
- [x] 4.2 Create `frontend/src/pages/Dashboard.tsx` — portfolio summary (total value, P&L), recent recommendations list with StockCards, empty state for no positions (~70 lines)
- [x] 4.3 Create `frontend/src/pages/StockDetail.tsx` — stock info, recommendation with scores breakdown (technical, fundamental, sentiment), back button, 404 handling (~80 lines)
- [x] 4.4 Create `frontend/src/pages/Portfolio.tsx` — positions table with PositionRows, AddPositionForm, empty state (~70 lines)

## Phase 5: Backend Integration — Docker + Production Serving

- [ ] 5.1 Modify `src/alpharadar/api/main.py` — add StaticFiles mount for `frontend/dist` with `html=True` SPA fallback (~10 lines)
- [ ] 5.2 Modify `Dockerfile` — add Node 20 Alpine build stage for `frontend/`, copy dist into Python production image (~15 lines)

## Phase 6: Testing

- [ ] 6.1 Create `frontend/tests/setup.ts` — MSW server start/stop for unit tests (~15 lines)
- [ ] 6.2 Create `frontend/tests/fixtures/` — JSON fixture files mirroring API shapes for stocks, recommendations, portfolio (~40 lines)
- [ ] 6.3 Create `frontend/tests/unit/api-client.test.ts` — test error mapping: 404→"not found", 422→validation, 503→"unavailable", 5xx→generic (~40 lines)
- [ ] 6.4 Create `frontend/tests/unit/hooks.test.ts` — test `useStock`, `useRecommendation`, `usePortfolio` hooks with MSW (~50 lines)
- [ ] 6.5 Create `frontend/tests/unit/components.test.tsx` — smoke tests: all 7 components render without crash (~50 lines)
- [ ] 6.6 Create `frontend/tests/e2e/dashboard.spec.ts` — Playwright: load dashboard, verify portfolio summary or empty state, verify recommendations list (~40 lines)
- [ ] 6.7 Create `frontend/tests/e2e/stock-detail.spec.ts` — Playwright: navigate to stock detail, verify scores, back navigation (~35 lines)
- [ ] 6.8 Create `frontend/tests/e2e/portfolio.spec.ts` — Playwright: add position, verify table row, delete position, empty state (~50 lines)
