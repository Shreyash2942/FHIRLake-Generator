from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from .base import RunPaths, StorageBackend


class LocalStorage(StorageBackend):
    """
    Local filesystem storage backend.

    Default layout:
      <base_dir>/
        <run_id>/
          metadata/run_summary.json
          fhir_json/*.json
          fhir_ndjson/*.ndjson
    """

    def __init__(self, base_dir: str | Path = "output", versioned: bool = False):
        """
        base_dir: where all run folders live
        versioned: if True, adds timestamp suffix: <run_id>__<timestamp>
        """
        self.base_dir = Path(base_dir)
        self.versioned = versioned

    def prepare_run(self, run_id: str, timestamp_utc: str) -> RunPaths:
        self.base_dir.mkdir(parents=True, exist_ok=True)

        folder_name = f"{run_id}__{timestamp_utc}" if self.versioned else run_id
        run_root = self.base_dir / folder_name

        metadata_dir = run_root / "metadata"
        fhir_json_dir = run_root / "fhir_json"
        fhir_ndjson_dir = run_root / "fhir_ndjson"

        metadata_dir.mkdir(parents=True, exist_ok=True)
        fhir_json_dir.mkdir(parents=True, exist_ok=True)
        fhir_ndjson_dir.mkdir(parents=True, exist_ok=True)

        return RunPaths(
            run_root=run_root,
            metadata_dir=metadata_dir,
            fhir_json_dir=fhir_json_dir,
            fhir_ndjson_dir=fhir_ndjson_dir,
        )

    def write_run_summary(self, paths: RunPaths, summary: Dict) -> Path:
        out_path = paths.metadata_dir / "run_summary.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        return out_path
