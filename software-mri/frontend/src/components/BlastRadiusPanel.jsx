import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function BlastRadiusPanel({ selected, onSelect }) {
  const [blast, setBlast] = useState(null)
  const [explain, setExplain] = useState(null)
  const [modernize, setModernize] = useState(null)
  const [hidden, setHidden] = useState(null)
  const [loading, setLoading] = useState({})

  useEffect(() => {
    setBlast(null); setExplain(null); setModernize(null); setHidden(null)
    if (!selected) return
    setLoading({ blast: true, explain: true })
    api.blast(selected).then(setBlast).catch(console.error).finally(() => setLoading(l => ({ ...l, blast: false })))
    api.explain(selected).then(setExplain).catch(console.error).finally(() => setLoading(l => ({ ...l, explain: false })))
  }, [selected])

  if (!selected) {
    return (
      <aside className="panel">
        <div className="panel-empty">
          <h3>Select a module</h3>
          <p>Click any node in the graph to see its blast radius, ask Bob to explain it, plan a modernization, or recover its hidden business logic.</p>
        </div>
      </aside>
    )
  }

  const askModernization = () => {
    setLoading(l => ({ ...l, modernize: true }))
    api.modernize(selected).then(setModernize).catch(console.error).finally(() => setLoading(l => ({ ...l, modernize: false })))
  }
  const askHidden = () => {
    setLoading(l => ({ ...l, hidden: true }))
    api.hiddenLogic(selected).then(setHidden).catch(console.error).finally(() => setLoading(l => ({ ...l, hidden: false })))
  }

  return (
    <aside className="panel">
      <header className="panel-header">
        <h3>{selected}</h3>
        {blast && <span className={`risk-band band-${blast.risk_band}`}>{blast.risk_band} · {blast.risk_score}</span>}
      </header>

      <section className="panel-section">
        <h4>Blast radius</h4>
        {loading.blast && <em>computing…</em>}
        {blast && (
          <>
            <div className="metric-grid">
              <Metric label="Direct" value={blast.metrics.direct_count} />
              <Metric label="Transitive" value={blast.metrics.transitive_count} />
              <Metric label="Domains" value={blast.metrics.cross_domain_count} />
            </div>
            <details className="details">
              <summary>{blast.transitive_dependents.length} affected modules</summary>
              <ul className="dep-list">
                {blast.transitive_dependents.map((m) => (
                  <li key={m}><button className="link" onClick={() => onSelect(m)}>{m}</button></li>
                ))}
              </ul>
            </details>
            <ul className="factor-list">
              {blast.explanation_factors.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </>
        )}
      </section>

      <section className="panel-section">
        <h4>Bob explains</h4>
        {loading.explain && <em>asking Bob…</em>}
        {explain && <pre className="bob-output">{explain.answer}</pre>}
      </section>

      <section className="panel-section">
        <div className="panel-actions">
          <button className="btn" onClick={askModernization} disabled={loading.modernize}>
            {loading.modernize ? 'Bob is planning…' : 'Plan modernization with Bob'}
          </button>
          <button className="btn btn-ghost" onClick={askHidden} disabled={loading.hidden}>
            {loading.hidden ? 'Recovering…' : 'Recover hidden business logic'}
          </button>
        </div>
        {modernize && (
          <div className="bob-card">
            <div className="bob-card-title">Modernization plan</div>
            <pre className="bob-output">{modernize.answer}</pre>
          </div>
        )}
        {hidden && (
          <div className="bob-card">
            <div className="bob-card-title">Hidden business logic</div>
            <pre className="bob-output">{hidden.answer}</pre>
          </div>
        )}
      </section>
    </aside>
  )
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <div className="metric-value">{value}</div>
      <div className="metric-label">{label}</div>
    </div>
  )
}
