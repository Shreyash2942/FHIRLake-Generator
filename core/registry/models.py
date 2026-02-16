from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union


class DependencyPolicyEnum(str, Enum):
    AUTO_CREATE = "AUTO_CREATE"
    ERROR = "ERROR"
    FALLBACK = "FALLBACK"


DependencyPolicy = Union[DependencyPolicyEnum, str]


@dataclass(frozen=True, slots=True)
class ResourceSpec:
    """
    One registry entry per FHIR resource type.

    resource_type: FHIR name e.g. "Patient"
    bucket: store bucket key e.g. "patients" used by ResourceStore + exporter
    generator: import string "module.path:function_name"
    dependencies: resource types that must exist before generating this resource
    dependency_policy: how to handle missing dependencies (default AUTO_CREATE)
    required_inputs: generator input keys that must be resolved by engine/linking
                     e.g. ["patient_id", "encounter_id"]
    description: human-friendly description (GUI tooltips)
    """
    resource_type: str
    bucket: str
    generator: str
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    dependency_policy: DependencyPolicy = DependencyPolicyEnum.AUTO_CREATE
    required_inputs: List[str] = field(default_factory=list)
    optional_inputs: List[str] = field(default_factory=list)
    description: Optional[str] = None
