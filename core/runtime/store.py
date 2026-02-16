from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Set, Tuple


JsonDict = Dict[str, Any]


# ----------------------------
# Naming conventions
# ----------------------------

def pool_name(resource_type: str) -> str:
    """
    Standard pool name for IDs.
    Example: Patient -> patient_ids
    """
    return f"{resource_type.lower()}_ids"


def link_index_name(parent: str, child: str) -> str:
    """
    Standard link index name.
    Example: Patient -> Encounter => patient_to_encounter
    """
    return f"{parent.lower()}_to_{child.lower()}"


# ----------------------------
# ResourceStore
# ----------------------------

@dataclass(slots=True)
class ResourceStore:
    """
    Generic, future-proof in-memory store.

    - Stores resources by registry-defined bucket
    - Tracks existence of (resourceType, id)
    - Provides generic pools + link indexes
    """

    # bucket -> list[resource_json]
    resources: Dict[str, List[JsonDict]] = field(default_factory=dict)

    # pool_name -> list[str]
    pools: Dict[str, List[str]] = field(default_factory=dict)

    # index_name -> {key -> [values]}
    links: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)

    # fast reference existence check
    _id_set: Set[Tuple[str, str]] = field(default_factory=set, init=False)

    # ----------------------------
    # Add resources
    # ----------------------------
    def add(self, bucket: str, resource: JsonDict) -> None:
        rid = resource.get("id")
        rtype = resource.get("resourceType")

        if not rid or not rtype:
            raise ValueError(
                f"Resource missing required fields: id={rid}, resourceType={rtype}"
            )

        self.resources.setdefault(bucket, []).append(resource)
        self._id_set.add((rtype, rid))

    def add_many(self, bucket: str, resources: Iterable[JsonDict]) -> None:
        for r in resources:
            self.add(bucket, r)

    def add_from_spec(self, spec: Any, resource: JsonDict) -> None:
        bucket = getattr(spec, "bucket", None)
        if not bucket:
            raise ValueError("Registry spec missing 'bucket'")
        self.add(bucket, resource)

    def add_many_from_spec(self, spec: Any, resources: Iterable[JsonDict]) -> None:
        bucket = getattr(spec, "bucket", None)
        if not bucket:
            raise ValueError("Registry spec missing 'bucket'")
        self.add_many(bucket, resources)

    # ----------------------------
    # Queries
    # ----------------------------
    def exists(self, resource_type: str, resource_id: str) -> bool:
        return (resource_type, resource_id) in self._id_set

    def get_bucket(self, bucket: str) -> List[JsonDict]:
        return self.resources.get(bucket, [])

    def counts_by_bucket(self) -> Dict[str, int]:
        return {b: len(v) for b, v in self.resources.items()}

    # ----------------------------
    # Pools (generic)
    # ----------------------------
    def add_to_pool(self, pool: str, value: str) -> None:
        self.pools.setdefault(pool, []).append(value)

    def extend_pool(self, pool: str, values: Iterable[str]) -> None:
        self.pools.setdefault(pool, []).extend(list(values))

    def get_pool(self, pool: str) -> List[str]:
        return self.pools.get(pool, [])

    def register_id(self, resource_type: str, resource_id: str) -> None:
        """
        Registers an ID using standard convention.
        """
        self.add_to_pool(pool_name(resource_type), resource_id)

    # ----------------------------
    # Links (generic)
    # ----------------------------
    def link(self, index: str, key: str, value: str) -> None:
        self.links.setdefault(index, {}).setdefault(key, []).append(value)

    def get_links(self, index: str, key: str) -> List[str]:
        return self.links.get(index, {}).get(key, [])

    def register_link(
        self,
        parent_type: str,
        parent_id: str,
        child_type: str,
        child_id: str,
    ) -> None:
        """
        Registers a parent -> child relationship using standard naming.
        """
        self.link(
            link_index_name(parent_type, child_type),
            parent_id,
            child_id,
        )

    def register_generated_resources(
        self,
        *,
        default_resource_type: str,
        resources: Iterable[JsonDict],
        parent_refs: Iterable[Tuple[str, str]],
    ) -> Tuple[int, int]:
        """
        Register IDs and parent links for generated resources.
        Returns (ids_registered, links_registered).
        """
        registered = 0
        linked = 0
        for r in resources:
            rid = r.get("id")
            rtype = r.get("resourceType", default_resource_type)
            if not rid:
                continue

            self.register_id(rtype, rid)
            registered += 1

            for parent_type, parent_id in parent_refs:
                self.register_link(parent_type, parent_id, rtype, rid)
                linked += 1

        return registered, linked


