"""
Software MRI — FastAPI entrypoint.

Wires together:
  - the deterministic analyzer (analyzer/)
  - the IBM Bob client (bob/)
  - the REST API (api/)

Run with:
    uvicorn main:app --reload --host 127.0.0.1 --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from analyzer.scanner import scan_repository
from analyzer.ast_parser import parse_repository
from analyzer.graph_builder import build_dependency_graph
from analyzer.tech_debt import compute_tech_debt
from api.routes import router as api_router
from bob.client import BobClient

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO = os.getenv("DEFAULT_REPO_PATH", str(PROJECT_ROOT / "sample-repo"))


class AppState:
    """Process-wide singleton holding the current analysis result + Bob client."""

    repo_path: str = ""
    files: list = []
    modules: dict = {}
    graph = None  # networkx.DiGraph
    debt: dict = {}
    bob: BobClient | None = None


state = AppState()


def analyze_repo(path: str) -> None:
    """Run the full deterministic analysis pipeline against `path`.

    Deterministic-first is intentional. We never ask Bob to *find* structure
    that the AST already gives us. Bob is reserved for explanation, narration,
    and modernization advice — the things only an AI partner can do well.
    """
    abs_path = str(Path(path).resolve())
    files = scan_repository(abs_path)
    modules = parse_repository(abs_path, files)
    graph = build_dependency_graph(modules)
    debt = compute_tech_debt(modules, graph)

    state.repo_path = abs_path
    state.files = files
    state.modules = modules
    state.graph = graph
    state.debt = debt


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """On startup: analyze the default repo and instantiate Bob."""
    print(f"[software-mri] analyzing {DEFAULT_REPO} ...")
    analyze_repo(DEFAULT_REPO)
    print(
        f"[software-mri] {len(state.modules)} modules, "
        f"{state.graph.number_of_edges()} edges"
    )
    state.bob = BobClient()
    await state.bob.warmup()
    yield
    # nothing to clean up


app = FastAPI(
    title="Software MRI",
    description="Architectural observability for software systems. Powered by IBM Bob.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: dev-time only. Tighten for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "Software MRI",
        "tagline": "Architectural observability for software systems.",
        "powered_by": "IBM Bob",
        "loaded_repo": state.repo_path,
        "modules": len(state.modules),
    }
