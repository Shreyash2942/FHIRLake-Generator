from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


MissingDependencyAction = Literal["AUTO_CREATE", "ERROR", "FALLBACK"]


@dataclass(frozen=True)
class LinkingPolicy:
    """
    Central place for relationship enforcement decisions.

    encounter_required_for_condition:
      - AUTO_CREATE: create encounter if none exists for the patient
      - ERROR: fail if none exists
      - FALLBACK: allow missing and store fallback (later)
    """
    encounter_required_for_condition: MissingDependencyAction = "AUTO_CREATE"
