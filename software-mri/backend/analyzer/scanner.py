"""
Repository scanner.

Walks a directory and returns every Python source file, ignoring the usual
noise (venvs, caches, build artifacts). Honors MAX_FILES so a giant enterprise
repo can't accidentally OOM the demo box.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".pytest_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".mypy_cache",
}

DEFAULT_MAX_FILES = int(os.getenv("MAX_FILES", "2000"))


def scan_repository(root: str, max_files: int = DEFAULT_MAX_FILES) -> List[str]:
    """Return absolute paths to every .py file under `root`.

    Args:
        root: directory to walk
        max_files: hard cap, returns early past this many files

    Returns:
        Sorted list of absolute paths.
    """
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise FileNotFoundError(f"Not a directory: {root}")

    found: List[str] = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        # mutate dirnames in-place to prune the walk
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fname in filenames:
            if fname.endswith(".py"):
                found.append(os.path.join(dirpath, fname))
                if len(found) >= max_files:
                    return sorted(found)

    return sorted(found)
