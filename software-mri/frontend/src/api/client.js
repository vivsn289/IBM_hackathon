// Thin wrapper around fetch. All calls go through the Vite proxy to FastAPI.

const J = (method, path, body) =>
  fetch(`/api${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  }).then(async (r) => {
    if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
    return r.json()
  })

export const api = {
  graph: () => J('GET', '/graph'),
  debt: () => J('GET', '/debt'),
  blast: (mod) => J('GET', `/blast/${encodeURIComponent(mod)}`),
  query: (q) => J('POST', '/query', { query: q }),
  modernize: (target) => J('POST', '/modernize', { target }),
  explain: (mod) => J('GET', `/explain/${encodeURIComponent(mod)}`),
  hiddenLogic: (mod) => J('GET', `/hidden-logic/${encodeURIComponent(mod)}`),
  analyze: (path) => J('POST', '/analyze', { path }),
}
