from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass(frozen=True)
class UserRequest:
    """
    What the user asked to generate (CLI/GUI).

    selected_resource_types: list of FHIR resource types the user selected
    """
    selected_resource_types: List[str]

    # Optional run parameters (can grow later)
    num_patients: int = 10
    encounters_per_patient: int = 3
    conditions_per_patient: int = 2
    seed: Optional[int] = None


@dataclass(frozen=True)
class GenerationPlan:
    """
    Final expanded and ordered plan for execution.
    """
    requested: List[str]
    expanded: List[str]         # requested + auto-added dependencies
    ordered: List[str]          # execution order from dependency graph
    run_params: Dict[str, int]  # numeric parameters used by orchestrator
    seed: Optional[int] = None
