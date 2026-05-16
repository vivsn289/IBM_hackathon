export default function Header({ stats, debtSummary, tab, onTab }) {
  return (
    <header className="header">
      <div className="brand">
        <div className="brand-title">Software MRI</div>
        <div className="brand-sub">Architectural observability · powered by IBM Bob</div>
      </div>

      <div className="stats">
        <Stat label="Modules" value={stats?.modules} />
        <Stat label="Dependencies" value={stats?.dependencies} />
        <Stat label="Cycles" value={stats?.cycles_detected} warn={stats?.cycles_detected > 0} />
        <Stat label="Avg debt" value={debtSummary?.average_score?.toFixed?.(1) ?? '—'} />
      </div>

      <nav className="tabs">
        <button className={tab==='architecture'?'tab active':'tab'} onClick={() => onTab('architecture')}>Architecture</button>
        <button className={tab==='debt'?'tab active':'tab'} onClick={() => onTab('debt')}>Tech Debt</button>
        <button className={tab==='query'?'tab active':'tab'} onClick={() => onTab('query')}>Ask Bob</button>
      </nav>
    </header>
  )
}

function Stat({ label, value, warn }) {
  return (
    <div className={`stat ${warn ? 'stat-warn' : ''}`}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}
