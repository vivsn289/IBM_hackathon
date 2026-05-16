# Hackathon Notes

## Submission checklist

- [ ] Code runs end-to-end on a fresh laptop (run `bash scripts/setup.sh`)
- [ ] `.env` is configured with the real Bob endpoint and tested
- [ ] All four Bob endpoints respond in under 10s on the sample repo
- [ ] Pre-warmed the four canned demo queries so live demo is snappy
- [ ] `README.md` clearly states Bob's role in 30 seconds of reading
- [ ] `docs/BOB_INTEGRATION.md` exists (judges may go straight here)
- [ ] Demo script rehearsed at least 3 times, hitting the 2-minute mark
- [ ] Backup: screen recording of the demo in case of network failure
- [ ] Tested with Bob deliberately killed → fallbacks still produce sensible
      output, demo doesn't crash

## What is real vs faked

| Feature | Real? | Notes |
|--------|-------|-------|
| Repository scanning | ✅ Real | `os.walk` with sensible skips |
| Python AST parsing | ✅ Real | `ast` module, robust to syntax errors |
| Dependency graph | ✅ Real | NetworkX, resolves relative imports |
| Cycle detection | ✅ Real | Tarjan SCC algorithm |
| Blast radius | ✅ Real | Reverse transitive closure |
| Debt scoring | ✅ Real | Explainable composite, factors exposed |
| Flow tracing | ✅ Real | Keyword + synonym retrieval → bounded BFS |
| Bob integration | ✅ Real | But pluggable — adapt to actual Bob API |
| Sample legacy repo | ✅ Real Python | Stubs database calls, but the *structure* is real |
| COBOL/mainframe link | ⚠️ Mocked | `legacy/cobol_bridge.py` is symbolic |
| Multi-language support | ❌ Out of scope | Python only |

## Scope reality

This is a **hackathon prototype.** The point is to convincingly demonstrate
the architectural intelligence vision, not to ship a complete platform.

What's missing for a real product:
- Multi-language (Java/TypeScript/COBOL adapters)
- IDE plugin
- Auth & multi-tenant
- Persistence (graph cache, Bob response cache)
- Streaming Bob responses (currently blocking)
- Background re-analysis on git push
- Better graph layout for >5,000 modules
- Tests beyond smoke
- Observability for the platform itself (meta!)

We are not pretending otherwise. The brief in `PROJECT_BRIEF.md` says it
plainly: *"It only needs to convincingly demonstrate architectural
intelligence."* That's what we did.

## What to talk about if asked "what's next"

Three honest, ordered next steps:

1. **Bob streaming.** Right now Bob responses block. Streaming them token
   by token into the UI would make the demo feel substantially more alive.

2. **Java adapter.** The analyzer is structured so a new language is one
   module (`analyzer/java_parser.py`) that produces `Module` records. The
   graph builder, blast radius, and debt code are language-agnostic.

3. **Persisted graph cache.** Re-analyzing on every restart is fine for
   demos and small repos. Real repos need an incremental analysis pipeline
   triggered by git events.

## Things to avoid saying in the demo

- ❌ "Bob built this." — judges will see right through it
- ❌ "We use GPT under the hood." — it's Bob, say Bob
- ❌ "AI does X" — say which specific Bob task; vagueness hurts credibility
- ❌ "It works on any repo." — say "any Python repo; multi-language is
      the next adapter"
- ❌ "Production-ready." — it isn't, and judges know

## Team logistics

- Pre-record a 60-second backup demo video. Network failures at hackathons
  happen.
- If two people present, one drives the screen, one narrates. Practice the
  handoff.
- Have `docs/BOB_INTEGRATION.md` open in a second tab to scroll to if a
  judge asks "show me where Bob is used."
