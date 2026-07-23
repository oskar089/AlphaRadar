import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { PortfolioResponse, PositionCreate, PositionResponse } from '@/lib/types'

export function usePortfolio() {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: () => apiClient.get<PortfolioResponse>('/api/portfolio'),
  })
}

export function useAddPosition() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (position: PositionCreate) =>
      apiClient.post<PositionResponse>('/api/portfolio/positions', position),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })
}

export function useDeletePosition() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) =>
      apiClient.delete(`/api/portfolio/positions/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
    },
  })
}
