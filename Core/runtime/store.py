# Core/runtime/store.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


JsonDict = Dict[str, Any]


@dataclass
class ResourceStore:
    """
    ResourceStore is an in-memory store for generated resources.

    ✅ Stores resources by type (patients, encounters, conditions, ...)
    ✅ Tracks indexes for linking and fast lookups:
       - patient_id -> encounter_ids
       - patient_id -> condition_ids
       - encounter_id -> condition_ids

    Note: The "linking rules" will live in the next module.
    This store just tracks what's created.
    """
    resources: Dict[str, List[JsonDict]] = field(default_factory=dict)

    # Primary indexes
    patient_to_encounters: Dict[str, List[str]] = field(default_factory=dict)
    patient_to_conditions: Dict[str, List[str]] = field(default_factory=dict)
    encounter_to_conditions: Dict[str, List[str]] = field(default_factory=dict)

    # Fast existence checks by (resource_type, id)
    _id_set: Set[Tuple[str, str]] = field(default_factory=set, init=False)

    def add(self, resource_type: str, resource_json: JsonDict) -> None:
        """
        Add a resource JSON dict into the store and update existence index.
        Requires: resource_json must contain "id" and "resourceType"
        """
        rid = resource_json.get("id")
        rtype = resource_json.get("resourceType")

        if not rid or not rtype:
            raise ValueError(
                f"Resource missing required keys. Found id={rid}, resourceType={rtype}"
            )

        # Keep user-friendly keys like "patients", "encounters", etc.
        bucket = self.resources.setdefault(resource_type, [])
        bucket.append(resource_json)

        # Existence index uses the actual FHIR resourceType
        self._id_set.add((rtype, rid))

    def exists(self, fhir_resource_type: str, resource_id: str) -> bool:
        """Check if a resource exists in the store by (FHIR resourceType, id)."""
        return (fhir_resource_type, resource_id) in self._id_set

    # ----------------------------
    # Relationship index helpers
    # ----------------------------
    def link_patient_encounter(self, patient_id: str, encounter_id: str) -> None:
        self.patient_to_encounters.setdefault(patient_id, []).append(encounter_id)

    def link_patient_condition(self, patient_id: str, condition_id: str) -> None:
        self.patient_to_conditions.setdefault(patient_id, []).append(condition_id)

    def link_encounter_condition(self, encounter_id: str, condition_id: str) -> None:
        self.encounter_to_conditions.setdefault(encounter_id, []).append(condition_id)

    # ----------------------------
    # Query helpers
    # ----------------------------
    def get_patient_encounters(self, patient_id: str) -> List[str]:
        return self.patient_to_encounters.get(patient_id, [])

    def get_patient_conditions(self, patient_id: str) -> List[str]:
        return self.patient_to_conditions.get(patient_id, [])

    def get_encounter_conditions(self, encounter_id: str) -> List[str]:
        return self.encounter_to_conditions.get(encounter_id, [])

    def counts(self) -> Dict[str, int]:
        """Convenient summary counts per bucket (patients/encounters/etc.)."""
        return {k: len(v) for k, v in self.resources.items()}
