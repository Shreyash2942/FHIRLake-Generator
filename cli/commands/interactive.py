from __future__ import annotations

from pathlib import Path
from typing import Dict, Set

from cli.parsing.config import CliConfig
from cli.services.deps import dependency_defaults, expand_dependencies
from cli.parsing.formats import parse_formats
from cli.output.prompts import prompt, prompt_int, prompt_yes_no, selection_prompt
from core.engine import run_engine, ExportOptions
from core.orchestrator import EngineConfig
from core.planning import UserRequest
from core.registry import get_resource_registry
from Storage import LocalStorage, DockerStorage


def run_interactive(
    datasets_root: Path,
    output_dir: Path,
    *,
    config: CliConfig | None = None,
) -> int:
    registry = get_resource_registry(str(datasets_root))
    config = config or CliConfig()
    resource_types = config.filter_resources(registry.keys())
    if not resource_types:
        print("No resource types found in registry.")
        return 1

    selected = selection_prompt(resource_types)
    expanded_required = expand_dependencies(selected, registry, include_optional=False)
    expanded_all = expand_dependencies(selected, registry, include_optional=True)
    optional_only = sorted(expanded_all - expanded_required)
    include_optional = False

    if optional_only:
        print("\nOptional dependency notice:")
        print(f"Optional datasets available for cross-linking: {optional_only}")
        include_optional = prompt_yes_no(
            "Include optional datasets to make references real?",
            default=False,
        )

    expanded = expanded_all if include_optional else expanded_required
    deps_only = sorted(expanded - selected)
    if deps_only:
        print("\nDependency notice:")
        print(f"Your selection requires additional datasets: {deps_only}")
        if not prompt_yes_no("Continue and set counts for dependencies?", default=True):
            return 1

    print("\nCounts for selected resources:")
    selected_counts: Dict[str, int] = {}
    for rt in sorted(selected):
        selected_counts[rt] = prompt_int(
            f"{rt} count",
            default=config.default_count,
            minimum=1,
        )

    dep_defaults = dependency_defaults(
        selected_counts,
        registry,
        include_optional=include_optional,
    )
    dep_counts: Dict[str, int] = {}
    if deps_only:
        print("\nCounts for required dependencies:")
    for rt in deps_only:
        default = dep_defaults.get(rt, config.default_count)
        dep_counts[rt] = prompt_int(f"{rt} count", default=default, minimum=1)

    counts: Dict[str, int] = {}
    counts.update(selected_counts)
    counts.update(dep_counts)

    seed_raw = prompt("\nSeed (blank for random)", "")
    seed = None
    if seed_raw:
        try:
            seed = int(seed_raw)
        except ValueError:
            print("Invalid seed. Using random seed.")
            seed = None

    while True:
        try:
            formats = parse_formats(
                prompt("Export formats (json, ndjson, csv, xml, turtle, none)", "json")
            )
            break
        except ValueError as e:
            print(e)

    storage_choice = prompt("Storage backend (local/docker)", "local").strip().lower()
    if storage_choice not in {"local", "docker"}:
        print("Unknown storage backend. Using local.")
        storage_choice = "local"

    if storage_choice == "local":
        use_default_output = prompt_yes_no(
            f"\nStore outputs in default location '{output_dir}'?",
            default=True,
        )
        if not use_default_output:
            custom = prompt("Enter output folder path")
            if custom:
                custom_path = Path(custom)
                output_dir = custom_path if custom_path.is_absolute() else output_dir.parent / custom_path
        storage = LocalStorage(base_dir=output_dir, versioned=False, layout="flat")
    else:
        container_name = prompt("Docker container name or ID")
        container_path = prompt("Container base path", "/output")
        docker_tmp = prompt("Local temp dir for docker cp (blank for default)", "")
        docker_tmp = docker_tmp if docker_tmp else None
        storage = DockerStorage(
            container_name=container_name,
            container_base_dir=container_path,
            local_tmp_dir=docker_tmp,
            versioned=False,
            layout="flat",
            create_metadata_dir=False,
            create_summary_dir=False,
            create_log_dir=False,
        )

    req = UserRequest(
        selected=selected,
        counts=counts,
        seed=seed,
        strict=True,
        include_optional=include_optional,
    )

    export = ExportOptions(formats=formats, json_indent=2)
    engine_config = EngineConfig(
        output_dir=str(output_dir),
        write_manifest=False,
        write_engine_log=False,
    )

    print("\nRunning engine...")
    result = run_engine(
        req,
        datasets_root=datasets_root,
        storage=storage,
        export=export,
        orchestrator_config=engine_config,
    )

    print("\nRun complete.")
    print(f"Run ID: {result.run_id}")
    print(f"Run root: {result.run_root}")
    print(f"Summary: {result.summary_path}")
    print(f"Engine log: {result.engine_log_path}")
    if result.export_paths:
        print("Exports:")
        for fmt, paths in result.export_paths.items():
            for bucket, path in paths.items():
                print(f"  {fmt} {bucket}: {path}")
    return 0
