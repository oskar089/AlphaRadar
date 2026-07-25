import { describe, it, expect } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createElement } from 'react'
import { useStock } from '@/hooks/use-stock'
import { useRecommendation } from '@/hooks/use-recommendation'
import { usePortfolio } from '@/hooks/use-portfolio'

function createWrapper() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return createElement(QueryClientProvider, { client: queryClient }, children)
  }
}

describe('useStock', () => {
  it('fetches stock data for valid symbol', async () => {
    const { result } = renderHook(() => useStock('AAPL'), { wrapper: createWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data).toMatchObject({ symbol: 'AAPL', name: 'AAPL Inc.' })
  })

  it('does not fetch when symbol is empty', () => {
    const { result } = renderHook(() => useStock(''), { wrapper: createWrapper() })
    expect(result.current.fetchStatus).toBe('idle')
  })
})

describe('useRecommendation', () => {
  it('fetches recommendation data', async () => {
    const { result } = renderHook(() => useRecommendation('AAPL'), { wrapper: createWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.action).toBe('BUY')
    expect(result.current.data?.scores).toBeDefined()
  })
})

describe('usePortfolio', () => {
  it('fetches portfolio with positions', async () => {
    const { result } = renderHook(() => usePortfolio(), { wrapper: createWrapper() })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.portfolio.positions).toHaveLength(1)
    expect(result.current.data?.portfolio.total_value).toBe(1750)
  })
})
