from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.planning import build_plan, UserRequest
from core.runtime import RunContext, ResourceStore, write_manifest, build_manifest
from core.resolver import Resolver
from core.resolver.exceptions import AutoCreateDependencyError


# -------------------------------------------------
# Engine configuration
# -------------------------------------------------

@dataclass(frozen=True, slots=True)
class EngineConfig:
    """
    Configuration for the Core engine.
    """
    output_dir: str = "outputs"
    locale: str = "en_US"
    manifest_filename: str = "run_summary.json"
    console_mode: str = "summary"  # "summary", "verbose", "quiet"
    log_filename: str = "engine.log"  # human-readable run log
    write_manifest: bool = True
    write_engine_log: bool = True
    include_log_lines: bool = True


# -------------------------------------------------
# Simple status logger (print now, file later)
# -------------------------------------------------

class _RunLogger:
    def __init__(self, *, echo: bool = True) -> None:
        self.lines: List[str] = []
        self.echo = echo

    def info(self, msg: str) -> None:
        line = f"[ENGINE] {msg}"
        if self.echo:
            print(line)
        self.lines.append(line)

    def kv(self, key: str, value: Any) -> None:
        self.info(f"{key}: {value}")

    def write_to(self, path: Path) -> None:
        path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


# -------------------------------------------------
# Registry helpers (dict OR registry object)
# -------------------------------------------------

def _reg_get(registry: Any, resource_type: str) -> Any:
    if hasattr(registry, "get") and not isinstance(registry, dict):
        return registry.get(resource_type)
    return registry[resource_type]


# -------------------------------------------------
# Generator loading
# -------------------------------------------------

def _load_callable_from_string(path: str) -> Any:
    """
    Load a python object from an import string.

    Supported:
    - package.module:callable_or_class
    - package.module.callable_or_class
    """
    if ":" in path:
        module_name, attr = path.split(":", 1)
    else:
        parts = path.split(".")
        if len(parts) < 2:
            raise ImportError(f"Invalid import string: {path}")
        module_name, attr = ".".join(parts[:-1]), parts[-1]

    module = importlib.import_module(module_name)
    if not hasattr(module, attr):
        raise ImportError(f"'{module_name}' has no attribute '{attr}'")
    return getattr(module, attr)


def _load_generator(spec: Any) -> Any:
    gen_path = getattr(spec, "generator", None)
    if not gen_path:
        raise ValueError(f"Spec missing 'generator': {spec}")
    return _load_callable_from_string(gen_path)


def _call_generate(
    generator: Any,
    *,
    ctx: RunContext,
    store: ResourceStore,
    inputs: Dict[str, Any],
    count: int,
) -> List[Dict[str, Any]]:
    """
     Future-proof generator invocation.

    Supported generator shapes:
      A) function: generate(ctx, store, inputs, count) -> iterable[dict]
      B) class:    Gen() then Gen.generate(ctx, store, inputs, count)
      C) instance: gen.generate(ctx, store, inputs, count)
      D) factory:  make() -> instance with .generate(...)
      E) module-like object exposing .generate

    Returns list[dict] (FHIR JSON resources).
    """

    # C/E) instance or module-like with .generate
    if hasattr(generator, "generate") and callable(getattr(generator, "generate")):
        return list(generator.generate(ctx, store, inputs, count))

    # A/B/D) callable: try as function first
    if callable(generator):
        try:
            return list(generator(ctx, store, inputs, count))
        except TypeError:
            # might be class or factory; try instantiate below
            pass

        # try instantiate (class or factory)
        try:
            instance = generator()
        except TypeError as e:
            raise TypeError(
                f"Generator is callable but could not be invoked as function OR instantiated.\n"
                f"type={type(generator)} value={generator}\n"
                f"original_error={e}"
            ) from e

        # instance with .generate
        if hasattr(instance, "generate") and callable(getattr(instance, "generate")):
            return list(instance.generate(ctx, store, inputs, count))

        raise TypeError(
            f"Instantiated generator but instance has no .generate(...).\n"
            f"instance_type={type(instance)} instance={instance}"
        )

    raise TypeError(
        f"Unsupported generator type.\n"
        f"type={type(generator)} value={generator}\n"
        "Expected: function generate(ctx,store,inputs,count) OR class/factory returning object with .generate OR instance with .generate."
    )


# -------------------------------------------------
# Orchestrator entrypoint
# -------------------------------------------------

def run_job(
    req: UserRequest,
    registry: Any,
    config: Optional[EngineConfig] = None,
) -> Tuple[ResourceStore, Dict[str, Any]]:
    """
    Execute a full dataset generation run.

    Returns:
        store: ResourceStore
        summary: dict
    """
    config = config or EngineConfig()
    console_mode = (config.console_mode or "summary").strip().lower()
    if console_mode not in {"summary", "verbose", "quiet"}:
        console_mode = "summary"
    log = _RunLogger(echo=(console_mode == "verbose"))

    # 1 Planning
    log.info("Planning: build_plan()")
    plan = build_plan(req, registry)
    log.kv("Selected", sorted(plan.selected))
    log.kv("Expanded", sorted(plan.expanded))
    log.kv("Order", list(plan.order))
    log.kv("Expected counts", dict(plan.counts))
    for rt in plan.order:
        spec = _reg_get(registry, rt)
        deps = list(getattr(spec, "dependencies", None) or [])
        inputs = list(getattr(spec, "required_inputs", None) or [])
        count = int(plan.counts.get(rt, 0))
        log.info(f"Plan item: {rt} count={count} deps={deps} inputs={inputs}")

    if console_mode == "summary":
        selected = sorted(plan.selected)
        expanded = sorted(plan.expanded)
        deps_only = [rt for rt in expanded if rt not in plan.selected]
        print("[ENGINE] Plan summary")
        print(f"[ENGINE] Selected: {selected}")
        print(f"[ENGINE] Dependencies: {deps_only}")
        print(f"[ENGINE] Order: {list(plan.order)}")
        print(f"[ENGINE] Counts: {dict(plan.counts)}")
        for rt in plan.order:
            spec = _reg_get(registry, rt)
            deps = list(getattr(spec, "dependencies", None) or [])
            inputs = list(getattr(spec, "required_inputs", None) or [])
            count = int(plan.counts.get(rt, 0))
            print(
                f"[ENGINE] Resource: {rt} count={count} deps={deps} inputs={inputs}"
            )

    # 2 Runtime
    log.info("Runtime: create RunContext + ResourceStore")
    ctx = RunContext(seed=req.seed, locale=config.locale)
    store = ResourceStore()
    resolver = Resolver()

    log.kv("run_id", ctx.run_id)
    log.kv("timestamp_utc", ctx.timestamp_utc)
    log.kv("seed", ctx.seed)

    # 3 Execute plan
    for resource_type in plan.order:
        spec = _reg_get(registry, resource_type)
        count = int(plan.counts.get(resource_type, 0))

        log.info(f"Execute: {resource_type}")
        log.kv("count", count)
        log.kv("bucket", getattr(spec, "bucket", None))
        log.kv("generator", getattr(spec, "generator", None))

        if count <= 0:
            log.info(f"Skip: {resource_type} (count=0)")
            continue

        generator = _load_generator(spec)
        log.kv("loaded_generator_type", str(type(generator)))

        try:
            resolved = resolver.resolve(resource_type, spec, ctx, store, registry)
            log.info(f"Resolver: resolved inputs for {resource_type}")
            log.kv("inputs", resolved.values)
            log.kv("parent_refs", resolved.parent_refs)
        except AutoCreateDependencyError as e:
            raise RuntimeError(
                f"Resolver requires '{e.resource_type}' but pool is empty.\n"
                f"Fix: Ensure the dependency generator registers IDs using store.register_id(resourceType, id)\n"
                f"Resource being generated: {resource_type}"
            ) from e

        resources = _call_generate(
            generator,
            ctx=ctx,
            store=store,
            inputs=resolved.values,
            count=count,
        )

        log.info(f"Generator: produced {len(resources)} resources for {resource_type}")

        # Store + index
        store.add_many_from_spec(spec, resources)
        log.info(f"Store: added resources to bucket '{getattr(spec, 'bucket', None)}'")

        registered, linked = store.register_generated_resources(
            default_resource_type=resource_type,
            resources=resources,
            parent_refs=resolved.parent_refs,
        )
        log.kv("ids_registered", registered)
        log.kv("links_registered", linked)
        log.kv("bucket_counts_now", store.counts_by_bucket())

    # 4 Manifest + Engine Log
    manifest_data = build_manifest(
        ctx=ctx,
        plan=plan,
        store=store,
        registry=registry,
    )
    manifest_path: Optional[Path] = None
    if config.write_manifest:
        out_dir = Path(config.output_dir) / "summary" / ctx.timestamp_utc
        out_dir.mkdir(parents=True, exist_ok=True)
        log.info("Manifest: writing run summary")
        log.kv("output_dir", str(out_dir))
        manifest_path = write_manifest(
            out_dir,
            ctx=ctx,
            plan=plan,
            store=store,
            registry=registry,
            filename=f"run_summary_{ctx.timestamp_utc}_{ctx.run_id[:8]}.json",
        )
        log.kv("manifest_path", str(manifest_path))

    # write engine.log to output/log with timestamp
    engine_log_path: Optional[Path] = None
    if config.write_engine_log:
        try:
            log_dir = Path(config.output_dir) / "log"
            log_dir.mkdir(parents=True, exist_ok=True)
            engine_log_path = log_dir / f"orchestrator_{ctx.timestamp_utc}_{ctx.run_id[:8]}.log"
            log.write_to(engine_log_path)
            log.kv("engine_log", str(engine_log_path))
        except Exception as e:
            log.info(f"Could not write engine log file: {e}")

    summary = {
        "run_id": ctx.run_id,
        "created_at": ctx.created_at,
        "timestamp_utc": ctx.timestamp_utc,
        "seed": ctx.seed,
        "plan": {
            "selected": sorted(plan.selected),
            "expanded": sorted(plan.expanded),
            "order": list(plan.order),
            "counts": dict(plan.counts),
        },
        "actual_counts_by_bucket": store.counts_by_bucket(),
        "manifest": manifest_data,
        "manifest_path": str(manifest_path) if manifest_path else None,
        "engine_log_path": str(engine_log_path) if engine_log_path else None,
        "log_lines": list(log.lines) if config.include_log_lines else None,
    }

    return store, summary




