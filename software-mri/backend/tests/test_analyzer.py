"""
Smoke tests for the analyzer pipeline.

Run with: `pytest backend/tests/`
These run against the bundled sample-repo so they're self-contained.
"""

from __future__ import annotations

from pathlib import Path

from analyzer.scanner import scan_repository
from analyzer.ast_parser import parse_repository
from analyzer.graph_builder import build_dependency_graph, find_cycles
from analyzer.blast_radius import compute_blast_radius
from analyzer.tech_debt import compute_tech_debt
from analyzer.flow_tracer import trace_flow


SAMPLE_REPO = str(Path(__file__).resolve().parents[2] / "sample-repo")


def test_scanner_finds_files():
    files = scan_repository(SAMPLE_REPO)
    assert len(files) > 5, f"expected several .py files, got {len(files)}"
    assert all(f.endswith(".py") for f in files)


def test_parser_extracts_imports():
    files = scan_repository(SAMPLE_REPO)
    modules = parse_repository(SAMPLE_REPO, files)
    assert modules, "no modules parsed"
    # Pick any module with imports and confirm structure
    with_imports = [m for m in modules.values() if m.imports]
    assert with_imports, "expected at least one module with imports"


def test_graph_has_edges_and_cycles():
    files = scan_repository(SAMPLE_REPO)
    modules = parse_repository(SAMPLE_REPO, files)
    g = build_dependency_graph(modules)
    assert g.number_of_nodes() > 0
    assert g.number_of_edges() > 0
    # sample-repo is deliberately built to contain at least one cycle
    cycles = find_cycles(g)
    assert cycles, "sample-repo should contain at least one dependency cycle"


def test_blast_radius():
    files = scan_repository(SAMPLE_REPO)
    modules = parse_repository(SAMPLE_REPO, files)
    g = build_dependency_graph(modules)
    # Pick the most-depended-on module
    target = max(g.nodes(), key=lambda n: g.in_degree(n))
    result = compute_blast_radius(g, target)
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 100


def test_tech_debt_scoring():
    files = scan_repository(SAMPLE_REPO)
    modules = parse_repository(SAMPLE_REPO, files)
    g = build_dependency_graph(modules)
    debt = compute_tech_debt(modules, g)
    assert "summary" in debt
    assert "hotspots" in debt["summary"]
    assert len(debt["summary"]["hotspots"]) > 0


def test_flow_tracer_finds_payments():
    files = scan_repository(SAMPLE_REPO)
    modules = parse_repository(SAMPLE_REPO, files)
    g = build_dependency_graph(modules)
    flow = trace_flow("how does payment processing work?", modules, g)
    assert flow["seeds"], "expected at least one seed"
    assert any("payment" in s.lower() for s in flow["seeds"]), \
        f"expected a payment-related seed, got {flow['seeds']}"
