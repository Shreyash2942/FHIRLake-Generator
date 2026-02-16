# core/planning/planner.py

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, List, Set, Iterable, Any

from .models import UserRequest, ExecutionPlan, PlanNode
from .exceptions import (
    PlanningError,
    UnknownResourceTypeError,
    DependencyCycleError,
    InvalidCountsError,
)


# -----------------------------
# Registry compatibility layer
# -----------------------------

def _reg_has(registry: Any, rt: str) -> bool:
    """Support dict-style registry or Registry object with .has()."""
    if hasattr(registry, "has"):
        return registry.has(rt)
    return rt in registry


def _reg_get(registry: Any, rt: str):
    """Support dict-style registry or Registry object with .get()."""
    if hasattr(registry, "get") and not isinstance(registry, dict):
        # registry object API
        return registry.get(rt)
    # dict registry (or mapping)
    return registry[rt]


def _deps_of(spec) -> List[str]:
    """
    IMPORTANT:
      - In your Registry: spec.dependencies = resource-type dependencies (used by Planning)
      - spec.required_inputs = generator input keys (used later by Resolver/Runtime)
    """
    deps = getattr(spec, "dependencies", None)
    if deps is None:
        # fallback support if some specs still used required_inputs historically
        deps = getattr(spec, "required_inputs", None)
    return list(deps or [])


def _optional_deps_of(spec) -> List[str]:
    deps = getattr(spec, "optional_dependencies", None)
    return list(deps or [])


def _deps_for_planning(spec, *, include_optional: bool) -> List[str]:
    if include_optional:
        return list(_deps_of(spec)) + list(_optional_deps_of(spec))
    return list(_deps_of(spec))


# -----------------------------
# Public API
# -----------------------------

def build_plan(req: UserRequest, registry) -> ExecutionPlan:
    _validate_selected(req, registry)

    expanded = _expand_dependencies(req.selected, registry, include_optional=req.include_optional)
    graph = _build_dependency_graph(expanded, registry, include_optional=req.include_optional)
    order = _topological_sort(graph)
    counts = _validate_and_finalize_counts(req, expanded, registry, include_optional=req.include_optional)

    nodes: Dict[str, PlanNode] = {}
    for rt in expanded:
        spec = _reg_get(registry, rt)
        nodes[rt] = PlanNode(
            resource_type=rt,
            generator_key=rt,
            count=counts[rt],
            dependencies=_deps_for_planning(spec, include_optional=req.include_optional),
        )

    return ExecutionPlan(
        run_id=str(uuid4()),
        created_at=datetime.now(timezone.utc).isoformat(),
        selected=set(req.selected),
        expanded=set(expanded),
        order=order,
        nodes=nodes,
        counts=counts,
        seed=req.seed,
    )


# -----------------------------
# Helpers
# -----------------------------

def _validate_selected(req: UserRequest, registry) -> None:
    unknown = [rt for rt in req.selected if not _reg_has(registry, rt)]
    if unknown:
        raise UnknownResourceTypeError(f"Unknown resource types requested: {unknown}")


def _expand_dependencies(selected: Set[str], registry, *, include_optional: bool) -> Set[str]:
    expanded = set(selected)
    stack = list(selected)

    while stack:
        rt = stack.pop()
        spec = _reg_get(registry, rt)

        for dep in _deps_for_planning(spec, include_optional=include_optional):
            if not _reg_has(registry, dep):
                raise UnknownResourceTypeError(
                    f"Resource '{rt}' depends on unknown resource '{dep}'."
                )
            if dep not in expanded:
                expanded.add(dep)
                stack.append(dep)

    return expanded


def _build_dependency_graph(resources: Set[str], registry, *, include_optional: bool) -> Dict[str, Set[str]]:
    """
    Graph edges: dep -> rt   (dep must run before rt)
    """
    graph: Dict[str, Set[str]] = {rt: set() for rt in resources}

    for rt in resources:
        spec = _reg_get(registry, rt)
        for dep in _deps_for_planning(spec, include_optional=include_optional):
            if dep in resources:
                graph.setdefault(dep, set()).add(rt)
                graph.setdefault(rt, set())

    return graph


def _topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
    indegree = {n: 0 for n in graph}
    for u, vs in graph.items():
        for v in vs:
            indegree[v] += 1

    # Deterministic order with better performance than repeatedly sorting a list.
    import heapq
    heap = [n for n, d in indegree.items() if d == 0]
    heapq.heapify(heap)
    order: List[str] = []

    while heap:
        node = heapq.heappop(heap)
        order.append(node)
        for child in sorted(graph.get(node, [])):
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(heap, child)

    if len(order) != len(graph):
        cycle_nodes = [n for n, d in indegree.items() if d > 0]
        raise DependencyCycleError(f"Dependency cycle detected among: {cycle_nodes}")

    return order


def _validate_and_finalize_counts(
    req: UserRequest,
    expanded: Set[str],
    registry,
    *,
    include_optional: bool,
) -> Dict[str, int]:
    """
    Counts rules:
      - If req.counts provided: validate them
      - Ensure every expanded resource has a count (default 0)
      - If count(X)>0 and X depends on Y -> count(Y)>0
    """
    counts = dict(req.counts or {})

    # basic sanity for provided counts
    bad = {k: v for k, v in counts.items() if v is None or v < 0}
    if bad:
        raise InvalidCountsError(f"Invalid counts (must be >= 0): {bad}")

    # strict: selected must have explicit counts (if using counts)
    if req.strict and req.counts is not None:
        missing = [rt for rt in req.selected if rt not in counts]
        if missing:
            raise InvalidCountsError(f"Missing counts for selected resource types: {missing}")

    # default missing expanded deps to 0
    for rt in expanded:
        counts.setdefault(rt, 0)

    # dependency-count validation
    problems: List[str] = []
    for rt in expanded:
        if counts.get(rt, 0) > 0:
            spec = _reg_get(registry, rt)
            for dep in _deps_for_planning(spec, include_optional=include_optional):
                if counts.get(dep, 0) <= 0:
                    problems.append(
                        f"{rt}={counts.get(rt)} depends on {dep}={counts.get(dep)}"
                    )

    if problems:
        raise InvalidCountsError(
            "Invalid counts due to dependency violations:\n- " + "\n- ".join(problems)
        )

    return counts
