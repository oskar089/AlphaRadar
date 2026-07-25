import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { createElement } from 'react'
import { BrowserRouter } from 'react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from '@/components/Layout'
import RecommendationBadge from '@/components/RecommendationBadge'
import StockCard from '@/components/StockCard'
import PositionRow from '@/components/PositionRow'
import AddPositionForm from '@/components/AddPositionForm'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorMessage from '@/components/ErrorMessage'

function withProviders(children: React.ReactNode) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return createElement(
    QueryClientProvider,
    { client: queryClient },
    createElement(BrowserRouter, null, children),
  )
}

describe('Layout', () => {
  it('renders navigation and children', () => {
    const { getByText } = render(
      withProviders(createElement(Layout, null, createElement('div', null, 'Content'))),
    )
    expect(getByText('AlphaRadar')).toBeInTheDocument()
    expect(getByText('Dashboard')).toBeInTheDocument()
    expect(getByText('Portfolio')).toBeInTheDocument()
    expect(getByText('Content')).toBeInTheDocument()
  })
})

describe('RecommendationBadge', () => {
  it('renders BUY badge', () => {
    const { getByText } = render(createElement(RecommendationBadge, { action: 'BUY' }))
    expect(getByText('BUY')).toBeInTheDocument()
  })

  it('renders SELL badge', () => {
    const { getByText } = render(createElement(RecommendationBadge, { action: 'SELL' }))
    expect(getByText('SELL')).toBeInTheDocument()
  })

  it('renders HOLD badge', () => {
    const { getByText } = render(createElement(RecommendationBadge, { action: 'HOLD' }))
    expect(getByText('HOLD')).toBeInTheDocument()
  })
})

describe('StockCard', () => {
  it('renders symbol, name, and score', () => {
    const { getByText } = render(
      createElement(StockCard, {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        action: 'BUY',
        score: 0.75,
        onClick: () => {},
      }),
    )
    expect(getByText('AAPL')).toBeInTheDocument()
    expect(getByText('Apple Inc.')).toBeInTheDocument()
    expect(getByText('BUY')).toBeInTheDocument()
  })
})

describe('PositionRow', () => {
  it('renders position data with P&L', () => {
    const { getByText } = render(
      createElement(PositionRow, {
        position: { id: 1, symbol: 'AAPL', quantity: 10, avg_buy_price: 150, current_price: 175 },
        onDelete: () => {},
      }),
    )
    expect(getByText('AAPL')).toBeInTheDocument()
    expect(getByText('10')).toBeInTheDocument()
    expect(getByText('+250.00')).toBeInTheDocument()
  })
})

describe('AddPositionForm', () => {
  it('renders form fields', () => {
    const { getByPlaceholderText } = render(
      createElement(AddPositionForm, { onSubmit: () => {} }),
    )
    expect(getByPlaceholderText('AAPL')).toBeInTheDocument()
    expect(getByPlaceholderText('10')).toBeInTheDocument()
    expect(getByPlaceholderText('150.00')).toBeInTheDocument()
  })
})

describe('LoadingSpinner', () => {
  it('renders without crashing', () => {
    const { container } = render(createElement(LoadingSpinner))
    expect(container.firstChild).toBeInTheDocument()
  })
})

describe('ErrorMessage', () => {
  it('renders message', () => {
    const { getByText } = render(createElement(ErrorMessage, { message: 'Something went wrong' }))
    expect(getByText('Something went wrong')).toBeInTheDocument()
  })

  it('renders retry button when onRetry provided', () => {
    const { getByText } = render(
      createElement(ErrorMessage, { message: 'Error', onRetry: () => {} }),
    )
    expect(getByText('Retry')).toBeInTheDocument()
  })
})
