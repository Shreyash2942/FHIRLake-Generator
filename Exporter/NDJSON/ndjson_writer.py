from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


JsonDict = Dict[str, Any]


def write_ndjson(records: Iterable[JsonDict], out_path: str | Path) -> Path:
    """
    Write resources as NDJSON (one JSON object per line).
    Best for data lakes / streaming / Spark ingestion.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        for obj in records:
            f.write(json.dumps(obj, ensure_ascii=False))
            f.write("\n")

    return out_path


def write_ndjson_by_bucket(
    store_resources: Dict[str, List[JsonDict]],
    out_dir: str | Path,
    filename_map: Dict[str, str] | None = None,
) -> Dict[str, Path]:
    """
    Writes each ResourceStore bucket as NDJSON:
      - patients -> patients.ndjson
      - encounters -> encounters.ndjson
      - conditions -> conditions.ndjson
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename_map = filename_map or {}
    outputs: Dict[str, Path] = {}

    for bucket, records in store_resources.items():
        fname = filename_map.get(bucket, f"{bucket}.ndjson")
        path = out_dir / fname
        outputs[bucket] = write_ndjson(records, path)

    return outputs
