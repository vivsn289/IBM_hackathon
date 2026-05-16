"""
Technical debt scoring.

Technical debt = accumulated architectural complexity. We score each module on
several explainable axes and combine them. Every score has a `factors` list so
Bob can narrate *why* a module is debt-heavy rather than emitting a magic number.

Axes:
  - size:         LOC normalized
  - complexity:   branch-node count normalized
  - coupling:     in_degree + out_degree (centrality)
  - cycle:        membership in a strongly-connected component
  - legacy_flag:  modules in a `legacy/` or `old_` path
"""

from __future__ import annotations

from typing import Dict

import networkx as nx

from .ast_parser import Module
from .graph_builder import find_cycles


def compute_tech_debt(modules: Dict[str, Module], g: nx.DiGraph) -> dict:
    """Return per-module debt scores + a summary."""
    if not modules:
        return {"modules": {}, "summary": {}}

    # Normalization references
    max_loc = max((m.loc for m in modules.values()), default=1) or 1
    max_complexity = max((m.complexity for m in modules.values()), default=1) or 1

    cycle_members = set()
    for cycle in find_cycles(g):
        cycle_members.update(cycle)

    per_module = {}
    for name, mod in modules.items():
        factors = []
        score = 0.0

        # Size: up to 20 points
        size_pts = min(20.0, (mod.loc / max_loc) * 20.0)
        if mod.loc > 0.6 * max_loc:
            factors.append(f"oversized module ({mod.loc} LOC)")
        score += size_pts

        # Complexity: up to 25 points
        cplx_pts = min(25.0, (mod.complexity / max_complexity) * 25.0)
        if mod.complexity > 0.6 * max_complexity:
            factors.append(f"high branch complexity ({mod.complexity} branches)")
        score += cplx_pts

        # Coupling: up to 25 points
        deg = g.in_degree(name) + g.out_degree(name)
        coupling_pts = min(25.0, deg * 2.5)
        if deg >= 6:
            factors.append(f"tightly coupled ({deg} connections)")
        score += coupling_pts

        # Cycle membership: flat 20 points
        if name in cycle_members:
            score += 20.0
            factors.append("participates in a dependency cycle")

        # Legacy path: flat 10 points
        if "legacy" in name.lower() or "old_" in name.lower() or "deprecated" in name.lower():
            score += 10.0
            factors.append("located in a legacy path")

        score = min(100.0, score)

        per_module[name] = {
            "score": round(score, 1),
            "factors": factors,
            "metrics": {
                "loc": mod.loc,
                "complexity": mod.complexity,
                "in_degree": g.in_degree(name),
                "out_degree": g.out_degree(name),
                "in_cycle": name in cycle_members,
            },
        }

    ranked = sorted(per_module.items(), key=lambda kv: kv[1]["score"], reverse=True)
    hotspots = [{"module": k, **v} for k, v in ranked[:10]]

    avg = sum(v["score"] for v in per_module.values()) / len(per_module)
    return {
        "modules": per_module,
        "summary": {
            "average_score": round(avg, 1),
            "hotspots": hotspots,
            "cycle_count": len(find_cycles(g)),
            "modules_in_cycles": len(cycle_members),
        },
    }
