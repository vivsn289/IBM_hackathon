import { useMemo, useState } from 'react'

export default function Sidebar({ graph, debt, selected, onSelect }) {
  const [q, setQ] = useState('')

  const groups = useMemo(() => {
    if (!graph) return {}
    const byDomain = {}
    for (const n of graph.nodes) {
      if (q && !n.id.toLowerCase().includes(q.toLowerCase())) continue
      byDomain[n.domain] ||= []
      byDomain[n.domain].push(n)
    }
    // sort each domain by debt score desc
    for (const d of Object.keys(byDomain)) {
      byDomain[d].sort((a, b) => (b.debt_score ?? 0) - (a.debt_score ?? 0))
    }
    return byDomain
  }, [graph, q])

  return (
    <aside className="sidebar">
      <input
        className="search"
        placeholder="Filter modules…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <div className="module-list">
        {Object.keys(groups).sort().map((domain) => (
          <div key={domain} className="domain-group">
            <div className="domain-label" data-domain={domain}>{domain}</div>
            {groups[domain].map((n) => (
              <button
                key={n.id}
                className={`module-row ${selected === n.id ? 'selected' : ''}`}
                onClick={() => onSelect(n.id)}
                title={`${n.loc} LOC · debt ${n.debt_score?.toFixed?.(0) ?? 0}`}
              >
                <span className="module-name">{n.label}</span>
                <DebtPill score={n.debt_score} />
              </button>
            ))}
          </div>
        ))}
      </div>
    </aside>
  )
}

function DebtPill({ score }) {
  const s = score ?? 0
  let band = 'low'
  if (s >= 60) band = 'critical'
  else if (s >= 40) band = 'high'
  else if (s >= 20) band = 'medium'
  return <span className={`pill pill-${band}`}>{Math.round(s)}</span>
}
