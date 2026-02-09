from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class RunPaths:
    """
    Canonical output layout for a single generation run.
    """
    run_root: Path
    metadata_dir: Path
    fhir_json_dir: Path
    fhir_ndjson_dir: Path


class StorageBackend:
    """
    Storage backend interface. Local, fixed-location, S3, etc. implement this contract.
    """

    def prepare_run(self, run_id: str, timestamp_utc: str) -> RunPaths:  # pragma: no cover
        raise NotImplementedError

    def write_run_summary(self, paths: RunPaths, summary: Dict) -> Path:  # pragma: no cover
        raise NotImplementedError
