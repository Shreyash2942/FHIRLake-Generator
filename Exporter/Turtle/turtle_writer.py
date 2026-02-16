from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from Exporter.naming import default_filename_base, plan_export_paths, resolve_filename_override

JsonDict = Dict[str, Any]


FHIR_PREFIX = "http://hl7.org/fhir/"
EX_PREFIX = "urn:fhirlake:resource/"


def _json_default(o: Any):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if hasattr(o, "model_dump"):
        return o.model_dump(exclude_none=True)
    return str(o)


def _ttl_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\"", "\\\"")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def _literal(value: Any) -> str:
    if value is None:
        return "\"\""
    if isinstance(value, (str, int, float, bool)):
        return f"\"{_ttl_escape(str(value))}\""
    return f"\"{_ttl_escape(json.dumps(value, ensure_ascii=False, default=_json_default))}\""


def serialize_turtle(records: Iterable[JsonDict]) -> str:
    lines: List[str] = [
        f"@prefix fhir: <{FHIR_PREFIX}> .",
        f"@prefix ex: <{EX_PREFIX}> .",
        "",
    ]

    blank_idx = 0
    for r in records:
        rtype = r.get("resourceType")
        rid = r.get("id")
        if isinstance(rtype, str) and isinstance(rid, str) and rid:
            subject = f"ex:{rtype}/{rid}"
        else:
            subject = f"_:b{blank_idx}"
            blank_idx += 1

        for k, v in r.items():
            predicate = f"fhir:{k}"
            lines.append(f"{subject} {predicate} {_literal(v)} .")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_turtle(records: Iterable[JsonDict], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(serialize_turtle(records), encoding="utf-8")
    return out_path



def plan_turtle_exports(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Tuple[Path, str]]:
    """
    Plan Turtle exports without writing files.

    Returns:
      bucket -> (relative_path, turtle_text)
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
            if not fname.endswith(".ttl"):
                fname = f"{fname}.ttl"
            rel_path = Path(fname)
        else:
            rel_path = Path(default_base) / f"{default_base}_{timestamp_utc}.ttl"
        outputs[bucket] = (rel_path, serialize_turtle(records))

    return outputs


def plan_turtle_paths(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Path]:
    """
    Plan Turtle export paths without serialization.

    Returns:
      bucket -> relative_path
    """
    return plan_export_paths(
        store_resources,
        filename_map=filename_map,
        timestamp_utc=timestamp_utc,
        run_id=run_id,
        extension=".ttl",
    )
