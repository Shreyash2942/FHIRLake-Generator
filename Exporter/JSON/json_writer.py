from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


JsonDict = Dict[str, Any]


def write_json_array(records: List[JsonDict], out_path: str | Path, indent: int = 2) -> Path:
    """
    Write resources as a JSON array.
    Best for human readability and quick inspection.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=indent)

    return out_path


def write_json_by_bucket(
    store_resources: Dict[str, List[JsonDict]],
    out_dir: str | Path,
    filename_map: Dict[str, str] | None = None,
    indent: int = 2,
) -> Dict[str, Path]:
    """
    Writes each ResourceStore bucket as JSON array files:
      - patients -> patients.json
      - encounters -> encounters.json
      - conditions -> conditions.json
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    filename_map = filename_map or {}
    outputs: Dict[str, Path] = {}

    for bucket, records in store_resources.items():
        fname = filename_map.get(bucket, f"{bucket}.json")
        path = out_dir / fname
        outputs[bucket] = write_json_array(records, path, indent=indent)

    return outputs
