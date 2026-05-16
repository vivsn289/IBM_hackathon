# How IBM Bob Is Used

> **The hackathon rules state: "All submissions must clearly demonstrate how
> IBM Bob is used in the solution. Projects that do not show meaningful use
> of Bob may be disqualified."**
>
> This document is the proof.

## Summary

Software MRI integrates Bob at **four task-specific points**, each one
mapped to a distinct prompt template (`backend/bob/prompts.py`) and a
distinct API endpoint. Every integration is doing work that *only* an
AI partner that "reads complete repository context and explains logic
with clarity" can do well.

| # | Bob task | Endpoint | Prompt template | Why Bob specifically |
|---|----------|----------|-----------------|----------------------|
| 1 | Module summarization | `GET /api/explain/{module}` | `PROMPT_EXPLAIN_MODULE` | Reads code + neighbors in context, produces plain-English summary |
| 2 | Execution-flow Q&A | `POST /api/query` | `PROMPT_FLOW_QUERY` | Narrates a multi-module flow from intent + structured trace |
| 3 | Modernization planning | `POST /api/modernize` | `PROMPT_MODERNIZATION` | Multi-step reasoning over risk metrics → ordered plan with tradeoffs |
| 4 | Hidden-logic recovery | `GET /api/hidden-logic/{module}` | `PROMPT_HIDDEN_LOGIC` | Surfaces implicit business rules — the *institutional knowledge* problem |

Each one of these is unblocked by Bob's distinctive capabilities and is
genuinely hard for deterministic code to do well.

---

## 1. Module summarization

**What:** When a user clicks any module, Bob produces a 4–6 sentence
plain-English summary of what that module does in the *business* sense
(not just the code).

**Input to Bob:**
- The full source of the selected module
- A short description of its closest in-repo neighbors (importers + imported)
- The instruction to explain *purpose*, not list functions

**Why Bob:** Reading a module *in the context of its neighbors* and
producing a tight business-level summary is exactly the work Bob is
positioned to do well. A regex or symbol-graph cannot summarize "this
module owns settlement for Swiss-franc payments because of a 1996 COBOL
migration."

**Where in the code:**
- Prompt: `backend/bob/prompts.py` → `PROMPT_EXPLAIN_MODULE`
- Client method: `BobClient.explain_module()` in `backend/bob/client.py`
- API: `routes.py` → `get_explain()`

---

## 2. Execution-flow Q&A

**What:** User asks a natural-language question like *"how does payment
validation work?"* — Bob narrates the answer using the modules that
actually implement it.

**Input to Bob:**
- The user's question (intent)
- The seed modules our deterministic flow tracer matched
- The 2-hop subgraph reachable from the seeds
- Source snippets of the modules in the subgraph
- Instruction to walk the flow in execution order, calling out entry
  points, validation, business decisions, state mutations, and
  compliance branches

**Why Bob:** This is the textbook "Bob understands intent and explains
logic with clarity" case. We *retrieve* the relevant code deterministically
(graph + AST), then Bob narrates. Bob never has to guess which files are
involved — but it has to write the explanation, which no graph algorithm
can do.

**Where:**
- Prompt: `PROMPT_FLOW_QUERY`
- Client method: `BobClient.answer_flow_query()`
- API: `routes.py` → `post_query()`

---

## 3. Modernization planning

**What:** Given a target module, Bob proposes a safe, incremental migration
plan — ordered, with tradeoffs, with parallel steps flagged, with the
highest-risk step called out.

**Input to Bob:**
- The blast radius result (risk band, score, direct & transitive
  dependents, affected domains, factor list)
- Repo-wide debt hotspots
- Instruction to produce an ordered plan, *not* a full rewrite

**Why Bob:** This is multi-step reasoning over structured data, exactly
what the challenge description says Bob excels at ("automates complex
transformations, streamlines multi-step work"). Producing a coherent
ordered plan with tradeoffs requires:
- Understanding what each module does
- Reasoning about coupling between them
- Sequencing extractions to minimize blast radius at each step
- Knowing which extractions enable others

A deterministic algorithm can compute risk scores, but it can't write
*"start by isolating the audit log because it has no upstream callers
and that lets you safely refactor the payment processor next."*

**Where:**
- Prompt: `PROMPT_MODERNIZATION`
- Client method: `BobClient.recommend_modernization()`
- API: `routes.py` → `post_modernize()`

---

## 4. Hidden business logic recovery

**What:** For a legacy module, Bob reads the source and surfaces the
*implicit business rules* — regulatory branches, magic constants,
edge cases handled because of a past incident, undocumented assumptions
about callers.

**Input to Bob:**
- The full source of the module
- Instruction to be skeptical of code that looks redundant, because in
  legacy systems it usually isn't

**Why Bob:** This is the deepest enterprise value in the brief —
"transforming repositories into organizational memory." It requires
reading code carefully and inferring the *intent* behind defensive
branches, magic constants, and seemingly-redundant code paths. Static
analysis can't do this. A symbol graph can't do this. This is the
purest "Bob reads complete repository context and explains logic with
clarity" use case in the product.

**Demo target:** Point this at `sample-repo/legacy/old_gateway.py` — it's
written specifically to have hidden logic (CHF rounding step, Brexit
GBP-via-COBOL routing, BIN-prefix acquirer routing, etc.). Bob should
identify these.

**Where:**
- Prompt: `PROMPT_HIDDEN_LOGIC`
- Client method: `BobClient.recover_hidden_logic()`
- API: `routes.py` → `get_hidden_logic()`

---

## Configuring Bob

Set these in `.env`:

```ini
BOB_ENDPOINT=http://localhost:7070    # or wherever your Bob exposes its API
BOB_API_KEY=...                       # if your install requires one
BOB_MODEL=bob-default
```

Or for CLI mode:

```ini
BOB_CLI_PATH=/path/to/bob
```

**Adapt the transport.** The default REST shape in `_call_bob_rest()` is
OpenAI-compatible (`{"messages": [...]}` request, `choices[0].message.content`
response). If your Bob install uses a different shape, adjust that one
function — everything else is shape-agnostic. There's a clear `TODO` comment
where the adaptation goes.

## Fallback behavior

If Bob is unreachable, every endpoint still returns a useful deterministic
explanation built from the structured analysis. This means:

- The demo never goes blank
- We have a baseline to compare Bob's quality against
- Reviewers can run the project without a Bob instance

The fallbacks live in `backend/bob/client.py` in the `_fallback_*` helpers
and are intentionally not pretending to be AI — they just state the facts
the graph already knows.

## What we are *not* doing with Bob

To be honest with judges:

- **No fake autocompleted code** to pad the demo
- **No "Bob built our app"** narrative — we built the platform, Bob explains code
- **No prompt-injection theater** — every prompt is small, focused, and
  derived from structured deterministic context
- **No Bob calls in tight loops** — Bob is on the slow path; we cache
  results in component state on the frontend
