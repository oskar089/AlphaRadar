import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { StockResponse } from '@/lib/types'

export function useStock(symbol: string) {
  return useQuery({
    queryKey: ['stock', symbol],
    queryFn: () => apiClient.get<StockResponse>(`/api/stocks/${symbol}`),
    enabled: !!symbol,
  })
}
