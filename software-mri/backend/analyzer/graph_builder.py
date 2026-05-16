"""
Dependency graph builder.

Takes the parsed modules and produces a NetworkX DiGraph where:
  - nodes are dotted module names with metadata (domain, loc, complexity)
  - edges are import relationships

Only intra-repo edges are kept. Imports of stdlib / 3rd-party libs are dropped
from the graph but preserved on the node metadata (useful for Bob later).
"""

from __future__ import annotations

from typing import Dict, List

import networkx as nx

from .ast_parser import Module


def build_dependency_graph(modules: Dict[str, Module]) -> nx.DiGraph:
    """Build a directed graph of intra-repo dependencies.

    An edge A -> B means "module A imports module B" (A depends on B).
    """
    g = nx.DiGraph()
    module_names = set(modules.keys())

    # First pass: add all nodes with metadata
    for name, mod in modules.items():
        g.add_node(
            name,
            domain=mod.domain,
            loc=mod.loc,
            complexity=mod.complexity,
            functions=len(mod.functions),
            classes=len(mod.classes),
            path=mod.path,
        )

    # Second pass: edges. An import counts as intra-repo if its dotted prefix
    # matches a known module exactly OR if it matches a parent of one.
    for name, mod in modules.items():
        for imp in mod.imports:
            target = _resolve_import_to_module(imp, module_names)
            if target and target != name:
                g.add_edge(name, target)

    return g


def _resolve_import_to_module(imp: str, known: set) -> str | None:
    """Map an import string to a module in `known`, or None if external.

    `from billing.invoices import generate` → import string is "billing.invoices".
    `import billing` → could refer to billing/__init__.py which is just "billing".
    """
    if imp in known:
        return imp
    # walk up parents
    parts = imp.split(".")
    while len(parts) > 1:
        parts.pop()
        candidate = ".".join(parts)
        if candidate in known:
            return candidate
    return None


def find_cycles(g: nx.DiGraph) -> List[List[str]]:
    """Return strongly-connected components of size > 1 — the dependency cycles."""
    return [list(c) for c in nx.strongly_connected_components(g) if len(c) > 1]


def graph_to_dict(g: nx.DiGraph, debt: dict | None = None) -> dict:
    """Serialize the graph for the frontend (vis-network-friendly shape)."""
    debt = debt or {}
    nodes = []
    for n, data in g.nodes(data=True):
        score = debt.get(n, {}).get("score", 0.0)
        nodes.append({
            "id": n,
            "label": n.split(".")[-1],
            "domain": data.get("domain", "unknown"),
            "loc": data.get("loc", 0),
            "complexity": data.get("complexity", 0),
            "in_degree": g.in_degree(n),
            "out_degree": g.out_degree(n),
            "debt_score": score,
        })
    edges = [{"from": u, "to": v} for u, v in g.edges()]
    return {
        "nodes": nodes,
        "edges": edges,
        "cycles": find_cycles(g),
        "stats": {
            "modules": g.number_of_nodes(),
            "dependencies": g.number_of_edges(),
            "cycles_detected": len(find_cycles(g)),
        },
    }
