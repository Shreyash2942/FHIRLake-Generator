from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def _reg_get(registry: Any, rt: str):
    if hasattr(registry, "get") and not isinstance(registry, dict):
        return registry.get(rt)
    return registry[rt]


def build_manifest(
    *,
    ctx: Any,
    plan: Any,
    store: Any,
    registry: Optional[Any] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    actual_by_bucket = (
        store.counts_by_bucket() if hasattr(store, "counts_by_bucket") else {}
    )

    expected_by_resource = dict(getattr(plan, "counts", {}) or {})

    expected_by_bucket: Dict[str, int] = {}
    if registry is not None:
        for rt, cnt in expected_by_resource.items():
            try:
                spec = _reg_get(registry, rt)
                bucket = getattr(spec, "bucket", rt)
            except Exception:
                bucket = rt
            expected_by_bucket[bucket] = expected_by_bucket.get(bucket, 0) + int(cnt)

    manifest = {
        "run_id": getattr(ctx, "run_id", None),
        "created_at": getattr(ctx, "created_at", None),
        "timestamp_utc": getattr(ctx, "timestamp_utc", None),
        "seed": getattr(ctx, "seed", None),
        "plan": {
            "selected": sorted(getattr(plan, "selected", [])),
            "expanded": sorted(getattr(plan, "expanded", [])),
            "order": list(getattr(plan, "order", [])),
        },
        "expected_counts_by_resource": expected_by_resource,
        "expected_counts_by_bucket": expected_by_bucket,
        "actual_counts_by_bucket": actual_by_bucket,
    }

    if extra:
        manifest.update(extra)

    return manifest


def write_manifest(
    output_dir: str | Path,
    *,
    ctx: Any,
    plan: Any,
    store: Any,
    registry: Optional[Any] = None,
    filename: str = "run_summary.json",
    extra: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Writes a stable run manifest for auditing and downstream pipelines.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / filename

    manifest = build_manifest(
        ctx=ctx,
        plan=plan,
        store=store,
        registry=registry,
        extra=extra,
    )

    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path
