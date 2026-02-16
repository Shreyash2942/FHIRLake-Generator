from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class CliConfig:
    allowed_resources: Optional[List[str]] = None
    default_count: int = 10

    @classmethod
    def load(cls, path: Path) -> "CliConfig":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        allowed = data.get("allowed_resources")
        default_count = int(data.get("default_count", 10))
        if allowed is not None:
            allowed = [str(x) for x in allowed]
        return cls(allowed_resources=allowed, default_count=default_count)

    def filter_resources(self, resources: Iterable[str]) -> List[str]:
        if not self.allowed_resources:
            return sorted(resources)
        allowed = {r.lower() for r in self.allowed_resources}
        return sorted([r for r in resources if r.lower() in allowed])
