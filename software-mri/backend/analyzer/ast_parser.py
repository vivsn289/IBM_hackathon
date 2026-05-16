"""
AST parser.

For each Python file we extract a `Module` record containing:
  - module path (dotted)
  - imports (resolved to dotted module paths where possible)
  - top-level functions and classes
  - a rough complexity signal (count of branch nodes)
  - LOC (non-blank)
  - raw source (cached for Bob)

We deliberately keep this lightweight — no symbol table, no type inference.
The point isn't to rebuild pyright; the point is enough structure to draw a
graph and let Bob explain the rest.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class Module:
    name: str                       # dotted, e.g. "billing.invoices"
    path: str                       # absolute file path
    domain: str                     # top-level package, e.g. "billing"
    imports: Set[str] = field(default_factory=set)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    calls: List[str] = field(default_factory=list)   # function names called anywhere
    loc: int = 0
    complexity: int = 0             # rough cyclomatic complexity
    source: str = ""                # cached; Bob reads this

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": self.path,
            "domain": self.domain,
            "imports": sorted(self.imports),
            "functions": self.functions,
            "classes": self.classes,
            "loc": self.loc,
            "complexity": self.complexity,
        }


# AST node types that count toward cyclomatic complexity
_BRANCH_NODES = (
    ast.If, ast.For, ast.While, ast.Try,
    ast.ExceptHandler, ast.With, ast.BoolOp, ast.IfExp,
)


def _module_name_from_path(repo_root: Path, file_path: Path) -> str:
    """Convert /abs/path/to/repo/billing/invoices.py -> 'billing.invoices'."""
    rel = file_path.relative_to(repo_root).with_suffix("")
    parts = list(rel.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts else file_path.stem


def _resolve_relative_import(current: str, level: int, target: Optional[str]) -> str:
    """Resolve `from ..foo.bar import x` relative to the current module."""
    parts = current.split(".")
    if level > len(parts):
        # over-relative; just return target as-is, we'll likely drop it
        return target or ""
    base = parts[: len(parts) - level]
    if target:
        return ".".join(base + target.split("."))
    return ".".join(base)


def parse_file(repo_root: Path, file_path: Path) -> Module:
    """Parse a single Python file into a Module record."""
    source = file_path.read_text(encoding="utf-8", errors="replace")
    module_name = _module_name_from_path(repo_root, file_path)
    domain = module_name.split(".", 1)[0] if "." in module_name else module_name

    mod = Module(name=module_name, path=str(file_path), domain=domain, source=source)
    mod.loc = sum(1 for line in source.splitlines() if line.strip() and not line.strip().startswith("#"))

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        # Real legacy code has files that don't parse. Don't crash — degrade.
        return mod

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod.imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            target = node.module or ""
            if node.level and node.level > 0:
                resolved = _resolve_relative_import(module_name, node.level, target)
                if resolved:
                    mod.imports.add(resolved)
            else:
                if target:
                    mod.imports.add(target)
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            # only record top-level functions (parent is module)
            mod.functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            mod.classes.append(node.name)
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                mod.calls.append(fn.id)
            elif isinstance(fn, ast.Attribute):
                mod.calls.append(fn.attr)
        if isinstance(node, _BRANCH_NODES):
            mod.complexity += 1

    # Top-level functions only: walk tree.body, not the whole tree
    mod.functions = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    mod.classes = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]

    return mod


def parse_repository(repo_root: str, file_paths: List[str]) -> Dict[str, Module]:
    """Parse every file. Returns dict keyed by dotted module name."""
    root = Path(repo_root).resolve()
    modules: Dict[str, Module] = {}
    for fp in file_paths:
        mod = parse_file(root, Path(fp))
        modules[mod.name] = mod
    return modules
