import type { PositionResponse } from '@/lib/types'

interface PositionRowProps {
  position: PositionResponse
  onDelete: (id: number) => void
}

export default function PositionRow({ position, onDelete }: PositionRowProps) {
  const pnl = (position.current_price - position.avg_buy_price) * position.quantity
  const pnlColor = pnl >= 0 ? 'text-green-400' : 'text-red-400'

  return (
    <tr className="border-b border-gray-800">
      <td className="px-4 py-3 font-bold text-white">{position.symbol}</td>
      <td className="px-4 py-3 text-gray-300">{position.quantity}</td>
      <td className="px-4 py-3 text-gray-300">${position.avg_buy_price.toFixed(2)}</td>
      <td className="px-4 py-3 text-gray-300">${position.current_price.toFixed(2)}</td>
      <td className={`px-4 py-3 font-medium ${pnlColor}`}>
        {pnl >= 0 ? '+' : ''}{pnl.toFixed(2)}
      </td>
      <td className="px-4 py-3">
        <button
          onClick={() => onDelete(position.id)}
          className="rounded bg-red-900 px-3 py-1 text-xs text-red-300 transition-colors hover:bg-red-800"
        >
          Delete
        </button>
      </td>
    </tr>
  )
}
