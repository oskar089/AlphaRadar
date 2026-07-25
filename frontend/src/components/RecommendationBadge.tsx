const actionStyles: Record<string, string> = {
  BUY: 'bg-green-900 text-green-300',
  SELL: 'bg-red-900 text-red-300',
  HOLD: 'bg-yellow-900 text-yellow-300',
}

export default function RecommendationBadge({ action }: { action: string }) {
  const style = actionStyles[action] ?? 'bg-gray-800 text-gray-300'
  return (
    <span className={`inline-block rounded-full px-3 py-0.5 text-xs font-semibold ${style}`}>
      {action}
    </span>
  )
}
