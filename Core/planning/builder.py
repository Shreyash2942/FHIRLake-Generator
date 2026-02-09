from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from Core.registry import RESOURCE_REGISTRY
from .models import UserRequest, GenerationPlan


class PlanningError(ValueError):
    """Raised when the user request cannot be planned safely."""


def _validate_supported(requested: List[str]) -> None:
    unsupported = [r for r in requested if r not in RESOURCE_REGISTRY]
    if unsupported:
        raise PlanningError(
            f"Unsupported resource types: {unsupported}. "
            f"Supported: {sorted(RESOURCE_REGISTRY.keys())}"
        )


def _expand_dependencies(requested: List[str]) -> List[str]:
    """
    Expand requested resource types by recursively adding dependencies.
    """
    _validate_supported(requested)

    expanded: Set[str] = set()

    def add_with_deps(rtype: str) -> None:
        if rtype in expanded:
            return
        expanded.add(rtype)
        spec = RESOURCE_REGISTRY[rtype]
        for dep in spec.dependencies:
            add_with_deps(dep)

    for r in requested:
        add_with_deps(r)

    return sorted(expanded)


def _topological_sort(resource_types: List[str]) -> List[str]:
    """
    Topological sort for execution order.
    Ensures dependencies appear before dependents.
    """
    # Build adjacency and in-degree restricted to resource_types set
    node_set = set(resource_types)
    in_degree: Dict[str, int] = {n: 0 for n in node_set}
    edges: Dict[str, List[str]] = {n: [] for n in node_set}

    for n in node_set:
        deps = [d for d in RESOURCE_REGISTRY[n].dependencies if d in node_set]
        for d in deps:
            edges[d].append(n)
            in_degree[n] += 1

    # Kahn's algorithm
    queue = [n for n, deg in in_degree.items() if deg == 0]
    ordered: List[str] = []

    while queue:
        current = queue.pop(0)
        ordered.append(current)
        for nxt in edges[current]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    if len(ordered) != len(node_set):
        raise PlanningError(
            "Dependency cycle detected in registry. "
            "Check RESOURCE_REGISTRY dependencies."
        )

    return ordered


def build_plan(req: UserRequest) -> GenerationPlan:
    """
    Build a full generation plan:
    - validate requested resources
    - expand dependencies
    - compute execution order
    - enforce basic numeric requirements
    """
    requested = req.selected_resource_types
    if not requested:
        raise PlanningError("No resources selected. Please select at least one resource type.")

    _validate_supported(requested)

    expanded = _expand_dependencies(requested)
    ordered = _topological_sort(expanded)

    # Basic enforcement rules for v1 (can be moved to policy engine later)
    # If Encounter is in expanded set, you must generate at least 1 patient.
    if "Patient" in expanded and req.num_patients <= 0:
        raise PlanningError("num_patients must be > 0 when Patient is required.")

    # If Encounter required, ensure encounters_per_patient >= 1
    if "Encounter" in expanded and req.encounters_per_patient <= 0:
        raise PlanningError(
            "Encounter is required by selected resources; encounters_per_patient must be >= 1."
        )

    # If Condition required, ensure conditions_per_patient >= 0 (0 is allowed)
    if "Condition" in expanded and req.conditions_per_patient < 0:
        raise PlanningError("conditions_per_patient must be >= 0.")

    run_params = {
        "num_patients": req.num_patients,
        "encounters_per_patient": req.encounters_per_patient,
        "conditions_per_patient": req.conditions_per_patient,
    }

    return GenerationPlan(
        requested=requested,
        expanded=expanded,
        ordered=ordered,
        run_params=run_params,
        seed=req.seed,
    )
