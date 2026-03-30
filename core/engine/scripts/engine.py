# core/engine/scripts/engine.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.planning import UserRequest
from core.orchestrator.run import run_job, EngineConfig as OrchestratorConfig
from .engine_models import ExportOptions, EngineResult
from .logging_utils import make_engine_logger, log_plan

from Storage import LocalStorage, StorageBackend, RunPaths
from Exporter import (
    plan_json_paths,
    plan_ndjson_paths,
    plan_csv_paths,
    plan_xml_paths,
    plan_turtle_paths,
)


# -------------------------------------------------
# Storage-driven exporting (Option B)
# -------------------------------------------------

# Export writing is delegated to StorageBackend to keep serialization centralized.


def _resolve_registry(registry: Optional[Any], datasets_root: str | Path) -> Any:
    if registry is not None:
        return registry
    from core.registry.registry import get_resource_registry
    return get_resource_registry(str(datasets_root))


def _resolve_storage(storage: Optional[StorageBackend]) -> StorageBackend:
    return storage or LocalStorage(base_dir="output", versioned=False, layout="flat")


def _resolve_export(export: Optional[ExportOptions]) -> ExportOptions:
    return export or ExportOptions(formats=("json",))


def _resolve_orchestrator_config(
    config: Optional[OrchestratorConfig],
    storage: StorageBackend,
) -> OrchestratorConfig:
    if config is not None:
        return config
    default_output = str(getattr(storage, "base_dir", "output"))
    return OrchestratorConfig(
        output_dir=default_output,
        write_manifest=False,
        write_engine_log=False,
    )


def _init_engine_logger(
    paths: RunPaths,
    *,
    run_id: str,
    timestamp_utc: str,
    summary: Dict[str, Any],
) -> tuple[logging.Logger, Path]:
    engine_log_path = paths.log_dir / "engine.log"
    logger = make_engine_logger(engine_log_path)

    logger.info(f"run_id: {run_id}")
    logger.info(f"timestamp_utc: {timestamp_utc}")
    logger.info(f"seed: {summary.get('seed')}")
    log_plan(logger, summary)
    return logger, engine_log_path


def _write_run_summary(
    *,
    summary: Dict[str, Any],
    storage: StorageBackend,
    paths: RunPaths,
    logger: logging.Logger,
) -> Path:
    manifest_path = summary.get("manifest_path")
    if manifest_path:
        summary_path = Path(str(manifest_path))
        logger.info(f"Run summary -> {summary_path}")
        return summary_path

    manifest = summary.get("manifest")
    if isinstance(manifest, dict):
        summary_path = storage.write_run_summary(paths, manifest)
        logger.info(f"Wrote run summary -> {summary_path}")
        return summary_path

    summary_path = storage.write_run_summary(paths, summary)
    logger.info(f"Wrote run summary -> {summary_path}")
    return summary_path


def _normalize_formats(formats: Tuple[str, ...]) -> Tuple[str, ...]:
    normalized = [f.lower().strip() for f in formats]
    # Preserve order while removing duplicates
    return tuple(dict.fromkeys(normalized))


def _export_resources(
    *,
    storage: StorageBackend,
    paths: RunPaths,
    export: ExportOptions,
    store_resources: Dict[str, List[Dict[str, Any]]],
    timestamp_utc: str,
    run_id: str,
    logger: logging.Logger,
) -> Dict[str, Dict[str, str]]:
    export_paths: Dict[str, Dict[str, str]] = {}

    formats = _normalize_formats(export.formats)
    if "none" in formats:
        logger.info("Export skipped (formats includes 'none').")
        return export_paths

    def _export_json() -> Dict[str, str]:
        out: Dict[str, str] = {}
        plans = plan_json_paths(
            store_resources,
            filename_map=export.filename_map,
            timestamp_utc=timestamp_utc,
            run_id=run_id,
        )
        for bucket, rel_path in plans.items():
            out_path = paths.dir_for_format("json") / rel_path
            storage.write_json(out_path, store_resources.get(bucket, []), indent=export.json_indent)
            out[bucket] = str(out_path)
            logger.info(f"Exported JSON bucket '{bucket}' -> {out_path}")
        return out

    def _export_ndjson() -> Dict[str, str]:
        out: Dict[str, str] = {}
        plans = plan_ndjson_paths(
            store_resources,
            filename_map=export.filename_map,
            timestamp_utc=timestamp_utc,
            run_id=run_id,
        )
        for bucket, rel_path in plans.items():
            out_path = paths.dir_for_format("ndjson") / rel_path
            storage.write_ndjson(out_path, store_resources.get(bucket, []))
            out[bucket] = str(out_path)
            logger.info(f"Exported NDJSON bucket '{bucket}' -> {out_path}")
        return out

    def _export_csv() -> Dict[str, str]:
        out: Dict[str, str] = {}
        plans = plan_csv_paths(
            store_resources,
            filename_map=export.filename_map,
            timestamp_utc=timestamp_utc,
            run_id=run_id,
        )
        for bucket, rel_path in plans.items():
            out_path = paths.dir_for_format("csv") / rel_path
            storage.write_csv(out_path, store_resources.get(bucket, []))
            out[bucket] = str(out_path)
            logger.info(f"Exported CSV bucket '{bucket}' -> {out_path}")
        return out

    def _export_xml() -> Dict[str, str]:
        out: Dict[str, str] = {}
        plans = plan_xml_paths(
            store_resources,
            filename_map=export.filename_map,
            timestamp_utc=timestamp_utc,
            run_id=run_id,
        )
        for bucket, rel_path in plans.items():
            out_path = paths.dir_for_format("xml") / rel_path
            storage.write_xml(out_path, store_resources.get(bucket, []))
            out[bucket] = str(out_path)
            logger.info(f"Exported XML bucket '{bucket}' -> {out_path}")
        return out

    def _export_turtle() -> Dict[str, str]:
        out: Dict[str, str] = {}
        plans = plan_turtle_paths(
            store_resources,
            filename_map=export.filename_map,
            timestamp_utc=timestamp_utc,
            run_id=run_id,
        )
        for bucket, rel_path in plans.items():
            out_path = paths.dir_for_format("turtle") / rel_path
            storage.write_turtle(out_path, store_resources.get(bucket, []))
            out[bucket] = str(out_path)
            logger.info(f"Exported Turtle bucket '{bucket}' -> {out_path}")
        return out

    exporters = {
        "json": _export_json,
        "ndjson": _export_ndjson,
        "csv": _export_csv,
        "xml": _export_xml,
        "turtle": _export_turtle,
        # Future formats (add later without changing engine flow):
        # "parquet": _export_parquet,
    }

    for fmt in formats:
        exporter = exporters.get(fmt)
        if exporter is None:
            logger.info(f"Skipping unsupported export format: {fmt}")
            continue
        export_paths[fmt] = exporter()

    return export_paths


def _get_store_resources(store: Any) -> Dict[str, List[Dict[str, Any]]]:
    store_resources = getattr(store, "resources", None)
    if not isinstance(store_resources, dict):
        raise TypeError("ResourceStore.resources must be dict[bucket -> list[resource_dict]].")
    return store_resources


# -------------------------------------------------
# Engine entrypoint
# -------------------------------------------------

def run_engine(
    req: UserRequest,
    *,
    registry: Optional[Any] = None,
    datasets_root: str | Path = "Datasets",
    storage: Optional[StorageBackend] = None,
    export: Optional[ExportOptions] = None,
    orchestrator_config: Optional[OrchestratorConfig] = None,
) -> EngineResult:
    """
    Single stable entrypoint for CLI/GUI.

    Flow:
      1) Load registry (if not provided)
      2) Run Core Orchestrator (plan + runtime + resolver + generators + manifest)
      3) Prepare canonical run folder via Storage
      4) Persist run_summary.json via Storage
      5) Export via Storage (json/ndjson)
      6) Return EngineResult

    Future-proof:
      - Engine never serializes datetimes directly
      - New formats = add storage.write_<format>() + one dispatch entry
      - New storage backend = implement StorageBackend methods
    """
    # 0) Resolve dependencies
    registry = _resolve_registry(registry, datasets_root)
    storage = _resolve_storage(storage)
    export = _resolve_export(export)
    orchestrator_config = _resolve_orchestrator_config(orchestrator_config, storage)

    # 1) Run core job
    store, summary = run_job(req, registry, orchestrator_config)

    run_id = str(summary.get("run_id"))
    timestamp_utc = str(summary.get("timestamp_utc"))

    # 2) Prepare storage run layout (exports)
    paths = storage.prepare_run(
        run_id=run_id,
        timestamp_utc=timestamp_utc,
        formats=_normalize_formats(export.formats),
    )

    # Logs and summary should stay local unless storage is already local.
    log_storage: StorageBackend
    if isinstance(storage, LocalStorage):
        log_storage = storage
        log_paths = paths
    else:
        log_storage = LocalStorage(base_dir="output", versioned=False, layout="flat")
        log_paths = log_storage.prepare_run(
            run_id=run_id,
            timestamp_utc=timestamp_utc,
            formats=_normalize_formats(export.formats),
        )

    # 3) Engine logger
    logger, engine_log_path = _init_engine_logger(
        log_paths,
        run_id=run_id,
        timestamp_utc=timestamp_utc,
        summary=summary,
    )

    # 4) Use orchestrator manifest summary (already written)
    summary_path = _write_run_summary(
        summary=summary,
        storage=log_storage,
        paths=log_paths,
        logger=logger,
    )

    # 5) Export formats (dispatch map)
    store_resources = _get_store_resources(store)
    export_paths = _export_resources(
        storage=storage,
        paths=paths,
        export=export,
        store_resources=store_resources,
        timestamp_utc=timestamp_utc,
        run_id=run_id,
        logger=logger,
    )

    logger.info("Engine complete")

    return EngineResult(
        run_id=run_id,
        timestamp_utc=timestamp_utc,
        run_root=str(paths.run_root),
        summary_path=str(summary_path),
        engine_log_path=str(engine_log_path),
        export_paths=export_paths,
        core_summary=summary,
    )
