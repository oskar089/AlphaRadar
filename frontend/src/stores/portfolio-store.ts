import { create } from 'zustand'

interface PortfolioUIState {
  isAddFormOpen: boolean
  toggleAddForm: () => void
}

export const usePortfolioUIStore = create<PortfolioUIState>((set) => ({
  isAddFormOpen: false,
  toggleAddForm: () => set((s) => ({ isAddFormOpen: !s.isAddFormOpen })),
}))
