"""
Prompt templates for Bob.

Each template is for one of the four meaningful Bob integration points in
Software MRI. The templates expect the deterministic analyzer to have already
shortlisted relevant modules — Bob's job is to *explain*, not to *search*.
"""

PROMPT_EXPLAIN_MODULE = """\
You are explaining a code module to a senior engineer who is onboarding to a \
legacy enterprise codebase. They need a clear, technical, plain-English summary.

Module: `{module}`

Source:
```python
{source}
```

Closest in-repo neighbors:
{neighbors}

Write a tight 4–6 sentence summary that answers:
1. What does this module *do* in the business sense (not just the code)?
2. Which other modules does it depend on, and why?
3. Any non-obvious assumptions, edge cases, or hidden business logic?

Do not list every function. Do not restate the source. Be concrete.\
"""


PROMPT_FLOW_QUERY = """\
A developer is trying to understand a legacy codebase. They asked:

> "{query}"

The deterministic flow tracer identified these as the most relevant seed \
modules: {seeds}

And these modules are reachable from the seeds in 2 hops: {modules}

Here are the relevant source snippets:

{snippets}

Narrate the execution flow that answers the developer's question. Walk through \
it module by module in the order things actually execute. Call out:
- entry point(s)
- where validation happens
- where the business decision is made
- where state is mutated or persisted
- any branch that handles regulatory or compliance edge cases

Be specific. Reference function names. 6–10 sentences.\
"""


PROMPT_MODERNIZATION = """\
A team is planning to modernize the module `{target}` in a legacy enterprise \
codebase. The deterministic blast-radius analysis says:

- Risk band: **{risk_band}** (score {risk_score}/100)
- Directly depended on by: {direct}
- Transitively reaches {transitive_count} module(s)
- Spreads across these business domains: {domains}
- Repo-wide technical-debt hotspots: {hotspots}

Recommend a safe, incremental modernization plan. Your output must:
1. State the *order* of extraction (what to isolate first, second, third)
2. For each step, name the tradeoff (what risk is reduced, what new risk is introduced)
3. Identify which steps could be done in parallel
4. Flag the single highest-risk step and what to do before attempting it

Do not suggest a full rewrite. Incremental only. 8–12 sentences.\
"""


PROMPT_HIDDEN_LOGIC = """\
The module below is from a legacy enterprise codebase. Most of the team has \
left. Documentation is outdated. We need to recover the *institutional \
knowledge* embedded in this file.

Module: `{module}`

```python
{source}
```

Surface the implicit business rules this module encodes. Specifically:
- Regulatory or compliance branches (tax, KYC, AML, regional law)
- Magic constants and what they probably represent
- Edge cases handled in a way that suggests a real-world incident shaped them
- Assumptions about upstream/downstream callers
- Anything that, if a junior dev "cleaned it up," would silently break production

Be skeptical of code that looks redundant — in legacy systems it often isn't. \
Use bullet points. Be specific. Reference line numbers or function names.\
"""
