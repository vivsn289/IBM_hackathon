# Demo Script — Software MRI (target: 2 minutes)

> Print this. Rehearse it. The demo is what wins.

---

## Setup (before judges arrive)

1. `bash scripts/run-backend.sh` in one terminal
2. `bash scripts/run-frontend.sh` in another
3. Open `http://localhost:5173` in a clean Chrome window, fullscreen
4. Make sure Bob is reachable. Run `curl $BOB_ENDPOINT/health` first.
5. **Pre-warm the four canned queries below** by clicking them once.
   Bob's first call is the slow one — cached responses make the demo snap.

---

## Opening (15 seconds)

> *"Most enterprise modernization projects take 2 to 10 years. The bottleneck
> isn't writing new code — it's understanding what the old code already does.*
>
> *This is a banking system. 17 years of accumulated logic. Nobody on the
> team has read all of it. Watch this."*

**Action:** Have the architecture graph already loaded on screen. The dense
graph of the sample banking repo is on display, with `legacy/` glowing red.

---

## Section 1 — Architecture observability (20 seconds)

> *"In about a second, Software MRI parsed the entire repo, extracted every
> import, and built a dependency graph. Each color is a business domain.
> Each node sized by lines of code. The header tells us there's one
> dependency cycle — billing and payments calling each other."*

**Action:** Click the `Tech Debt` tab. Heatmap renders. `legacy.old_gateway`
and `payments.processor` glow red.

> *"And here's the technical debt heatmap. The reddest cells are the
> modernization risk hotspots."*

**Action:** Hover over `payments.processor`. Tooltip shows the factors.

> *"Notice — this isn't a magic AI score. It's an explainable composite:
> oversized, high branch complexity, tightly coupled to seven other modules.
> Every factor is named."*

---

## Section 2 — Blast radius (25 seconds)

**Action:** Back to Architecture. Click `payments.processor`. Side panel
populates.

> *"Now the operational question every enterprise team is afraid to ask.
> What breaks if we touch this? Software MRI computes the blast radius —
> direct dependents, transitive reach, and the business domains it spreads
> across. This module is rated MEDIUM risk. We can see exactly which other
> modules will be affected, and we can click any of them to navigate the
> graph."*

---

## Section 3 — Bob narrates modernization (40 seconds)

**Action:** Click `Plan modernization with Bob`. Wait for response.

> *"Now this is where Bob earns its place. The risk score is graph theory.
> But knowing what to do *next* — that requires reading the code, reasoning
> about coupling, and writing a coherent plan. That's Bob's specialty.*
>
> *Bob has read the blast-radius result and the debt summary. It's writing
> an ordered extraction plan with tradeoffs."*

**Action:** Read 2 highlights from Bob's response aloud. Don't read the whole
thing — let it speak for itself on screen.

---

## Section 4 — Hidden logic recovery (30 seconds — the killer feature)

**Action:** Navigate to `legacy.old_gateway`. Click `Recover hidden business
logic`.

> *"This is the feature I'm most proud of. This module is 17 years of
> accumulated currency rules — Swiss 5-cent rounding, post-Brexit routing,
> a 1996 COBOL bridge. Most of the team has never read it. The few who did
> are gone."*

**Action:** Bob's response appears. It calls out the CHF step rule, the
Brexit GBP path, the BIN prefix routing, etc.

> *"Bob has surfaced the implicit business rules buried in this file. The
> stuff that, if a junior dev cleaned it up, would silently break production.
> This is institutional knowledge recovery. This is what enterprises pay
> consultants millions for."*

---

## Closing (10 seconds)

> *"Software MRI uses Bob to do what only Bob can — read complete repository
> context and explain it clearly. The deterministic layer finds the structure.
> Bob recovers the understanding.*
>
> ***Modernization should not require losing institutional memory.****"*

Stop. Smile. Take questions.

---

## Q&A prep

**"How is this different from existing static analyzers?"**
> They produce graphs. We produce understanding. Sourcegraph, GitHub code
> search, language servers — they all answer "where does this function get
> called." We answer "what would break if we modernize this, why, in what
> order, and what hidden business logic does that code encode."

**"Does this scale to a real enterprise repo?"**
> The AST + graph pipeline scales linearly with LOC and is fast — millions
> of lines in minutes. The Bob calls are per-module and per-query, so they
> scale with user interaction, not repo size. The graph layout is the
> bottleneck past ~5,000 modules; we'd switch to a domain-grouped view.

**"What about non-Python codebases?"**
> The analyzer pattern works for any language with importable modules.
> Java, TypeScript, Go would be the next adapters. COBOL and AS/400 are
> the genuinely hard ones — that's where Bob's reading-comprehension
> would matter most.

**"Why deterministic-first?"**
> Three reasons: speed, cost, and reliability. We never have Bob hallucinate
> file names or fabricate imports. The graph is ground truth. Bob narrates
> ground truth.

**"What if Bob isn't available?"**
> Every Bob-backed endpoint has a deterministic fallback. The demo never
> goes blank. (Show them by killing the Bob endpoint and clicking explain.)
