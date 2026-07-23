import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { beforeAll, afterEach, afterAll } from 'vitest'
import '@testing-library/jest-dom/vitest'

const handlers = [
  http.get('/api/health/live', () => {
    return HttpResponse.json({ status: 'alive', version: '0.1.0' })
  }),
  http.get('/api/stocks/:symbol', ({ params }) => {
    const symbol = (params.symbol as string).toUpperCase()
    if (symbol === 'INVALID') {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json({ symbol, name: `${symbol} Inc.`, exchange: 'NASDAQ' })
  }),
  http.get('/api/recommendations/:symbol', ({ params }) => {
    const symbol = (params.symbol as string).toUpperCase()
    if (symbol === 'INVALID') {
      return new HttpResponse(null, { status: 404 })
    }
    return HttpResponse.json({
      symbol,
      action: 'BUY',
      score: 0.75,
      confidence: 0.85,
      reasoning: 'Strong technicals and fundamentals.',
      scores: { technical: 0.8, fundamental: 0.7, sentiment: 0.6, final_score: 0.75 },
    })
  }),
  http.get('/api/portfolio', () => {
    return HttpResponse.json({
      portfolio: {
        name: 'My Portfolio',
        positions: [
          { id: 1, symbol: 'AAPL', quantity: 10, avg_buy_price: 150.0, current_price: 175.0 },
        ],
        total_value: 1750.0,
        total_pnl: 250.0,
        storage: 'process-local-non-durable',
      },
    })
  }),
  http.post('/api/portfolio/positions', async ({ request }) => {
    const body = (await request.json()) as { symbol: string; quantity: number; avg_buy_price: number }
    return HttpResponse.json(
      { id: 2, ...body, current_price: body.avg_buy_price },
      { status: 201 },
    )
  }),
  http.delete('/api/portfolio/positions/:id', () => {
    return new HttpResponse(null, { status: 204 })
  }),
]

const server = setupServer(...handlers)

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

export { server }
