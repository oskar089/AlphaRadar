import { create } from 'zustand'

interface StockUIState {
  selectedSymbol: string
  setSelectedSymbol: (symbol: string) => void
}

export const useStockStore = create<StockUIState>((set) => ({
  selectedSymbol: '',
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
}))
