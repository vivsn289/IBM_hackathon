export default function TechDebtPanel({ debt, graph, onSelect }) {
  if (!debt || !debt.summary) return <div className="panel-empty">No debt data.</div>
  const { summary, modules } = debt

  return (
    <div className="debt-page">
      <div className="debt-header">
        <h2>Technical Debt</h2>
        <div className="debt-stats">
          <span>Avg score: <strong>{summary.average_score}</strong> / 100</span>
          <span>Cycles: <strong>{summary.cycle_count}</strong></span>
          <span>Modules in cycles: <strong>{summary.modules_in_cycles}</strong></span>
        </div>
      </div>

      <div className="debt-split">
        <div className="debt-heatmap">
          <h3>Heatmap</h3>
          <div className="heatmap-grid">
            {Object.entries(modules)
              .sort(([, a], [, b]) => b.score - a.score)
              .map(([name, m]) => (
                <button
                  key={name}
                  className="heat-cell"
                  style={{ background: heatColor(m.score) }}
                  onClick={() => onSelect(name)}
                  title={`${name}\nscore ${m.score}\n${m.factors.join('\n')}`}
                >
                  <span className="heat-name">{name.split('.').slice(-1)[0]}</span>
                  <span className="heat-score">{Math.round(m.score)}</span>
                </button>
              ))}
          </div>
        </div>

        <div className="debt-hotspots">
          <h3>Top hotspots</h3>
          <ol className="hotspot-list">
            {summary.hotspots.map((h) => (
              <li key={h.module}>
                <button className="link" onClick={() => onSelect(h.module)}>{h.module}</button>
                <span className="hotspot-score">{h.score}</span>
                <ul className="factor-list">
                  {h.factors.map((f, i) => <li key={i}>{f}</li>)}
                </ul>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </div>
  )
}

function heatColor(score) {
  // green (low) -> yellow (mid) -> red (high)
  const s = Math.max(0, Math.min(100, score)) / 100
  const r = Math.round(255 * Math.min(1, s * 1.6))
  const g = Math.round(200 * Math.max(0, 1 - s * 1.2))
  return `rgb(${r}, ${g}, 80)`
}
