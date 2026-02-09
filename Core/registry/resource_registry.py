from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


# Policy choices for dependency handling (used later by linking/planning)
DependencyPolicy = Literal["AUTO_CREATE", "ERROR", "FALLBACK"]


@dataclass(frozen=True)
class ResourceSpec:
    """
    One registry entry per FHIR resource type.

    resource_type: FHIR name e.g. "Patient"
    bucket: store bucket key e.g. "patients" used by ResourceStore + exporter
    generator: import string "module.path:function_name"
    dependencies: resource types that must exist before generating this resource
    dependency_policy: how to handle missing dependencies (default AUTO_CREATE)
    """
    resource_type: str
    bucket: str
    generator: str
    dependencies: List[str] = field(default_factory=list)
    dependency_policy: DependencyPolicy = "AUTO_CREATE"
    description: Optional[str] = None


# ✅ v1 registry (Patient, Encounter, Condition)
# NOTE: generator strings must match your real module paths.
RESOURCE_REGISTRY: Dict[str, ResourceSpec] = {
    "Patient": ResourceSpec(
        resource_type="Patient",
        bucket="patients",
        generator="patient.generate_patient_fhir:generate_patient",
        dependencies=[],
        description="Synthetic Patient resource generator.",
    ),
    "Encounter": ResourceSpec(
        resource_type="Encounter",
        bucket="encounters",
        generator="encounter.generate_encounter_fhir:generate_encounter",
        dependencies=["Patient"],
        description="Synthetic Encounter linked to Patient.",
    ),
    "Condition": ResourceSpec(
        resource_type="Condition",
        bucket="conditions",
        generator="condition.generate_condition_fhir:generate_condition",
        # We keep dependencies data-driven. In your analytics contract,
        # Condition should usually link to Encounter too.
        dependencies=["Patient", "Encounter"],
        dependency_policy="AUTO_CREATE",
        description="Synthetic Condition linked to Patient and Encounter.",
    ),
}


def supported_resource_types() -> List[str]:
    """Return all supported FHIR resource types."""
    return sorted(RESOURCE_REGISTRY.keys())
