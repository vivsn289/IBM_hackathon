# Project Brief — Software MRI / RepoLens AI

## The challenge we're answering

IBM Bob Hackathon, *"Turn idea into impact faster."* Bob is positioned as
your AI-powered development partner — it reads complete repository context,
explains logic with clarity, and automates complex transformations.

The fastest way for Bob to create "impact" is on the work that takes engineers
the longest: **understanding code they didn't write.**

## The fundamental problem

Large enterprises run software that is:

- decades old
- mission-critical
- undocumented
- accumulated with technical debt
- impossible to fully replace

Examples: banking, insurance, hospitals, airlines, government, manufacturing
ERP — built on AS/400, z/OS, COBOL, legacy Java monoliths, ancient middleware.

**These systems are not broken.** They process billions of dollars reliably.
The problem is: *nobody fully understands them anymore.*

## Why modernization takes 2–10 years

The bottleneck isn't writing new code. The bottleneck is preserving behavior
without losing institutional knowledge. Five constraints make this hard:

1. **Hidden business logic** — implicit legal rules, compliance branches,
   undocumented edge cases. The codebase *is* the organization's memory.
2. **Feature retention** — clients want the same behavior on better infra.
   Modernization is fundamentally about preserving behavior while evolving
   infrastructure.
3. **Legal & compliance risk** — banking, healthcare, insurance, government:
   tiny behavioral deviations create legal exposure.
4. **Institutional knowledge loss** — engineers leave, docs go stale, the
   org becomes dependent on tribal knowledge.
5. **Extreme coupling** — small changes ripple through billing, auth, audit,
   transactions. Modernization triggers catastrophic regressions.

## Why existing tools fall short

Current tools provide code search, static diagrams, isolated dependency views.
They do **not** provide:

- operational behavior understanding
- blast-radius estimation
- modernization intelligence
- execution-flow cognition
- architecture observability

There is no strong **system intelligence layer** for software architecture.

## Our thesis

> Software systems have become cognitively unmanageable. The solution is to
> transform them into observable operational structures.

Software MRI is **an MRI scan for software systems.** Hidden structures
become visible. Fragile regions become identifiable. Execution flows become
understandable. Modernization risks become observable.

## What Bob is uniquely good for here

Bob is positioned as an AI that reads complete repository context, explains
logic with clarity, automates complex transformations, and streamlines
multi-step work. That maps almost exactly onto what modernization needs:

| Modernization need | What Bob does |
|--------------------|---------------|
| Recover undocumented business logic | Reads source, explains hidden rules |
| Narrate execution flows | Walks a graph and tells the story |
| Plan safe migration order | Multi-step reasoning over dependencies |
| Onboard a new engineer | Plain-English module summaries |

This is genuine, non-cosmetic use of Bob. It's not Bob writing autocompleted
boilerplate — it's Bob doing the hard cognitive work that has no off-the-shelf
deterministic answer.

## Design philosophy

**Deterministic analysis first. AI explanation second.**

```
Repository
  → static analysis (scanner + AST)
  → dependency extraction
  → graph generation (NetworkX)
  → flow reconstruction (subgraph by query)
  → risk analysis (blast radius, cycles, debt scoring)
  → Bob narrates                              ← AI enters here
  → visualization
```

We never ask Bob to *find* structure that the AST already provides. We give
Bob a small, high-signal subgraph and a focused prompt. This makes the system:

- faster (Bob is the slowest hop)
- cheaper (smaller prompts)
- more reliable (no AI hallucination about which file calls which)
- more demoable (deterministic steps always produce something to show)

## Strategic positioning

Software MRI is fundamentally **a cognition layer for software systems**, not
a coding assistant. The future value of AI in enterprise software may not
primarily be generating code — it may be **recovering understanding.**
