from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from Exporter.naming import default_filename_base, plan_export_paths, resolve_filename_override

JsonDict = Dict[str, Any]


def _json_default(o: Any):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if hasattr(o, "model_dump"):
        return o.model_dump(exclude_none=True)
    return str(o)


def write_ndjson(records: Iterable[JsonDict], out_path: str | Path) -> Path:
    """
    Write resources as NDJSON (one JSON object per line).
    Best for data lakes / streaming / Spark ingestion.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        for obj in records:
            f.write(json.dumps(obj, ensure_ascii=False, default=_json_default))
            f.write("\n")

    return out_path



def serialize_ndjson(records: Iterable[JsonDict]) -> str:
    lines: List[str] = []
    for obj in records:
        lines.append(json.dumps(obj, ensure_ascii=False, default=_json_default))
    return "\n".join(lines) + ("\n" if lines else "")


def plan_ndjson_exports(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Tuple[Path, str]]:
    """
    Plan NDJSON exports without writing files.

    Returns:
      bucket -> (relative_path, ndjson_text)
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
            if not fname.endswith(".ndjson"):
                fname = f"{fname}.ndjson"
            rel_path = Path(fname)
        else:
            rel_path = Path(default_base) / f"{default_base}_{timestamp_utc}.ndjson"
        outputs[bucket] = (rel_path, serialize_ndjson(records))

    return outputs


def plan_ndjson_paths(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Path]:
    """
    Plan NDJSON export paths without serialization.

    Returns:
      bucket -> relative_path
    """
    return plan_export_paths(
        store_resources,
        filename_map=filename_map,
        timestamp_utc=timestamp_utc,
        run_id=run_id,
        extension=".ndjson",
    )
