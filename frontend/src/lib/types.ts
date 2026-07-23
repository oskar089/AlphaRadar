export interface StockResponse {
  symbol: string
  name: string
  exchange: string
}

export interface AnalysisScoresResponse {
  technical: number
  fundamental: number
  sentiment: number
  final_score: number
}

export interface RecommendationResponse {
  symbol: string
  action: string
  score: number
  confidence: number
  reasoning: string
  scores: AnalysisScoresResponse
}

export interface PositionCreate {
  symbol: string
  quantity: number
  avg_buy_price: number
}

export interface PositionResponse extends PositionCreate {
  id: number
  current_price: number
}

export interface PortfolioData {
  name: string
  positions: PositionResponse[]
  total_value: number
  total_pnl: number
  storage: string
}

export interface PortfolioResponse {
  portfolio: PortfolioData
}

export interface ApiError {
  detail: string
}
