from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set


@dataclass(frozen=True, slots=True)
class UserRequest:
    """
    User intent (CLI/GUI).

    Preferred:
      - selected: resource types user explicitly selected
      - counts: absolute counts per resource type

    Optional legacy (temporary):
      - num_patients / encounters_per_patient / conditions_per_patient
      Use UserRequest.from_legacy(...) to construct a modern request.
    """
    selected: Set[str]
    counts: Optional[Dict[str, int]] = None

    # legacy knobs (optional)
    num_patients: int = 10
    encounters_per_patient: int = 3
    conditions_per_patient: int = 2

    seed: Optional[int] = None
    strict: bool = True
    include_optional: bool = False

    @staticmethod
    def from_legacy(
        *,
        num_patients: int,
        encounters_per_patient: int,
        conditions_per_patient: int,
        seed: Optional[int] = None,
        strict: bool = True,
    ) -> "UserRequest":
        """
        Build a modern request from legacy count knobs.
        This is a temporary compatibility helper.
        """
        selected = {"Patient", "Encounter", "Condition"}
        counts = {
            "Patient": max(0, int(num_patients)),
            "Encounter": max(0, int(encounters_per_patient)),
            "Condition": max(0, int(conditions_per_patient)),
        }
        return UserRequest(
            selected=selected,
            counts=counts,
            seed=seed,
            strict=strict,
            num_patients=num_patients,
            encounters_per_patient=encounters_per_patient,
            conditions_per_patient=conditions_per_patient,
        )


@dataclass(frozen=True, slots=True)
class PlanNode:
    resource_type: str
    generator_key: str
    count: int
    dependencies: List[str]


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """
    Final expanded and ordered plan for execution.
    """
    run_id: str
    created_at: str
    selected: Set[str]
    expanded: Set[str]
    order: List[str]
    nodes: Dict[str, PlanNode]
    counts: Dict[str, int]
    seed: Optional[int] = None
