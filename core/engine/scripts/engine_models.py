from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple


@dataclass(frozen=True, slots=True)
class ExportOptions:
    """
    Export configuration requested by CLI/GUI.

    formats:
      - "json"   : per-bucket JSON arrays (patients.json, encounters.json, ...)
      - "ndjson" : per-bucket line-delimited JSON (patients.ndjson, ...)
      - "csv"    : per-bucket CSV (flattened, top-level keys)
      - "xml"    : per-bucket XML
      - "turtle" : per-bucket Turtle (RDF-like)
      - "none"   : skip exporting resources (still writes run_summary + engine.log)
    """
    formats: Tuple[str, ...] = ("json",)
    json_indent: int = 2
    filename_map: Dict[str, str] = field(default_factory=dict)  # bucket -> filename override


@dataclass(frozen=True, slots=True)
class EngineResult:
    run_id: str
    timestamp_utc: str
    run_root: str
    summary_path: str
    engine_log_path: str
    export_paths: Dict[str, Dict[str, str]]
    core_summary: Dict[str, Any]
