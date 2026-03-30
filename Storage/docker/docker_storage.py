from __future__ import annotations

import json
import os
import subprocess
import tempfile
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List

from Storage.base import RunPaths, StorageBackend
from Exporter import serialize_csv, serialize_xml, serialize_turtle


def _json_default(o: Any):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if hasattr(o, "model_dump"):
        return o.model_dump(exclude_none=True)
    return str(o)


class DockerStorage(StorageBackend):
    """
    Storage backend that writes outputs into a Docker container.

    This uses the docker CLI to create directories and copy files.
    """

    def __init__(
        self,
        *,
        container_name: str,
        container_base_dir: str | PurePosixPath = "/output",
        local_tmp_dir: str | Path | None = None,
        versioned: bool = False,
        layout: str = "flat",
        validate_container: bool = True,
        create_metadata_dir: bool = False,
        create_summary_dir: bool = False,
        create_log_dir: bool = False,
    ):
        self.container_name = container_name
        self.container_base_dir = PurePosixPath(str(container_base_dir))
        self.local_tmp_dir = Path(local_tmp_dir) if local_tmp_dir else None
        self.versioned = versioned
        self.layout = layout
        self.create_metadata_dir = create_metadata_dir
        self.create_summary_dir = create_summary_dir
        self.create_log_dir = create_log_dir
        if validate_container:
            self._validate_container()

    def _docker_exec(self, args: List[str]) -> None:
        cmd = ["docker", "exec", self.container_name] + args
        subprocess.run(cmd, check=True)

    def _docker_cp(self, src: Path, dest: PurePosixPath) -> None:
        dest_str = f"{self.container_name}:{dest.as_posix()}"
        subprocess.run(["docker", "cp", str(src), dest_str], check=True)

    def _ensure_dir(self, path: PurePosixPath) -> None:
        self._docker_exec(["mkdir", "-p", path.as_posix()])

    def _validate_container(self) -> None:
        cmd = ["docker", "inspect", "-f", "{{.State.Running}}", self.container_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            msg = result.stderr.strip() or result.stdout.strip()
            raise ValueError(f"Docker container '{self.container_name}' not found. {msg}")
        running = result.stdout.strip().lower()
        if running != "true":
            raise RuntimeError(f"Docker container '{self.container_name}' is not running.")

    def prepare_run(
        self,
        run_id: str,
        timestamp_utc: str,
        formats: tuple[str, ...] | None = None,
    ) -> RunPaths:
        if self.layout == "run":
            folder_name = f"{run_id}__{timestamp_utc}" if self.versioned else run_id
            run_root = self.container_base_dir / folder_name
        else:
            run_root = self.container_base_dir

        metadata_dir = run_root / "metadata"
        fhir_json_dir = run_root / "json"
        fhir_ndjson_dir = run_root / "ndjson"
        fhir_csv_dir = run_root / "csv"
        fhir_xml_dir = run_root / "xml"
        fhir_turtle_dir = run_root / "turtle"
        summary_dir = self.container_base_dir / "summary" / timestamp_utc
        log_dir = self.container_base_dir / "logs" / timestamp_utc

        selected = None
        if formats is not None:
            selected = {f.lower().strip() for f in formats if str(f).strip()}
            if "none" in selected:
                selected = set()

        if selected is None or "json" in selected:
            self._ensure_dir(fhir_json_dir)
        if selected is None or "ndjson" in selected:
            self._ensure_dir(fhir_ndjson_dir)
        if selected is None or "csv" in selected:
            self._ensure_dir(fhir_csv_dir)
        if selected is None or "xml" in selected:
            self._ensure_dir(fhir_xml_dir)
        if selected is None or "turtle" in selected or "ttl" in selected:
            self._ensure_dir(fhir_turtle_dir)
        if self.create_metadata_dir:
            self._ensure_dir(metadata_dir)
        if self.create_summary_dir:
            self._ensure_dir(summary_dir)
        if self.create_log_dir:
            self._ensure_dir(log_dir)

        return RunPaths(
            run_root=Path(run_root.as_posix()),
            metadata_dir=Path(metadata_dir.as_posix()),
            fhir_json_dir=Path(fhir_json_dir.as_posix()),
            fhir_ndjson_dir=Path(fhir_ndjson_dir.as_posix()),
            fhir_csv_dir=Path(fhir_csv_dir.as_posix()),
            fhir_xml_dir=Path(fhir_xml_dir.as_posix()),
            fhir_turtle_dir=Path(fhir_turtle_dir.as_posix()),
            summary_dir=Path(summary_dir.as_posix()),
            log_dir=Path(log_dir.as_posix()),
        )

    def _write_temp(self, content: bytes) -> Path:
        if self.local_tmp_dir:
            self.local_tmp_dir.mkdir(parents=True, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(dir=str(self.local_tmp_dir))
        else:
            fd, tmp_path = tempfile.mkstemp()
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        return Path(tmp_path)

    def write_text(self, path: Path, content: str) -> Path:
        tmp = self._write_temp(content.encode("utf-8"))
        try:
            self._ensure_dir(PurePosixPath(path.parent.as_posix()))
            self._docker_cp(tmp, PurePosixPath(path.as_posix()))
        finally:
            tmp.unlink(missing_ok=True)
        return path

    def write_bytes(self, path: Path, content: bytes) -> Path:
        tmp = self._write_temp(content)
        try:
            self._ensure_dir(PurePosixPath(path.parent.as_posix()))
            self._docker_cp(tmp, PurePosixPath(path.as_posix()))
        finally:
            tmp.unlink(missing_ok=True)
        return path

    def write_json(self, path: Path, data: Any, indent: int = 2) -> Path:
        payload = json.dumps(data, ensure_ascii=False, indent=indent, default=_json_default)
        return self.write_text(path, payload)

    def write_ndjson(self, path: Path, records: List[Dict[str, Any]]) -> Path:
        lines = []
        for r in records:
            lines.append(json.dumps(r, ensure_ascii=False, default=_json_default))
        payload = "\n".join(lines) + ("\n" if lines else "")
        return self.write_text(path, payload)

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
        out_path = Path(paths.summary_dir) / f"run_summary{suffix}.json"
        return self.write_json(out_path, summary, indent=2)
