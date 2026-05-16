# Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (React + Vite + vis-network)                       │
│  - Architecture graph                                       │
│  - Blast-radius panel                                       │
│  - Tech debt heatmap                                        │
│  - Natural-language query interface                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP /api/*
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI (Python 3.11)                                      │
│                                                             │
│  api/routes.py            ← REST endpoints                  │
│      │                                                      │
│      ├──▶ analyzer/        ← DETERMINISTIC LAYER            │
│      │     scanner.py       walk repo                       │
│      │     ast_parser.py    AST → module records            │
│      │     graph_builder.py → NetworkX DiGraph              │
│      │     blast_radius.py  reverse transitive closure      │
│      │     tech_debt.py     complexity / cycle / coupling   │
│      │     flow_tracer.py   query → seed → bounded subgraph │
│      │                                                      │
│      └──▶ bob/             ← AI EXPLANATION LAYER           │
│            client.py        REST or CLI, w/ fallback        │
│            prompts.py       4 task-specific templates       │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP or subprocess
                           ▼
                  ┌─────────────────┐
                  │   IBM Bob       │
                  │  (local install)│
                  └─────────────────┘
```

## Data flow per request

### "Show me the architecture graph"

1. Frontend mounts → `GET /api/graph`
2. Routes return the pre-computed graph from `state` (populated at startup
   by `analyze_repo()` in `main.py`)
3. Frontend renders with vis-network, colored by domain, sized by LOC,
   debt score on each node

**Bob is not involved.** Structure comes from AST.

### "What's the blast radius of payments.processor?"

1. User clicks node → `GET /api/blast/payments.processor`
2. `compute_blast_radius()` walks the reverse graph from the target
3. Computes risk score from reach × coupling × cross-domain-spread
4. Returns structured factors that explain the score

**Bob is not involved.** Reach is graph theory.

### "What happens if we modernize the payment engine?" (Bob's specialty)

1. User clicks "Plan modernization" → `POST /api/modernize`
2. Backend runs blast radius (deterministic) + reads debt summary (deterministic)
3. Bundles both into the `PROMPT_MODERNIZATION` template
4. Calls `bob.complete(prompt)` → Bob returns an ordered plan with tradeoffs
5. Returns Bob's answer + the structured blast data to the frontend

**Bob is essential here** — the ordering + tradeoff narrative is exactly the
multi-step reasoning the deterministic layer can't do.

### "How does authentication work?" (Bob narrates a trace)

1. User types question → `POST /api/query`
2. `trace_flow()` does:
   - Expand query with synonyms
   - Score every module by name/source/function matches
   - Pick top-3 seeds
   - 2-hop BFS through the dependency graph
3. Backend extracts source snippets for those modules
4. Bundles into `PROMPT_FLOW_QUERY`
5. Bob narrates the flow step by step

**Bob is essential** for the narration. The retrieval is deterministic.

## Why this split matters

The brief in `PROJECT_BRIEF.md` explains the philosophy. In practice:

- We never ask Bob "what files implement payments?" — that's a graph query
- We never ask Bob to "compute the blast radius" — that's transitive closure
- We *do* ask Bob to write the human-readable narrative
- We *do* ask Bob to surface hidden business logic from raw source
- We *do* ask Bob to sequence a modernization plan with tradeoffs

The result is: fast, cheap, robust, and Bob is genuinely doing what only
Bob can do.

## State model

The backend is **single-tenant in-memory** — one repo loaded at a time,
held in a global `state` singleton (`backend/main.py`). This is fine for
a hackathon demo. Production would need:

- per-tenant workspaces
- background re-analysis on git push
- persistent graph storage (Neo4j or a flat-file cache)
- streaming Bob responses

## Bob client architecture

`bob/client.py` is a single seam. Two transport modes:

- **REST** (default): assumes an OpenAI-compatible POST endpoint on Bob.
  Adjust `_call_bob_rest()` if your install differs.
- **CLI**: invokes the local `bob` binary via subprocess.

If Bob is unreachable, every method has a deterministic fallback so the demo
never blanks. The fallbacks are not pretend-AI — they restate what the graph
already knows, in plain prose.

## Frontend architecture

Single-page React app. Three top-level views (tabs):

1. **Architecture** — graph + side panel
2. **Tech Debt** — heatmap + ranked hotspots
3. **Ask Bob** — query box + suggestion chips + result narrative

State is held in `App.jsx` and passed down. No Redux, no Zustand — kept
simple for hackathon velocity.

## Dependencies

Backend:
- `fastapi`, `uvicorn` — HTTP
- `pydantic` — schemas
- `networkx` — graph algorithms
- `httpx` — async Bob calls
- `python-dotenv` — config

Frontend:
- `react`, `react-dom`
- `vis-network`, `vis-data` — graph visualization
- `vite` — dev server + build
