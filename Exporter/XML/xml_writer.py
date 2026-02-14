from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from Exporter.naming import default_filename_base, plan_export_paths, resolve_filename_override
from xml.etree import ElementTree as ET


JsonDict = Dict[str, Any]


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "model_dump"):
        value = value.model_dump(exclude_none=True)
    return str(value)


def _append_value(parent: ET.Element, key: str, value: Any) -> None:
    child = ET.SubElement(parent, key)
    if isinstance(value, dict):
        for k, v in value.items():
            _append_value(child, k, v)
    elif isinstance(value, list):
        for item in value:
            _append_value(child, "item", item)
    else:
        child.text = _stringify(value)


def serialize_xml(records: Iterable[JsonDict]) -> str:
    root = ET.Element("resources")
    for r in records:
        tag = r.get("resourceType") if isinstance(r.get("resourceType"), str) else "resource"
        node = ET.SubElement(root, tag)
        for k, v in r.items():
            _append_value(node, k, v)

    xml_bytes = ET.tostring(root, encoding="utf-8")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + xml_bytes.decode("utf-8")


def write_xml(records: Iterable[JsonDict], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(serialize_xml(records), encoding="utf-8")
    return out_path



def plan_xml_exports(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Tuple[Path, str]]:
    """
    Plan XML exports without writing files.

    Returns:
      bucket -> (relative_path, xml_text)
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
            if not fname.endswith(".xml"):
                fname = f"{fname}.xml"
            rel_path = Path(fname)
        else:
            rel_path = Path(default_base) / f"{default_base}_{timestamp_utc}.xml"
        outputs[bucket] = (rel_path, serialize_xml(records))

    return outputs


def plan_xml_paths(
    store_resources: Dict[str, List[JsonDict]],
    *,
    filename_map: Dict[str, str] | None = None,
    timestamp_utc: str,
    run_id: str,
) -> Dict[str, Path]:
    """
    Plan XML export paths without serialization.

    Returns:
      bucket -> relative_path
    """
    return plan_export_paths(
        store_resources,
        filename_map=filename_map,
        timestamp_utc=timestamp_utc,
        run_id=run_id,
        extension=".xml",
    )
