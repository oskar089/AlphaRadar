import { useState } from 'react'
import { usePortfolio, useAddPosition, useDeletePosition } from '@/hooks/use-portfolio'
import PositionRow from '@/components/PositionRow'
import AddPositionForm from '@/components/AddPositionForm'
import LoadingSpinner from '@/components/LoadingSpinner'
import ErrorMessage from '@/components/ErrorMessage'
import type { PositionCreate } from '@/lib/types'

export default function Portfolio() {
  const { data, isLoading, error, refetch } = usePortfolio()
  const addPosition = useAddPosition()
  const deletePosition = useDeletePosition()
  const [showForm, setShowForm] = useState(false)

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message={error.message} onRetry={refetch} />

  const portfolio = data?.portfolio
  const hasPositions = portfolio && portfolio.positions.length > 0

  function handleAdd(position: PositionCreate) {
    addPosition.mutate(position, {
      onSuccess: () => setShowForm(false),
    })
  }

  function handleDelete(id: number) {
    if (confirm('Remove this position?')) {
      deletePosition.mutate(id)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Portfolio</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-500"
        >
          {showForm ? 'Cancel' : 'Add Position'}
        </button>
      </div>

      {showForm && (
        <AddPositionForm
          onSubmit={handleAdd}
          disabled={addPosition.isPending}
        />
      )}

      {hasPositions ? (
        <div className="overflow-hidden rounded-lg border border-gray-800">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-900 text-gray-400">
              <tr>
                <th className="px-4 py-3">Symbol</th>
                <th className="px-4 py-3">Qty</th>
                <th className="px-4 py-3">Avg Price</th>
                <th className="px-4 py-3">Current</th>
                <th className="px-4 py-3">P&L</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {portfolio.positions.map((pos) => (
                <PositionRow key={pos.id} position={pos} onDelete={handleDelete} />
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="rounded-lg border border-gray-800 bg-gray-900 p-8 text-center">
          <p className="text-gray-400">No positions yet. Click "Add Position" to get started.</p>
        </div>
      )}
    </div>
  )
}
