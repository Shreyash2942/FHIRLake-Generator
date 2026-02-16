from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from Exporter.naming import default_filename_base, plan_export_paths, resolve_filename_override

JsonDict = Dict[str, Any]


def _json_default(o: Any):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if hasattr(o, "model_dump"):
        return o.model_dump(exclude_none=True)
    return str(o)


def write_json_array(records: List[JsonDict], out_path: str | Path, indent: int = 2) -> Path:
    """
    Write resources as a JSON array.
    Best for human readability and quick inspection.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=indent, default=_json_default)

    return out_path



def serialize_json_array(records: List[JsonDict], indent: int = 2) -> str:
    return json.dumps(records, ensure_ascii=False, indent=indent, default=_json_default)


def plan_json_exports(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    indent: int = 2,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Tuple[Path, str]]:
    """
    Plan JSON exports without writing files.

    Returns:
      bucket -> (relative_path, json_text)
    """
    filename_map = filename_map or {}
    outputs: Dict[str, Tuple[Path, str]] = {}

    for bucket, records in store_resources.items():
        default_base = default_filename_base(bucket, records)
        fname = resolve_filename_override(
            filename_map.get(bucket),
            timestamp_utc=timestamp_utc,
            run_id=run_id,
        )
        if fname:
            rel_path = Path(fname)
        else:
            rel_path = Path(default_base) / f"{default_base}_{timestamp_utc}.json"
        outputs[bucket] = (rel_path, serialize_json_array(records, indent=indent))

    return outputs


def plan_json_paths(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Path]:
    """
    Plan JSON export paths without serialization.

    Returns:
      bucket -> relative_path
    """
    return plan_export_paths(
        store_resources,
        filename_map=filename_map,
        timestamp_utc=timestamp_utc,
        run_id=run_id,
        extension=".json",
    )
