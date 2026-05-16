import { useState } from 'react'
import { api } from '../api/client'

const SUGGESTIONS = [
  'How does authentication work?',
  'Where does payment validation happen?',
  'What happens if we modernize the payment engine?',
  'How is tax calculated on invoices?',
  'How does fraud screening interact with payments?',
]

export default function QueryPanel({ onSelect }) {
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const ask = async (text) => {
    const query = text ?? q
    if (!query.trim()) return
    setLoading(true); setError(null); setResult(null)
    try {
      const r = await api.query(query)
      setResult(r)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="query-page">
      <h2>Ask Bob about the codebase</h2>
      <p className="muted">
        Bob reads the deterministic flow tracer's output and narrates how the
        relevant modules actually execute.
      </p>

      <div className="query-bar">
        <input
          className="query-input"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && ask()}
          placeholder='e.g. "What happens if we modernize the payment engine?"'
        />
        <button className="btn" onClick={() => ask()} disabled={loading}>
          {loading ? 'Bob is thinking…' : 'Ask Bob'}
        </button>
      </div>

      <div className="suggestions">
        {SUGGESTIONS.map((s) => (
          <button key={s} className="chip" onClick={() => { setQ(s); ask(s) }}>{s}</button>
        ))}
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="query-result">
          <div className="bob-card">
            <div className="bob-card-title">Bob's narrative</div>
            <pre className="bob-output">{result.answer}</pre>
          </div>

          {result.structured && (
            <div className="trace-card">
              <h4>Modules in the trace</h4>
              <p className="muted">
                Seeds: {result.structured.seeds.map((s) => (
                  <button key={s} className="link" onClick={() => onSelect(s)}>{s}</button>
                )).reduce((acc, el, i) => i === 0 ? [el] : [...acc, ', ', el], [])}
              </p>
              <ul>
                {result.structured.modules.map((m) => (
                  <li key={m}>
                    <button className="link" onClick={() => onSelect(m)}>{m}</button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
