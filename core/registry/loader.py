from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import importlib.util

from .models import ResourceSpec


class RegistryLoadError(RuntimeError):
    pass


def _load_module_from_path(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise RegistryLoadError(f"Failed to create import spec for: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def discover_resource_specs(
    datasets_root: str | Path,
    spec_filename: str = "resource_spec.py",
) -> List[Tuple[Path, ResourceSpec]]:
    """
    Discover and load ResourceSpec entries from dataset folders.

    Expected convention:
      Each resource folder contains a file named 'resource_spec.py'
      that defines a top-level variable: RESOURCE_SPEC (ResourceSpec)
    """
    datasets_root = Path(datasets_root)
    if not datasets_root.exists():
        raise RegistryLoadError(f"Datasets root not found: {datasets_root}")

    spec_files = sorted(datasets_root.rglob(spec_filename))
    loaded: List[Tuple[Path, ResourceSpec]] = []

    for i, spec_path in enumerate(spec_files, start=1):
        # Create a stable unique module name to avoid collisions
        module_name = f"fhirlake_resource_spec_{i}"

        module = _load_module_from_path(module_name, spec_path)

        if not hasattr(module, "RESOURCE_SPEC"):
            raise RegistryLoadError(
                f"Missing RESOURCE_SPEC in {spec_path}. "
                f"Each {spec_filename} must define RESOURCE_SPEC = ResourceSpec(...)."
            )

        spec_obj = getattr(module, "RESOURCE_SPEC")
        if not isinstance(spec_obj, ResourceSpec):
            raise RegistryLoadError(
                f"RESOURCE_SPEC in {spec_path} is not a ResourceSpec. "
                f"Got: {type(spec_obj)}"
            )

        loaded.append((spec_path, spec_obj))

    return loaded


def build_registry(
    datasets_root: str | Path,
) -> Dict[str, ResourceSpec]:
    """
    Builds the full registry dict:
      key: resource_type
      value: ResourceSpec

    Validates:
      - no duplicate resource_type
    """
    discovered = discover_resource_specs(datasets_root=datasets_root)
    registry: Dict[str, ResourceSpec] = {}

    for path, spec in discovered:
        if spec.resource_type in registry:
            raise RegistryLoadError(
                f"Duplicate resource_type '{spec.resource_type}' found.\n"
                f"Duplicate from: {path}"
            )
        registry[spec.resource_type] = spec

    return registry
