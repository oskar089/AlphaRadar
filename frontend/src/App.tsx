import { Routes, Route } from 'react-router'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import StockDetail from './pages/StockDetail'
import Portfolio from './pages/Portfolio'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/stocks/:symbol" element={<StockDetail />} />
        <Route path="/portfolio" element={<Portfolio />} />
      </Routes>
    </Layout>
  )
}
