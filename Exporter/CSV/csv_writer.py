from __future__ import annotations

import csv
import json
from datetime import date, datetime
from io import StringIO
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


def _stringify_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, default=_json_default)


def _collect_headers(records: Iterable[JsonDict]) -> List[str]:
    keys = set()
    for r in records:
        keys.update(r.keys())
    ordered = []
    for k in ("resourceType", "id"):
        if k in keys:
            ordered.append(k)
            keys.remove(k)
    ordered.extend(sorted(keys))
    return ordered


def serialize_csv(records: Iterable[JsonDict]) -> str:
    records_list = list(records)
    headers = _collect_headers(records_list)

    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    for r in records_list:
        row = {k: _stringify_cell(r.get(k)) for k in headers}
        writer.writerow(row)
    return out.getvalue()


def write_csv(records: Iterable[JsonDict], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = serialize_csv(records)
    out_path.write_text(content, encoding="utf-8", newline="")
    return out_path



def plan_csv_exports(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Tuple[Path, str]]:
    """
    Plan CSV exports without writing files.

    Returns:
      bucket -> (relative_path, csv_text)
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
            if not fname.endswith(".csv"):
                fname = f"{fname}.csv"
            rel_path = Path(fname)
        else:
            rel_path = Path(default_base) / f"{default_base}_{timestamp_utc}.csv"
        outputs[bucket] = (rel_path, serialize_csv(records))

    return outputs


def plan_csv_paths(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Path]:
    """
    Plan CSV export paths without serialization.

    Returns:
      bucket -> relative_path
    """
    return plan_export_paths(
        store_resources,
        filename_map=filename_map,
        timestamp_utc=timestamp_utc,
        run_id=run_id,
        extension=".csv",
    )
