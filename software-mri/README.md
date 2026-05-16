# Software MRI · RepoLens AI

> **Architectural observability for software systems.**
> Powered by **IBM Bob**.

Software MRI is a repository cognition platform. It takes a legacy codebase that
"nobody fully understands anymore" and turns it into an observable operational
structure — architecture graphs, execution flows, blast-radius prediction,
technical-debt heatmaps, and modernization intelligence.

This repo is our IBM Bob Hackathon submission for the
**"Turn idea into impact faster"** challenge.

---

## The Problem We're Solving

Most enterprise modernization projects take 2–10 years. The bottleneck isn't
writing new code — it's **understanding what the old code already does** without
breaking compliance, business logic, or institutional knowledge.

Current tools give you code search and static diagrams. They don't give you a
*cognition layer*. We do.

See [`docs/PROJECT_BRIEF.md`](docs/PROJECT_BRIEF.md) for the full thesis.

---

## What This Does

Point Software MRI at any Python repository and within seconds you get:

1. **Architecture graph** — every module, every dependency, color-coded by domain
2. **Execution flow tracing** — ask "how does authentication work?" in plain English
3. **Blast radius prediction** — "what breaks if we modernize the payment engine?"
4. **Technical debt heatmap** — fragile, cyclic, oversized, and tightly-coupled regions
5. **Modernization sequencing** — Bob recommends a safe, incremental migration order
6. **Institutional knowledge recovery** — Bob explains undocumented modules in plain English

The deterministic analysis layer is what *finds* the structure. **Bob** is what
*explains* it — turning graphs into narratives a non-engineer can read.

---

## How IBM Bob Is Used (Critical for Judging)

Bob is integrated at four meaningful points in the pipeline. Every integration
point uses Bob for what only an AI partner can do — reading intent, explaining
logic, summarizing complete repository context. See
[`docs/BOB_INTEGRATION.md`](docs/BOB_INTEGRATION.md) for full details.

| Stage | Bob's Role | Why Bob Specifically |
|-------|-----------|----------------------|
| Module summarization | Reads each module's source + its neighbors and writes a plain-English description of what it does | Bob reads complete repository context |
| Execution-flow Q&A | User asks "how does X work?", Bob traces using the dependency graph + AST and narrates the flow | Bob understands intent |
| Modernization advice | Bob reviews blast radius + debt scores and proposes a safe extraction order | Bob automates complex multi-step reasoning |
| Hidden-logic recovery | Bob reads legacy modules and surfaces the implicit business rules they encode | Bob explains logic with clarity |

---

## Quick Start

```bash
# 1. Clone and enter
cd software-mri

# 2. One-shot setup (creates venv, installs everything, builds frontend)
bash scripts/setup.sh

# 3. Configure Bob (see docs/BOB_INTEGRATION.md)
cp .env.example .env
# Edit .env and set your Bob endpoint / credentials

# 4. Run backend (terminal 1)
bash scripts/run-backend.sh

# 5. Run frontend (terminal 2)
bash scripts/run-frontend.sh

# 6. Open http://localhost:5173
#    The sample legacy banking codebase is pre-loaded.
```

If Bob isn't configured yet, the app still runs — Bob calls fall back to
deterministic explanations so you can develop and demo the rest of the
pipeline. See `backend/bob/client.py`.

---

## Repository Layout

```
software-mri/
├── backend/                FastAPI + static analysis + Bob client
│   ├── main.py             Entrypoint
│   ├── analyzer/           Deterministic intelligence layer
│   │   ├── scanner.py        Find source files
│   │   ├── ast_parser.py     Parse Python AST, extract imports/calls
│   │   ├── graph_builder.py  Build NetworkX dependency graph
│   │   ├── blast_radius.py   Reverse transitive closure
│   │   ├── tech_debt.py      Complexity, cycles, coupling metrics
│   │   └── flow_tracer.py    Execution flow reconstruction
│   ├── bob/                IBM Bob integration
│   │   ├── client.py         Bob API client w/ deterministic fallback
│   │   └── prompts.py        Prompt templates for each task
│   └── api/                REST endpoints
├── frontend/               React + Vite + vis-network
│   └── src/components/       Graph, blast-radius, debt, query panels
├── sample-repo/            A deliberately gnarly fake legacy banking system
│   ├── core/, auth/, billing/, payments/, reporting/, legacy/
│   └── (contains intentional cycles, tight coupling, dead code, cobol bridge)
├── docs/
│   ├── PROJECT_BRIEF.md      The thesis
│   ├── ARCHITECTURE.md       Technical architecture
│   ├── BOB_INTEGRATION.md    How Bob is wired in
│   ├── DEMO_SCRIPT.md        2-minute demo narration
│   └── HACKATHON_NOTES.md    Submission checklist, scope reality, what's next
└── scripts/                setup, run-backend, run-frontend
```

---

## Demo Path

For judges and for our own demo:

1. Open `http://localhost:5173`
2. The dependency graph of the sample banking system renders. Note `payments/`
   is in a cycle with `billing/` and `legacy/old_gateway.py` is a debt hotspot.
3. Click `payments/processor.py` → blast-radius panel lights up 14 modules.
4. In the query box, ask **"What happens if we modernize the payment engine?"**
5. Bob responds with a narrated migration order. Tradeoffs are listed.
6. Switch to the Tech Debt tab → heatmap shows `legacy/` glowing red.
7. Click `legacy/old_gateway.py` → Bob explains the hidden business rules
   (currency rounding edge cases, regulatory branches) that aren't documented anywhere.

Closing line: *"Modernization should not require losing institutional memory."*

See [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md) for the full narration.

---

## Scope Honesty

This is a hackathon prototype. What's real:

- ✅ Static analysis is real (AST-based, works on any Python repo)
- ✅ Graph, blast radius, cycles, debt metrics — all computed, not faked
- ✅ Bob integration architecture is real and pluggable
- ✅ Sample repo is realistic enough to show the pattern

What's intentionally out of scope for the hackathon:

- ❌ Multi-language support (Python only — COBOL/Java are mocked in sample)
- ❌ Full IDE plugin (CLI + web UI only)
- ❌ Auth, multi-tenant, persistence beyond in-memory
- ❌ Production-grade graph layout at >5k modules

See [`docs/HACKATHON_NOTES.md`](docs/HACKATHON_NOTES.md).

---

## Team Notes

- Use `docs/DEMO_SCRIPT.md` to rehearse — the demo is what wins, not the code.
- Bob's response quality during the demo is critical. Pre-test the four canned
  questions in `docs/DEMO_SCRIPT.md` against your Bob instance before pitching.
- If Bob is slow or unavailable, the deterministic fallback in
  `backend/bob/client.py` will still produce a coherent answer.
