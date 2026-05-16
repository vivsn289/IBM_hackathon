"""Pydantic request/response models for the REST API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    path: str


class QueryRequest(BaseModel):
    query: str


class ModernizeRequest(BaseModel):
    target: str


class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    cycles: List[List[str]]
    stats: Dict[str, int]


class BobResponse(BaseModel):
    answer: str
    structured: Optional[Dict[str, Any]] = None
