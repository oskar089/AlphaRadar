import { useParams, useNavigate } from 'react-router'
import { useStock } from '@/hooks/use-stock'
import { useRecommendation } from '@/hooks/use-recommendation'
import RecommendationBadge from '@/components/RecommendationBadge'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorMessage from '@/components/ErrorMessage'

export default function StockDetail() {
  const { symbol } = useParams<{ symbol: string }>()
  const navigate = useNavigate()
  const stockQuery = useStock(symbol ?? '')
  const recQuery = useRecommendation(symbol ?? '')

  const isLoading = stockQuery.isLoading || recQuery.isLoading
  const error = stockQuery.error || recQuery.error

  if (isLoading) return <LoadingSpinner />
  if (error) {
    const isNotFound = error.message.includes('not found')
    return (
      <div className="space-y-4">
        <ErrorMessage
          message={isNotFound ? `Symbol "${symbol}" not found` : error.message}
          onRetry={() => { stockQuery.refetch(); recQuery.refetch() }}
        />
        <button
          onClick={() => navigate('/')}
          className="text-sm text-blue-400 hover:text-blue-300"
        >
          Back to Dashboard
        </button>
      </div>
    )
  }

  const stock = stockQuery.data
  const rec = recQuery.data

  return (
    <div className="space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-blue-400 hover:text-blue-300"
      >
        Back
      </button>

      {stock && (
        <div>
          <h1 className="text-2xl font-bold text-white">{stock.symbol}</h1>
          <p className="text-gray-400">{stock.name} &middot; {stock.exchange}</p>
        </div>
      )}

      {rec && (
        <div className="space-y-4 rounded-lg border border-gray-800 bg-gray-900 p-6">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-white">Recommendation</h2>
            <RecommendationBadge action={rec.action} />
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Score</span>
              <p className="text-white">{rec.score.toFixed(2)}</p>
            </div>
            <div>
              <span className="text-gray-400">Confidence</span>
              <p className="text-white">{(rec.confidence * 100).toFixed(0)}%</p>
            </div>
          </div>

          <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-400">Scores Breakdown</h3>
            <div className="grid grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Technical</span>
                <p className="text-white">{rec.scores.technical.toFixed(2)}</p>
              </div>
              <div>
                <span className="text-gray-500">Fundamental</span>
                <p className="text-white">{rec.scores.fundamental.toFixed(2)}</p>
              </div>
              <div>
                <span className="text-gray-500">Sentiment</span>
                <p className="text-white">{rec.scores.sentiment.toFixed(2)}</p>
              </div>
              <div>
                <span className="text-gray-500">Final</span>
                <p className="text-white">{rec.scores.final_score.toFixed(2)}</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-400">Reasoning</h3>
            <p className="mt-1 text-sm text-gray-300">{rec.reasoning}</p>
          </div>
        </div>
      )}
    </div>
  )
}
