from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True, slots=True)
class ResolvedInputs:
    """
    Returned by Resolver.

    values:
        Concrete inputs passed into a generator.
        Example: {"patient_id": "pat-1", "encounter_id": "enc-7"}

    parent_refs:
        Parent references implied by resolved inputs:
        [("Patient", "pat-1"), ("Encounter", "enc-7")]

        Orchestrator can use this later to register links AFTER
        the child resource is generated (when child ids are known).
    """
    values: Dict[str, Optional[str]]
    parent_refs: List[Tuple[str, str]]
