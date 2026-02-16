from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from core.runtime.store import pool_name  # runtime convention helper
from .models import ResolvedInputs
from .exceptions import (
    MissingDependencyError,
    AutoCreateDependencyError,
    InvalidInputKeyError,
)
from .strategies import RoundRobinStrategy


def _input_key_to_resource_type(input_key: str) -> str:
    """
    Map generator input keys like 'patient_id' -> 'Patient'.

    Rules (future-proof, no registry changes):
    - input key must end with '_id'
    - snake_case -> PascalCase
      ex: medication_request_id -> MedicationRequest
    """
    if not input_key.endswith("_id"):
        raise InvalidInputKeyError(
            f"Cannot map input key '{input_key}' to a resource type. Expected '*_id'."
        )

    base = input_key[:-3]  # remove '_id'
    parts = [p for p in base.split("_") if p]
    if not parts:
        raise InvalidInputKeyError(f"Invalid input key '{input_key}'.")

    return "".join(p[:1].upper() + p[1:] for p in parts)


logger = logging.getLogger(__name__)


def _get_policy(spec: Any) -> str:
    """
    Dependency policy options:
    - AUTO_CREATE (default): signal orchestrator to create missing parents
    - ERROR: raise MissingDependencyError immediately
    - FALLBACK: return None for missing inputs
    """
    policy = getattr(spec, "dependency_policy", "AUTO_CREATE") or "AUTO_CREATE"
    if hasattr(policy, "value"):
        return str(policy.value)
    return str(policy)


@dataclass(slots=True)
class Resolver:
    """
    Resolver resolves spec.required_inputs into concrete IDs from ResourceStore pools.

    Future-proof rules:
    - Uses spec.required_inputs like ['patient_id', 'encounter_id']
    - Pulls IDs from pools using convention: '{resource_type.lower()}_ids'
    - Does NOT hardcode resource names.
    """

    _rr: RoundRobinStrategy[str] = field(default_factory=RoundRobinStrategy)

    def resolve(
        self,
        resource_type: str,
        spec: Any,
        ctx: Any,
        store: Any,
        registry: Optional[Any] = None,  # reserved for future enhancements
    ) -> ResolvedInputs:
        required: Iterable[str] = getattr(spec, "required_inputs", []) or []
        optional: Iterable[str] = getattr(spec, "optional_inputs", []) or []
        values: Dict[str, Optional[str]] = {}
        parent_refs: List[Tuple[str, str]] = []

        policy = _get_policy(spec)

        for key in required:
            # Optional advanced override mapping:
            # spec.input_resource_types = {"subject_id": "Patient"} etc.
            mapping = getattr(spec, "input_resource_types", None)
            if isinstance(mapping, dict) and key in mapping:
                parent_type = mapping[key]
            else:
                parent_type = _input_key_to_resource_type(key)
                logger.debug(
                    "Resolver inferred parent_type '%s' from input key '%s' for resource '%s'",
                    parent_type,
                    key,
                    resource_type,
                )

            pid = self._pick_id(parent_type, ctx, store)

            if pid is None:
                if policy == "ERROR":
                    raise MissingDependencyError(
                        f"Missing '{parent_type}' IDs required for '{resource_type}' (input '{key}')."
                    )
                if policy == "FALLBACK":
                    values[key] = None
                    continue

                # AUTO_CREATE (default)
                raise AutoCreateDependencyError(
                    parent_type,
                    f"Missing '{parent_type}' IDs required for '{resource_type}' (AUTO_CREATE).",
                )

            values[key] = pid
            parent_refs.append((parent_type, pid))

        for key in optional:
            mapping = getattr(spec, "input_resource_types", None)
            if isinstance(mapping, dict) and key in mapping:
                parent_type = mapping[key]
            else:
                parent_type = _input_key_to_resource_type(key)
                logger.debug(
                    "Resolver inferred parent_type '%s' from input key '%s' for resource '%s' (optional)",
                    parent_type,
                    key,
                    resource_type,
                )

            pid = self._pick_id(parent_type, ctx, store)
            if pid is None:
                values[key] = None
                continue

            values[key] = pid
            parent_refs.append((parent_type, pid))

        return ResolvedInputs(values=values, parent_refs=parent_refs)

    def _pick_id(self, parent_resource_type: str, ctx: Any, store: Any) -> Optional[str]:
        pool = pool_name(parent_resource_type)

        items: Sequence[str] = store.get_pool(pool) if hasattr(store, "get_pool") else []
        if not items:
            return None

        rng = getattr(ctx, "rng", None)
        if rng is not None and hasattr(rng, "choice"):
            return rng.choice(list(items))

        return self._rr.pick(list(items))


def resolve_inputs(
    resource_type: str,
    spec: Any,
    ctx: Any,
    store: Any,
    registry: Optional[Any] = None,
) -> ResolvedInputs:
    """Functional wrapper for convenience."""
    return Resolver().resolve(resource_type, spec, ctx, store, registry=registry)
