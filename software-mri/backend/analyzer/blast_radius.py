"""
Blast radius analysis.

"What breaks if we modernize the payment engine?"

For a given target module M, compute:
  - direct_dependents: modules that import M (1-hop reverse)
  - transitive_dependents: full upstream reach
  - affected_domains: which business domains light up
  - risk_score: a 0-100 heuristic combining reach + coupling + criticality

The risk score is intentionally explainable — we expose the contributing factors
so Bob can narrate *why* the score is what it is.
"""

from __future__ import annotations

from typing import Dict, List

import networkx as nx


def compute_blast_radius(g: nx.DiGraph, target: str) -> dict:
    """Return blast radius for a single target module."""
    if target not in g:
        return {"error": f"module not found: {target}"}

    direct = list(g.predecessors(target))
    # Transitive reverse: everything that can reach target via imports
    reverse_g = g.reverse(copy=False)
    transitive = set()
    if target in reverse_g:
        transitive = set(nx.descendants(reverse_g, target))

    domains = {g.nodes[m].get("domain", "unknown") for m in transitive}
    domains.discard(g.nodes[target].get("domain"))  # the target's own domain doesn't count as "spread"

    coupling = g.in_degree(target)  # how many things depend on it directly
    reach = len(transitive)
    cross_domain = len(domains)

    # Heuristic risk score 0-100
    # weights: reach is the biggest factor; cross-domain spread amplifies it
    raw = (reach * 2) + (coupling * 3) + (cross_domain * 8)
    risk_score = min(100, raw)

    risk_band = "low"
    if risk_score >= 60:
        risk_band = "critical"
    elif risk_score >= 35:
        risk_band = "high"
    elif risk_score >= 15:
        risk_band = "medium"

    return {
        "target": target,
        "direct_dependents": sorted(direct),
        "transitive_dependents": sorted(transitive),
        "affected_domains": sorted(domains),
        "metrics": {
            "direct_count": len(direct),
            "transitive_count": reach,
            "cross_domain_count": cross_domain,
        },
        "risk_score": risk_score,
        "risk_band": risk_band,
        "explanation_factors": [
            f"{len(direct)} module(s) import this directly",
            f"{reach} module(s) reach it transitively",
            f"impact spreads across {cross_domain} other business domain(s)",
        ],
    }


def rank_by_blast_radius(g: nx.DiGraph, limit: int = 10) -> List[dict]:
    """Return the top-N most dangerous modules to modify, ranked by reach."""
    scored = []
    for n in g.nodes():
        result = compute_blast_radius(g, n)
        scored.append(result)
    scored.sort(key=lambda r: r["risk_score"], reverse=True)
    return scored[:limit]
