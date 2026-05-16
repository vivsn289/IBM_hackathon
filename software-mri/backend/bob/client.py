"""
IBM Bob client.

This module is the *single seam* between Software MRI and Bob. Everything else
in the codebase calls `BobClient.complete(prompt)` and doesn't care whether the
real Bob is responding or the fallback heuristics are.

== How Bob is actually used in this product ==

Software MRI uses Bob at four meaningful points:

  1. explain_module()       — turn a module + its neighbors into a plain-English
                              architectural summary. Bob is great at this because
                              it reads complete repository context, which is the
                              hardest part of summarizing real code.

  2. answer_flow_query()    — given a user question and a small subgraph that
                              the deterministic flow tracer pre-selected, Bob
                              narrates how the flow works step by step.

  3. recommend_modernization() — Bob reads the blast-radius result and the debt
                                 hotspots and proposes a safe extraction order
                                 with tradeoffs.

  4. recover_hidden_logic() — Bob reads a legacy module and surfaces the
                              implicit business rules it encodes (edge cases,
                              regulatory branches, undocumented assumptions).

Each of these maps to a prompt template in `prompts.py`.

== Transport ==

We support two integration modes, picked from env:

  - REST: set BOB_ENDPOINT (assumed POST /v1/chat/completions style)
  - CLI:  set BOB_CLI_PATH (subprocess, Bob is invoked locally)

Adapt the request shape in `_call_bob_rest` to match your actual Bob install.
Anywhere we couldn't pin down the exact contract from the docs, there's a
clear TODO so you can wire it up in 5 minutes.

== Fallback ==

If Bob isn't reachable, `complete()` returns a deterministic explanation
built from the structured context. This keeps the demo robust — and honestly
makes for a useful baseline to compare Bob's quality against.
"""

from __future__ import annotations

import os
import subprocess
from typing import Any, Dict, List, Optional

import httpx

from .prompts import (
    PROMPT_EXPLAIN_MODULE,
    PROMPT_FLOW_QUERY,
    PROMPT_MODERNIZATION,
    PROMPT_HIDDEN_LOGIC,
)


class BobClient:
    """Thin client over Bob with a deterministic fallback."""

    def __init__(self) -> None:
        self.endpoint = os.getenv("BOB_ENDPOINT", "").rstrip("/")
        self.api_key = os.getenv("BOB_API_KEY", "")
        self.cli_path = os.getenv("BOB_CLI_PATH", "")
        self.model = os.getenv("BOB_MODEL", "bob-default")
        self._available: Optional[bool] = None

    async def warmup(self) -> None:
        """Probe Bob at startup and remember whether it's available."""
        self._available = await self._probe()
        mode = "REST" if self.endpoint else "CLI" if self.cli_path else "none"
        print(f"[bob] mode={mode} available={self._available}")

    async def _probe(self) -> bool:
        if self.endpoint:
            try:
                async with httpx.AsyncClient(timeout=2.0) as c:
                    r = await c.get(self.endpoint + "/health")
                    return r.status_code < 500
            except Exception:
                return False
        if self.cli_path and os.path.exists(self.cli_path):
            return True
        return False

    # ------------------------------------------------------------------
    # Public, task-oriented methods. These are what the API routes call.
    # ------------------------------------------------------------------

    async def explain_module(self, module_name: str, source: str,
                             neighbors: List[Dict[str, Any]]) -> str:
        prompt = PROMPT_EXPLAIN_MODULE.format(
            module=module_name,
            source=_clip(source, 4000),
            neighbors=_format_neighbors(neighbors),
        )
        return await self.complete(prompt, fallback=_fallback_explain(module_name, source, neighbors))

    async def answer_flow_query(self, query: str, flow_result: Dict[str, Any],
                                module_snippets: Dict[str, str]) -> str:
        prompt = PROMPT_FLOW_QUERY.format(
            query=query,
            modules=", ".join(flow_result.get("modules", [])),
            seeds=", ".join(flow_result.get("seeds", [])),
            snippets=_format_snippets(module_snippets),
        )
        return await self.complete(prompt, fallback=_fallback_flow(query, flow_result))

    async def recommend_modernization(self, target: str, blast: Dict[str, Any],
                                      debt_summary: Dict[str, Any]) -> str:
        prompt = PROMPT_MODERNIZATION.format(
            target=target,
            risk_band=blast.get("risk_band", "unknown"),
            risk_score=blast.get("risk_score", 0),
            direct=", ".join(blast.get("direct_dependents", [])),
            transitive_count=blast.get("metrics", {}).get("transitive_count", 0),
            domains=", ".join(blast.get("affected_domains", [])),
            hotspots=", ".join(h["module"] for h in debt_summary.get("hotspots", [])[:5]),
        )
        return await self.complete(prompt, fallback=_fallback_modernization(target, blast))

    async def recover_hidden_logic(self, module_name: str, source: str) -> str:
        prompt = PROMPT_HIDDEN_LOGIC.format(
            module=module_name,
            source=_clip(source, 6000),
        )
        return await self.complete(prompt, fallback=_fallback_hidden_logic(module_name, source))

    # ------------------------------------------------------------------
    # Transport.
    # ------------------------------------------------------------------

    async def complete(self, prompt: str, fallback: str = "") -> str:
        """Single entrypoint. Picks REST > CLI > fallback."""
        if self.endpoint:
            try:
                return await self._call_bob_rest(prompt)
            except Exception as e:
                print(f"[bob] REST call failed: {e!r}, using fallback")
        elif self.cli_path:
            try:
                return self._call_bob_cli(prompt)
            except Exception as e:
                print(f"[bob] CLI call failed: {e!r}, using fallback")
        return fallback or "[Bob unavailable — no fallback content for this prompt]"

    async def _call_bob_rest(self, prompt: str) -> str:
        # TODO: confirm the exact request/response shape against your Bob install.
        # The OpenAI-compatible shape below is a reasonable default — adjust if
        # your endpoint expects something else (e.g. `{"input": ...}` or
        # `{"messages": [{"role": "user", "content": ...}]}` with a different
        # response field).
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are Bob, IBM's AI development partner. "
                                              "You read complete repository context and "
                                              "explain code with clarity. Be concise and "
                                              "technical."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        url = self.endpoint + "/v1/chat/completions"
        async with httpx.AsyncClient(timeout=60.0) as c:
            r = await c.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        # OpenAI-compatible response. Adjust if Bob returns a different shape.
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            # Try common alternative shapes
            for key in ("output", "response", "text", "completion"):
                if key in data and isinstance(data[key], str):
                    return data[key]
            raise RuntimeError(f"Unexpected Bob response shape: {list(data.keys())}")

    def _call_bob_cli(self, prompt: str) -> str:
        """Run Bob Shell in non-interactive mode (`bob -p`).

        Bob Shell wraps its response between `---output---` markers on stdout.
        We extract just the content between them. Stderr contains deprecation
        warnings and status — ignored.
        """
        # Run from the sample-repo dir so Bob has the right working context.
        from pathlib import Path
        cwd = Path(__file__).resolve().parents[2] / "sample-repo"

        result = subprocess.run(
            [self.cli_path, "-p", prompt],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(cwd),
        )
        if result.returncode != 0:
            raise RuntimeError(f"bob CLI failed: {result.stderr.strip()[:500]}")

        # Extract content between ---output--- markers
        stdout = result.stdout
        marker = "---output---"
        if marker in stdout:
            parts = stdout.split(marker)
            if len(parts) >= 3:
                return parts[1].strip()
        # Fallback: return raw stdout if format is unexpected
        return stdout.strip()


# ----------------------------------------------------------------------
# Helpers and deterministic fallbacks.
# Fallbacks aren't pretend-AI. They state what the structured analysis
# already knows, in clear prose. They're a useful baseline even when Bob
# is available.
# ----------------------------------------------------------------------


def _clip(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [{len(text) - max_chars} chars truncated]"


def _format_neighbors(neighbors: List[Dict[str, Any]]) -> str:
    if not neighbors:
        return "(no intra-repo neighbors)"
    return "\n".join(
        f"- {n['name']} ({n.get('relation', 'related')}): {n.get('summary', '')}"
        for n in neighbors
    )


def _format_snippets(snippets: Dict[str, str]) -> str:
    parts = []
    for name, src in snippets.items():
        parts.append(f"### {name}\n```python\n{_clip(src, 1200)}\n```")
    return "\n\n".join(parts)


def _fallback_explain(module: str, source: str, neighbors: List[Dict[str, Any]]) -> str:
    loc = source.count("\n")
    fns = source.count("def ")
    classes = source.count("class ")
    rels = ", ".join(n["name"] for n in neighbors[:5]) or "none"
    return (
        f"**{module}**\n\n"
        f"This module has approximately {loc} lines, {fns} functions, and {classes} classes. "
        f"Its closest in-repo relationships are with: {rels}. "
        f"A full natural-language explanation requires Bob — configure BOB_ENDPOINT and try again."
    )


def _fallback_flow(query: str, flow: Dict[str, Any]) -> str:
    seeds = ", ".join(flow.get("seeds", [])) or "no strong matches"
    mods = ", ".join(flow.get("modules", [])[:8])
    return (
        f"Query: *{query}*\n\n"
        f"The deterministic flow tracer identified **{seeds}** as the most relevant seed module(s). "
        f"Reachable in 2 hops: {mods}. "
        f"For a step-by-step narrative explanation of the flow, enable Bob in `.env`."
    )


def _fallback_modernization(target: str, blast: Dict[str, Any]) -> str:
    return (
        f"Modernizing **{target}** is rated **{blast.get('risk_band', '?')}** risk "
        f"(score {blast.get('risk_score', '?')}/100).\n\n"
        f"Factors:\n- " + "\n- ".join(blast.get("explanation_factors", []))
        + "\n\nEnable Bob to get an ordered extraction plan with tradeoffs."
    )


def _fallback_hidden_logic(module: str, source: str) -> str:
    # Surface heuristically interesting bits: conditionals on magic constants,
    # comments mentioning regulations, etc.
    interesting = []
    for line in source.splitlines():
        ls = line.strip().lower()
        if any(kw in ls for kw in ("# todo", "# hack", "# legacy", "# regulation", "# compliance", "# fixme")):
            interesting.append(line.strip())
    bullets = "\n".join(f"- `{i}`" for i in interesting[:8]) or "- (no obvious hidden-logic markers detected heuristically)"
    return (
        f"**Heuristic scan of {module}:**\n\n{bullets}\n\n"
        f"Bob would normally read the full source and identify implicit business rules. "
        f"Configure BOB_ENDPOINT for the real analysis."
    )
