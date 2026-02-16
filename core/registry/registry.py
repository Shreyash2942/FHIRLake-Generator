from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Union

from .models import ResourceSpec
from .loader import build_registry

# Cache is keyed by normalized datasets_root path string
_RESOURCE_REGISTRY_CACHE: Dict[str, Dict[str, ResourceSpec]] = {}


def _normalize_root(datasets_root: Union[str, Path]) -> str:
    """
    Normalize datasets root into a stable cache key.
    """
    p = Path(datasets_root).resolve()
    return str(p)


def get_resource_registry(datasets_root: Union[str, Path] = "Datasets") -> Dict[str, ResourceSpec]:
    """
    Load registry (cached per datasets_root). Call this from planning/orchestrator/GUI.

    datasets_root: root folder to scan for resource_spec.py files.
    """
    key = _normalize_root(datasets_root)
    if key not in _RESOURCE_REGISTRY_CACHE:
        _RESOURCE_REGISTRY_CACHE[key] = build_registry(datasets_root=key)
    return _RESOURCE_REGISTRY_CACHE[key]


def supported_resource_types(datasets_root: Union[str, Path] = "Datasets") -> List[str]:
    """
    Return all supported FHIR resource types discovered from plugins.
    """
    return sorted(get_resource_registry(datasets_root).keys())


def reset_registry_cache(datasets_root: Optional[Union[str, Path]] = None) -> None:
    """
    Reset registry cache.

    - If datasets_root is None: clears all cached registries (useful in tests).
    - If datasets_root provided: clears only that registry root.
    """
    global _RESOURCE_REGISTRY_CACHE
    if datasets_root is None:
        _RESOURCE_REGISTRY_CACHE.clear()
        return

    key = _normalize_root(datasets_root)
    _RESOURCE_REGISTRY_CACHE.pop(key, None)
