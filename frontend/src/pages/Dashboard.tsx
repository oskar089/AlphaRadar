import { useNavigate } from 'react-router'
import { usePortfolio } from '@/hooks/use-portfolio'
import StockCard from '@/components/StockCard'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorMessage from '@/components/ErrorMessage'

export default function Dashboard() {
  const navigate = useNavigate()
  const { data, isLoading, error, refetch } = usePortfolio()

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} onRetry={refetch} />

  const portfolio = data?.portfolio
  const hasPositions = portfolio && portfolio.positions.length > 0

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Total Value</p>
          <p className="text-2xl font-bold text-white">
            ${hasPositions ? portfolio.total_value.toFixed(2) : '0.00'}
          </p>
        </div>
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-4">
          <p className="text-sm text-gray-400">Total P&L</p>
          <p className={`text-2xl font-bold ${hasPositions && portfolio.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {hasPositions ? `${portfolio.total_pnl >= 0 ? '+' : ''}${portfolio.total_pnl.toFixed(2)}` : '$0.00'}
          </p>
        </div>
      </div>

      {/* Positions */}
      {hasPositions ? (
        <div>
          <h2 className="mb-4 text-lg font-semibold text-white">Your Positions</h2>
          <div className="space-y-3">
            {portfolio.positions.map((pos) => (
              <StockCard
                key={pos.id}
                symbol={pos.symbol}
                name={pos.symbol}
                action="HOLD"
                score={0}
                onClick={() => navigate(`/stocks/${pos.symbol}`)}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-8 text-center">
          <p className="text-gray-400">No positions yet. Add your first position to get started.</p>
          <button
            onClick={() => navigate('/portfolio')}
            className="mt-4 rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500"
          >
            Go to Portfolio
          </button>
        </div>
      )}
    </div>
  )
}
