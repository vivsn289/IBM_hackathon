"""
Execution flow tracer.

Given a natural-language query like "how does authentication work?", we:
  1. Keyword-match against module names, function names, and source content
  2. Pick the top-K seeds
  3. Walk the dependency graph from each seed (both directions, bounded)
  4. Return an ordered chain of modules that participate in the flow

This is deliberately a *hybrid*: deterministic retrieval gives Bob a small,
high-signal subgraph to reason about. Bob then narrates the flow. We never
ask Bob to "guess which modules are involved" — that's what the graph is for.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

import networkx as nx

from .ast_parser import Module


# Common synonyms — keeps the retrieval step robust to varied phrasing
SYNONYMS = {
    "auth": ["auth", "authentication", "login", "session", "credential", "user", "password"],
    "payment": ["payment", "pay", "transaction", "charge", "processor", "gateway"],
    "billing": ["billing", "invoice", "bill", "charge", "subscription"],
    "tax": ["tax", "vat", "gst", "duty"],
    "report": ["report", "reporting", "analytics", "audit"],
    "fraud": ["fraud", "risk", "screen", "deny"],
    "legacy": ["legacy", "old", "deprecated", "cobol", "mainframe"],
}


def _expand_query(q: str) -> List[str]:
    """Lowercased query tokens, expanded with synonyms."""
    tokens = re.findall(r"[a-zA-Z_]+", q.lower())
    expanded = set(tokens)
    for tok in tokens:
        for _key, syns in SYNONYMS.items():
            if tok in syns:
                expanded.update(syns)
    return list(expanded)


def _score_module(mod: Module, terms: List[str]) -> float:
    """Score a single module's relevance to the query terms."""
    score = 0.0
    name_lower = mod.name.lower()
    for t in terms:
        if t in name_lower:
            score += 5.0  # name match is strong signal
    src_lower = mod.source.lower()
    for t in terms:
        # cap source matches so a giant file doesn't dominate
        count = min(src_lower.count(t), 10)
        score += count * 0.5
    for fn in mod.functions:
        if any(t in fn.lower() for t in terms):
            score += 2.0
    return score


def trace_flow(
    query: str,
    modules: Dict[str, Module],
    g: nx.DiGraph,
    max_seeds: int = 3,
    max_hops: int = 2,
) -> dict:
    """Find seed modules and a bounded subgraph that likely implements the flow."""
    terms = _expand_query(query)
    if not terms:
        return {"query": query, "seeds": [], "modules": [], "edges": []}

    scored: List[Tuple[str, float]] = []
    for name, mod in modules.items():
        s = _score_module(mod, terms)
        if s > 0:
            scored.append((name, s))
    scored.sort(key=lambda kv: kv[1], reverse=True)
    seeds = [name for name, _ in scored[:max_seeds]]

    # BFS bounded by max_hops, both directions
    visited = set(seeds)
    frontier = set(seeds)
    for _ in range(max_hops):
        next_frontier = set()
        for n in frontier:
            if n not in g:
                continue
            next_frontier.update(g.successors(n))
            next_frontier.update(g.predecessors(n))
        frontier = next_frontier - visited
        visited |= frontier

    sub = g.subgraph(visited).copy()

    return {
        "query": query,
        "matched_terms": terms,
        "seeds": seeds,
        "modules": sorted(visited),
        "edges": [{"from": u, "to": v} for u, v in sub.edges()],
        "module_scores": {name: round(s, 2) for name, s in scored[:max_seeds]},
    }
