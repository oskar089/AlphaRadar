import RecommendationBadge from './RecommendationBadge'

interface StockCardProps {
  symbol: string
  name: string
  action: string
  score: number
  onClick: () => void
}

export default function StockCard({ symbol, name, action, score, onClick }: StockCardProps) {
  return (
    <button
      onClick={onClick}
      className="w-full rounded-lg border border-gray-800 bg-gray-900 p-4 text-left transition-colors hover:border-gray-600"
    >
      <div className="flex items-center justify-between">
        <div>
          <span className="text-lg font-bold text-white">{symbol}</span>
          <span className="ml-2 text-sm text-gray-400">{name}</span>
        </div>
        <RecommendationBadge action={action} />
      </div>
      <div className="mt-2 text-sm text-gray-400">
        Score: <span className="font-medium text-white">{score.toFixed(2)}</span>
      </div>
    </button>
  )
}
