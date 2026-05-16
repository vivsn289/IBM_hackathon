"""
REST API for the frontend.

Endpoints:
  GET    /api/graph                  — current dependency graph
  GET    /api/debt                   — tech-debt scores + hotspots
  GET    /api/blast/{module}         — blast radius for one module
  POST   /api/query                  — natural-language flow query (uses Bob)
  POST   /api/modernize              — modernization plan for a module (uses Bob)
  GET    /api/explain/{module}       — plain-English module summary (uses Bob)
  GET    /api/hidden-logic/{module}  — recover hidden business rules (uses Bob)
  POST   /api/analyze                — re-analyze a different repo path

Bob is reached through the shared BobClient on app state. If Bob is
unavailable, every Bob-backed endpoint still returns a useful deterministic
response — so the demo never goes blank.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from analyzer.blast_radius import compute_blast_radius, rank_by_blast_radius
from analyzer.flow_tracer import trace_flow
from analyzer.graph_builder import graph_to_dict
from api.schemas import (
    AnalyzeRequest,
    BobResponse,
    GraphResponse,
    ModernizeRequest,
    QueryRequest,
)

router = APIRouter()


def _state():
    # Lazy import to avoid a circular dependency with main.py at import time.
    from main import state
    return state


@router.get("/graph", response_model=GraphResponse)
def get_graph():
    s = _state()
    return graph_to_dict(s.graph, s.debt.get("modules", {}))


@router.get("/debt")
def get_debt():
    return _state().debt


@router.get("/blast/{module:path}")
def get_blast(module: str):
    s = _state()
    result = compute_blast_radius(s.graph, module)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/blast")
def get_blast_ranked():
    """Top-10 most dangerous modules to modify, ranked."""
    return {"ranked": rank_by_blast_radius(_state().graph, limit=10)}


@router.post("/query", response_model=BobResponse)
async def post_query(req: QueryRequest):
    s = _state()
    flow = trace_flow(req.query, s.modules, s.graph)

    snippets = {
        name: s.modules[name].source
        for name in flow["modules"][:6]
        if name in s.modules
    }
    answer = await s.bob.answer_flow_query(req.query, flow, snippets)
    return BobResponse(answer=answer, structured=flow)


@router.post("/modernize", response_model=BobResponse)
async def post_modernize(req: ModernizeRequest):
    s = _state()
    blast = compute_blast_radius(s.graph, req.target)
    if "error" in blast:
        raise HTTPException(status_code=404, detail=blast["error"])
    debt_summary = s.debt.get("summary", {})
    answer = await s.bob.recommend_modernization(req.target, blast, debt_summary)
    return BobResponse(answer=answer, structured={"blast": blast})


@router.get("/explain/{module:path}", response_model=BobResponse)
async def get_explain(module: str):
    s = _state()
    if module not in s.modules:
        raise HTTPException(status_code=404, detail=f"unknown module: {module}")
    mod = s.modules[module]
    neighbors = []
    if module in s.graph:
        for succ in list(s.graph.successors(module))[:6]:
            neighbors.append({"name": succ, "relation": "imports",
                              "summary": _short_summary(s.modules.get(succ))})
        for pred in list(s.graph.predecessors(module))[:6]:
            neighbors.append({"name": pred, "relation": "imported by",
                              "summary": _short_summary(s.modules.get(pred))})
    answer = await s.bob.explain_module(module, mod.source, neighbors)
    return BobResponse(answer=answer, structured={
        "module": mod.to_dict(),
        "neighbors": neighbors,
    })


@router.get("/hidden-logic/{module:path}", response_model=BobResponse)
async def get_hidden_logic(module: str):
    s = _state()
    if module not in s.modules:
        raise HTTPException(status_code=404, detail=f"unknown module: {module}")
    mod = s.modules[module]
    answer = await s.bob.recover_hidden_logic(module, mod.source)
    return BobResponse(answer=answer)


@router.post("/analyze")
def post_analyze(req: AnalyzeRequest):
    """Re-analyze a different repo path. Mutates global state."""
    from main import analyze_repo, state
    try:
        analyze_repo(req.path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "loaded": state.repo_path,
        "modules": len(state.modules),
        "edges": state.graph.number_of_edges(),
    }


def _short_summary(mod) -> str:
    if mod is None:
        return ""
    return f"{len(mod.functions)} fns, {len(mod.classes)} classes, {mod.loc} LOC"
