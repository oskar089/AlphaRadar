import { useState, type FormEvent } from 'react'
import type { PositionCreate } from '@/lib/types'

interface AddPositionFormProps {
  onSubmit: (position: PositionCreate) => void
  disabled?: boolean
}

export default function AddPositionForm({ onSubmit, disabled }: AddPositionFormProps) {
  const [symbol, setSymbol] = useState('')
  const [quantity, setQuantity] = useState('')
  const [avgBuyPrice, setAvgBuyPrice] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})

  function validate(): boolean {
    const newErrors: Record<string, string> = {}
    if (!symbol.trim()) newErrors.symbol = 'Symbol is required'
    if (!quantity || Number(quantity) <= 0) newErrors.quantity = 'Must be greater than 0'
    if (!avgBuyPrice || Number(avgBuyPrice) <= 0) newErrors.avgBuyPrice = 'Must be greater than 0'
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!validate()) return
    onSubmit({
      symbol: symbol.trim().toUpperCase(),
      quantity: Number(quantity),
      avg_buy_price: Number(avgBuyPrice),
    })
    setSymbol('')
    setQuantity('')
    setAvgBuyPrice('')
    setErrors({})
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-gray-800 bg-gray-900 p-4">
      <h3 className="text-lg font-semibold text-white">Add Position</h3>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="mb-1 block text-sm text-gray-400">Symbol</label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="w-full rounded border border-gray-700 bg-gray-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            placeholder="AAPL"
          />
          {errors.symbol && <p className="mt-1 text-xs text-red-400">{errors.symbol}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-400">Quantity</label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            className="w-full rounded border border-gray-700 bg-gray-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            placeholder="10"
            min="1"
          />
          {errors.quantity && <p className="mt-1 text-xs text-red-400">{errors.quantity}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm text-gray-400">Avg Buy Price</label>
          <input
            type="number"
            value={avgBuyPrice}
            onChange={(e) => setAvgBuyPrice(e.target.value)}
            className="w-full rounded border border-gray-700 bg-gray-800 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
            placeholder="150.00"
            step="0.01"
            min="0.01"
          />
          {errors.avgBuyPrice && <p className="mt-1 text-xs text-red-400">{errors.avgBuyPrice}</p>}
        </div>
      </div>
      <button
        type="submit"
        disabled={disabled}
        className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500 disabled:opacity-50"
      >
        Add Position
      </button>
    </form>
  )
}
