from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable


def default_filename_base(bucket: str, records: Iterable[Dict[str, Any]]) -> str:
    records_list = list(records)
    if not records_list:
        return bucket
    resource_type = records_list[0].get("resourceType")
    if not isinstance(resource_type, str) or not resource_type:
        return bucket
    for r in records_list[1:]:
        if r.get("resourceType") != resource_type:
            return bucket
    return resource_type.lower()


def resolve_filename_override(fname: str | None, *, timestamp_utc: str, run_id: str) -> str | None:
    if not fname:
        return None
    out = fname.replace("{timestamp}", timestamp_utc)
    out = out.replace("{run_id}", run_id[:8])
    return out


def plan_export_paths(
    store_resources: Dict[str, Iterable[Dict[str, Any]]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
    extension: str,
) -> Dict[str, Path]:
    """
    Plan export paths without serialization.
    Returns bucket -> relative_path
    """
    filename_map = filename_map or {}
    outputs: Dict[str, Path] = {}

    ext = extension if extension.startswith(".") else f".{extension}"

    for bucket, records in store_resources.items():
        default_base = default_filename_base(bucket, records)
        fname = resolve_filename_override(
            filename_map.get(bucket),
            timestamp_utc=timestamp_utc,
            run_id=run_id,
        )
        if fname:
            if not fname.endswith(ext):
                fname = f"{fname}{ext}"
            rel_path = Path(fname)
        else:
            rel_path = Path(default_base) / f"{default_base}-{timestamp_utc}{ext}"
        outputs[bucket] = rel_path

    return outputs
