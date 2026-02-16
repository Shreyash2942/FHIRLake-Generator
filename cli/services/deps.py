from __future__ import annotations

from typing import Dict, List, Set


def get_dependencies(registry: Dict[str, object], resource_type: str) -> List[str]:
    spec = registry[resource_type]
    deps = getattr(spec, "dependencies", None) or []
    return list(deps)


def get_optional_dependencies(registry: Dict[str, object], resource_type: str) -> List[str]:
    spec = registry[resource_type]
    deps = getattr(spec, "optional_dependencies", None) or []
    return list(deps)


def expand_dependencies(
    selected: Set[str],
    registry: Dict[str, object],
    *,
    include_optional: bool = False,
) -> Set[str]:
    expanded = set(selected)
    stack = list(selected)
    while stack:
        rt = stack.pop()
        deps = list(get_dependencies(registry, rt))
        if include_optional:
            deps.extend(get_optional_dependencies(registry, rt))
        for dep in deps:
            if dep not in expanded:
                expanded.add(dep)
                stack.append(dep)
    return expanded


def dependency_defaults(
    selected_counts: Dict[str, int],
    registry: Dict[str, object],
    *,
    include_optional: bool = False,
) -> Dict[str, int]:
    defaults: Dict[str, int] = {}
    for rt, count in selected_counts.items():
        closure = expand_dependencies({rt}, registry, include_optional=include_optional)
        for dep in closure:
            if dep == rt:
                continue
            defaults[dep] = max(defaults.get(dep, 0), count)
    return defaults
