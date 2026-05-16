import { useEffect, useState } from 'react'
import { api } from './api/client'
import Header from './components/Header'
import ArchitectureGraph from './components/ArchitectureGraph'
import BlastRadiusPanel from './components/BlastRadiusPanel'
import TechDebtPanel from './components/TechDebtPanel'
import QueryPanel from './components/QueryPanel'
import Sidebar from './components/Sidebar'

export default function App() {
  const [graph, setGraph] = useState(null)
  const [debt, setDebt] = useState(null)
  const [selected, setSelected] = useState(null)
  const [tab, setTab] = useState('architecture') // architecture | debt | query
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    Promise.all([api.graph(), api.debt()])
      .then(([g, d]) => {
        if (!alive) return
        setGraph(g)
        setDebt(d)
        setLoading(false)
      })
      .catch((e) => {
        if (!alive) return
        setError(String(e))
        setLoading(false)
      })
    return () => { alive = false }
  }, [])

  if (loading) return <div className="loading">Analyzing repository…</div>
  if (error)   return <div className="error">Backend error: {error}<br/>Is the FastAPI server running on :8000?</div>

  return (
    <div className="app">
      <Header
        stats={graph.stats}
        debtSummary={debt?.summary}
        tab={tab}
        onTab={setTab}
      />
      <div className="layout">
        <Sidebar
          graph={graph}
          debt={debt}
          selected={selected}
          onSelect={setSelected}
        />
        <main className="main">
          {tab === 'architecture' && (
            <div className="split">
              <ArchitectureGraph
                graph={graph}
                selected={selected}
                onSelect={setSelected}
              />
              <BlastRadiusPanel
                selected={selected}
                onSelect={setSelected}
              />
            </div>
          )}
          {tab === 'debt' && (
            <TechDebtPanel
              debt={debt}
              graph={graph}
              onSelect={(m) => { setSelected(m); setTab('architecture') }}
            />
          )}
          {tab === 'query' && (
            <QueryPanel onSelect={(m) => { setSelected(m); setTab('architecture') }} />
          )}
        </main>
      </div>
    </div>
  )
}
