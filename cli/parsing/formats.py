from __future__ import annotations

from typing import Tuple


ALLOWED_FORMATS = {"json", "ndjson", "csv", "xml", "turtle", "none"}


def parse_formats(raw: str) -> Tuple[str, ...]:
    if not raw:
        return ("json",)
    parts = [p.strip().lower() for p in raw.split(",") if p.strip()]
    invalid = [p for p in parts if p not in ALLOWED_FORMATS]
    if invalid:
        raise ValueError(f"Unsupported formats: {invalid}. Allowed: {sorted(ALLOWED_FORMATS)}")
    if "none" in parts and len(parts) > 1:
        raise ValueError("Format 'none' must be used alone.")
    return tuple(parts)
