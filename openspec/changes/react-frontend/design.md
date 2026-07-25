# Design: React + Vite Frontend for AlphaRadar

## Technical Approach

Add a React 19 + TypeScript SPA under `frontend/` that consumes the existing FastAPI REST API. During development, Vite proxies `/api` to the backend at `:8000`. In production, a multi-stage Docker build produces static assets served by FastAPI via `StaticFiles`. The design follows the existing hexagonal architecture — the frontend is a pure consumer of the API boundary, touching no domain or application layer code.

## Architecture Decisions

| Decision | Option A | Option B | Chosen | Rationale |
|----------|----------|----------|--------|-----------|
| Dev proxy | Vite `server.proxy` config | Separate nginx container | Vite proxy | Zero-config, no extra container, native HMR |
| Prod serving | FastAPI `StaticFiles` mount | Separate nginx container | FastAPI mount | Single container, no compose changes, simpler ops |
| Type generation | `openapi-typescript` script | Manual type files | Script | Types stay in sync with backend automatically |
| State management | Zustand (stores) | Redux Toolkit | Zustand | Minimal boilerplate, single-user app, no middleware needs |
| Data fetching | TanStack Query + fetch | Axios + SWR | TanStack Query | Better cache invalidation, loading/error states |
| Docker build | Multi-stage in existing Dockerfile | Separate Dockerfile | Multi-stage in existing | Single build pipeline, no compose service changes |

## Data Flow

```
Browser ──→ Vite dev server (:5173)
              │ proxy /api/* → :8000
              ▼
         FastAPI (:8000)
              │
    ┌─────────┼──────────┐
    ▼         ▼          ▼
 stocks   portfolio  recommendations
    │
    ▼
 Yahoo Finance / InMemory repo
```

**Production**: FastAPI serves `frontend/dist/` as `StaticFiles`. SPA fallback routes `/*` to `index.html` so React Router handles client-side routing.

```
Browser ──→ FastAPI (:8000)
              │
              ├── /api/* → route handlers
              └── /*     → StaticFiles(frontend/dist) + index.html fallback
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `frontend/` (entire directory) | Create | React SPA: Vite + React 19 + TS + Tailwind 4 |
| `frontend/vite.config.ts` | Create | Dev proxy config for `/api` → `localhost:8000` |
| `frontend/tsconfig.json` | Create | Strict TS config, path aliases |
| `frontend/tailwind.config.ts` | Create | Tailwind 4 theme config |
| `frontend/package.json` | Create | Dependencies and scripts |
| `frontend/playwright.config.ts` | Create | E2E test config |
| `frontend/index.html` | Create | SPA entry point |
| `frontend/src/main.tsx` | Create | React root with providers (QueryClient, Router) |
| `frontend/src/App.tsx` | Create | Router setup with routes for 3 pages |
| `frontend/src/lib/api-client.ts` | Create | Typed fetch wrapper hitting `/api/*` |
| `frontend/src/lib/types.ts` | Create | Generated from OpenAPI (via script) |
| `frontend/src/lib/generate-types.sh` | Create | `openapi-typescript` script |
| `frontend/src/stores/stock-store.ts` | Create | Zustand store for stock detail state |
| `frontend/src/stores/portfolio-store.ts` | Create | Zustand store for portfolio UI state |
| `frontend/src/hooks/use-stock.ts` | Create | TanStack Query hook for stock detail |
| `frontend/src/hooks/use-recommendation.ts` | Create | TanStack Query hook for recommendation |
| `frontend/src/hooks/use-portfolio.ts` | Create | TanStack Query hooks for portfolio CRUD |
| `frontend/src/components/Layout.tsx` | Create | Sidebar/header navigation shell |
| `frontend/src/components/StockCard.tsx` | Create | Reusable stock summary card |
| `frontend/src/components/RecommendationBadge.tsx` | Create | BUY/SELL/HOLD badge |
| `frontend/src/components/PositionRow.tsx` | Create | Portfolio position with P&L |
| `frontend/src/components/AddPositionForm.tsx` | Create | Symbol + quantity + price form |
| `frontend/src/pages/Dashboard.tsx` | Create | `/` — recent recs + portfolio summary |
| `frontend/src/pages/StockDetail.tsx` | Create | `/stocks/:symbol` — stock info + rec |
| `frontend/src/pages/Portfolio.tsx` | Create | `/portfolio` — positions + add form |
| `frontend/tests/unit/` | Create | Vitest unit tests for hooks + stores |
| `frontend/tests/e2e/` | Create | Playwright E2E for all 3 pages |
| `src/alpharadar/api/main.py` | Modify | Mount `StaticFiles` for `frontend/dist` with SPA fallback |
| `Dockerfile` | Modify | Add Node build stage, copy dist into Python image |

## Interfaces / Contracts

### OpenAPI → TypeScript Types (generated)

```typescript
// From POST /api/portfolio/positions
interface PositionCreate {
  symbol: string;        // 1-10 chars, normalized uppercase
  quantity: number;      // > 0
  avg_buy_price: number; // > 0, finite
}

interface PositionResponse extends PositionCreate {
  id: number;
  current_price: number;
}

interface StockResponse {
  symbol: string;
  name: string;
  exchange: string;
}

interface RecommendationResponse {
  symbol: string;
  action: string;        // "BUY" | "SELL" | "HOLD"
  score: number;
  confidence: number;
  reasoning: string;
  scores: AnalysisScoresResponse;
}

interface AnalysisScoresResponse {
  technical: number;
  fundamental: number;
  sentiment: number;
  final_score: number;
}
```

### FastAPI StaticFiles Mount (production)

```python
# Added to create_app() in main.py, after router includes
from pathlib import Path
from fastapi.staticfiles import StaticFiles

DIST_DIR = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"

if DIST_DIR.is_dir():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="static")
```

`html=True` enables the SPA fallback — requests to unknown paths serve `index.html` instead of 404.

### Vite Dev Proxy

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
```

### TanStack Query Pattern

```typescript
// hooks/use-recommendation.ts
export function useRecommendation(symbol: string) {
  return useQuery({
    queryKey: ['recommendation', symbol],
    queryFn: () => apiClient.get<RecommendationResponse>(`/api/recommendations/${symbol}`),
    staleTime: 5 * 60 * 1000, // 5 min — stock recs don't change fast
    enabled: !!symbol,
  });
}
```

### Zustand Store Pattern

```typescript
// stores/portfolio-store.ts
interface PortfolioUIState {
  isAddFormOpen: boolean;
  toggleAddForm: () => void;
}

export const usePortfolioUIStore = create<PortfolioUIState>((set) => ({
  isAddFormOpen: false,
  toggleAddForm: () => set((s) => ({ isAddFormOpen: !s.isAddFormOpen })),
}));
```

Note: Server state (positions, stocks, recommendations) lives in TanStack Query cache. Zustand is for pure UI state only — form visibility, selected filters, sidebar collapse.

### Dockerfile Multi-Stage

```dockerfile
# Build stage
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Production stage
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src/ src/
RUN pip install --no-cache-dir .
COPY --from=frontend-build /frontend/dist ./frontend/dist
EXPOSE 8000
CMD ["uvicorn", "alpharadar.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Testing Strategy

| Layer | Tool | What to Test | Approach |
|-------|------|-------------|----------|
| Unit | Vitest | Hooks, stores, utility functions | Mock `fetch` globally, assert store state transitions |
| Unit | Vitest | Components (smoke) | Render with MSW handlers, check no crash |
| E2E | Playwright | Full user flows across 3 pages | Real Vite dev server + FastAPI backend, test navigation + data display |

### Mock Strategy

- **Unit tests**: `msw` (Mock Service Worker) intercepts `fetch` calls at the network layer. No direct mocking of `api-client` internals — tests verify the real HTTP path.
- **Vitest config**: `vitest.config.ts` with `environment: 'jsdom'` and `setupFiles: ['./tests/setup.ts']` for MSW server start.
- **Playwright**: Hits the real Vite dev server (`localhost:5173`) which proxies to a test FastAPI instance (`localhost:8000`). No mocking — true integration.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary. The frontend is a pure HTTP consumer of an existing API.

## Migration / Rollout

No data migration required. The backend API is unchanged. Frontend is additive — Swagger UI continues to work at `/docs`. The `StaticFiles` mount uses a path-prefix check so it doesn't conflict with API routes (all under `/api/`).

**Rollout**: No feature flag needed. Deploy the new Docker image and the SPA is served automatically.

## Open Questions

- [ ] Should `generate-types.sh` run as a pre-build script (`"build": "generate-types && vite build"`) or as a separate CI step? — Recommend pre-build for simplicity, but requires `openapi-typescript` as a devDependency.
- [ ] Does the current `Dockerfile` have a `package-lock.json` to support `npm ci` reproducibility? — If not, first `npm install` will generate one.
