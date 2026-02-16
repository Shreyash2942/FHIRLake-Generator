# Storage/local/local_storage.py
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

from Storage.base import RunPaths, StorageBackend
from Exporter import serialize_csv, serialize_xml, serialize_turtle


def _json_default(o: Any):
    """
    Make common non-JSON types serializable.
    - datetime/date -> ISO8601 string
    - pydantic/fhir.resources objects -> model_dump()
    - fallback -> str(o)
    """
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if hasattr(o, "model_dump"):
        return o.model_dump(exclude_none=True)
    return str(o)


class LocalStorage(StorageBackend):
    """
    Local filesystem storage backend.

    Default layout (flat):
      <base_dir>/
        metadata/run_summary.json
        metadata/engine.log
        json/*.json
        ndjson/*.ndjson
        csv/*.csv
        xml/*.xml
        turtle/*.ttl

    Run-based layout (layout="run"):
      <base_dir>/
        <run_id>__<timestamp>/
          metadata/run_summary.json
          metadata/engine.log
          json/*.json
          ndjson/*.ndjson
          csv/*.csv
          xml/*.xml
          turtle/*.ttl
    """

    def __init__(
        self,
        base_dir: str | Path = "output",
        versioned: bool = False,
        layout: str = "flat",
    ):
        self.base_dir = Path(base_dir)
        self.versioned = versioned
        self.layout = layout

    def prepare_run(self, run_id: str, timestamp_utc: str) -> RunPaths:
        self.base_dir.mkdir(parents=True, exist_ok=True)

        if self.layout == "run":
            folder_name = f"{run_id}__{timestamp_utc}" if self.versioned else run_id
            run_root = self.base_dir / folder_name
        else:
            run_root = self.base_dir

        metadata_dir = run_root / "metadata"
        fhir_json_dir = run_root / "json"
        fhir_ndjson_dir = run_root / "ndjson"
        fhir_csv_dir = run_root / "csv"
        fhir_xml_dir = run_root / "xml"
        fhir_turtle_dir = run_root / "turtle"
        summary_dir = self.base_dir / "summary" / timestamp_utc
        log_dir = self.base_dir / "logs" / timestamp_utc

        metadata_dir.mkdir(parents=True, exist_ok=True)
        fhir_json_dir.mkdir(parents=True, exist_ok=True)
        fhir_ndjson_dir.mkdir(parents=True, exist_ok=True)
        fhir_csv_dir.mkdir(parents=True, exist_ok=True)
        fhir_xml_dir.mkdir(parents=True, exist_ok=True)
        fhir_turtle_dir.mkdir(parents=True, exist_ok=True)
        summary_dir.mkdir(parents=True, exist_ok=True)
        log_dir.mkdir(parents=True, exist_ok=True)

        return RunPaths(
            run_root=run_root,
            metadata_dir=metadata_dir,
            fhir_json_dir=fhir_json_dir,
            fhir_ndjson_dir=fhir_ndjson_dir,
            fhir_csv_dir=fhir_csv_dir,
            fhir_xml_dir=fhir_xml_dir,
            fhir_turtle_dir=fhir_turtle_dir,
            summary_dir=summary_dir,
            log_dir=log_dir,
        )

    def write_text(self, path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(content)
        return path

    def write_bytes(self, path: Path, content: bytes) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            f.write(content)
        return path

    def write_json(self, path: Path, data: Any, indent: int = 2) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent, default=_json_default)
        return path

    def write_ndjson(self, path: Path, records: List[Dict[str, Any]]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False, default=_json_default))
                f.write("\n")
        return path

    def write_csv(self, path: Path, records: List[Dict[str, Any]]) -> Path:
        return self.write_text(path, serialize_csv(records))

    def write_xml(self, path: Path, records: List[Dict[str, Any]]) -> Path:
        return self.write_text(path, serialize_xml(records))

    def write_turtle(self, path: Path, records: List[Dict[str, Any]]) -> Path:
        return self.write_text(path, serialize_turtle(records))

    def write_run_summary(self, paths: RunPaths, summary: Dict[str, Any]) -> Path:
        timestamp = str(summary.get("timestamp_utc", "")).strip()
        run_id = str(summary.get("run_id", "")).strip()
        suffix = f"_{timestamp}" if timestamp else ""
        if run_id:
            suffix = f"{suffix}_{run_id[:8]}"
        out_path = paths.summary_dir / f"run_summary{suffix}.json"
        return self.write_json(out_path, summary, indent=2)
