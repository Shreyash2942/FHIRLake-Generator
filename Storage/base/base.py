# Storage/base/base.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class RunPaths:
    """
    Canonical output layout for a single generation run.
    """
    run_root: Path
    metadata_dir: Path
    fhir_json_dir: Path
    fhir_ndjson_dir: Path
    fhir_csv_dir: Path
    fhir_xml_dir: Path
    fhir_turtle_dir: Path
    summary_dir: Path
    log_dir: Path

    def dir_for_format(self, fmt: str) -> Path:
        key = (fmt or "").strip().lower()
        if key == "json":
            return self.fhir_json_dir
        if key == "ndjson":
            return self.fhir_ndjson_dir
        if key == "csv":
            return self.fhir_csv_dir
        if key == "xml":
            return self.fhir_xml_dir
        if key in {"turtle", "ttl"}:
            return self.fhir_turtle_dir
        raise ValueError(f"Unsupported format: {fmt}")


class StorageBackend:
    """
    Storage backend interface.

    Option-B contract:
      - Engine calls Storage for ALL persistence.
      - Storage handles serialization (datetime, date, pydantic models, etc.).
    """

    # ---------- Run lifecycle ----------

    def prepare_run(
        self,
        run_id: str,
        timestamp_utc: str,
        formats: tuple[str, ...] | None = None,
    ) -> RunPaths:  # pragma: no cover
        raise NotImplementedError

    def write_run_summary(self, paths: RunPaths, summary: Dict[str, Any]) -> Path:  # pragma: no cover
        raise NotImplementedError

    # ---------- Generic writes ----------

    def write_text(self, path: Path, content: str) -> Path:  # pragma: no cover
        raise NotImplementedError

    def write_bytes(self, path: Path, content: bytes) -> Path:  # pragma: no cover
        raise NotImplementedError

    # ---------- Format writes (serialization lives here) ----------

    def write_json(self, path: Path, data: Any, indent: int = 2) -> Path:  # pragma: no cover
        raise NotImplementedError

    def write_ndjson(self, path: Path, records: List[Dict[str, Any]]) -> Path:  # pragma: no cover
        raise NotImplementedError

    def write_csv(self, path: Path, records: List[Dict[str, Any]]) -> Path:  # pragma: no cover
        raise NotImplementedError

    def write_xml(self, path: Path, records: List[Dict[str, Any]]) -> Path:  # pragma: no cover
        raise NotImplementedError

    def write_turtle(self, path: Path, records: List[Dict[str, Any]]) -> Path:  # pragma: no cover
        raise NotImplementedError
