import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import type { RecommendationResponse } from '@/lib/types'

export function useRecommendation(symbol: string) {
  return useQuery({
    queryKey: ['recommendation', symbol],
    queryFn: () =>
      apiClient.get<RecommendationResponse>(`/api/recommendations/${symbol}`),
    staleTime: 5 * 60 * 1000, // 5 min
    enabled: !!symbol,
  })
}
