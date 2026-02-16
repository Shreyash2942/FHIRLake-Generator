from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Iterable, Set, Tuple

from .engine import run_engine
from .engine_models import ExportOptions
from core.orchestrator import EngineConfig
from core.planning import UserRequest
from Storage import LocalStorage, DockerStorage


def _parse_resource_args(values: Iterable[str], default_count: int) -> Tuple[Set[str], Dict[str, int]]:
    selected: Set[str] = set()
    counts: Dict[str, int] = {}

    for raw in values:
        raw = raw.strip()
        if not raw:
            continue
        if "=" in raw:
            name, count_raw = raw.split("=", 1)
            name = name.strip()
            count_raw = count_raw.strip()
            if not name:
                raise ValueError(f"Invalid resource spec: '{raw}'")
            try:
                count = int(count_raw)
            except ValueError as exc:
                raise ValueError(f"Invalid count for resource '{name}': '{count_raw}'") from exc
        else:
            name = raw
            count = default_count

        if count < 1:
            raise ValueError(f"Count must be >= 1 for resource '{name}'")
        selected.add(name)
        counts[name] = count

    if not selected:
        raise ValueError("At least one --resource is required.")

    return selected, counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the FHIRLake core engine.")
    parser.add_argument(
        "--resource",
        action="append",
        required=True,
        help="Resource type (repeatable). Use 'Type=COUNT' to set count.",
    )
    parser.add_argument(
        "--default-count",
        type=int,
        default=1,
        help="Default count when a resource omits '=COUNT'.",
    )
    parser.add_argument(
        "--datasets-root",
        default="Datasets",
        help="Path to datasets root.",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory.",
    )
    parser.add_argument(
        "--storage",
        default="local",
        choices=["local", "docker"],
        help="Storage backend to use.",
    )
    parser.add_argument(
        "--docker-container",
        default=None,
        help="Docker container name or ID (required for --storage docker).",
    )
    parser.add_argument(
        "--docker-path",
        default="/output",
        help="Base path inside container (used for --storage docker).",
    )
    parser.add_argument(
        "--docker-tmp",
        default=None,
        help="Local temp dir for staging files before docker cp.",
    )
    parser.add_argument(
        "--docker-skip-validate",
        action="store_true",
        help="Skip Docker container existence/running check.",
    )
    parser.add_argument(
        "--format",
        action="append",
        default=["json"],
        help="Export format (repeatable). Options: json, ndjson, csv, xml, turtle, none.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed (omit for random).",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="Disable strict validation in the planner.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    selected, counts = _parse_resource_args(args.resource, args.default_count)

    req = UserRequest(
        selected=selected,
        counts=counts,
        seed=args.seed,
        strict=not args.no_strict,
    )

    datasets_root = Path(args.datasets_root)
    output_dir = Path(args.output)

    if args.storage == "docker":
        if not args.docker_container:
            raise ValueError("--docker-container is required when --storage docker is selected.")
        storage = DockerStorage(
            container_name=args.docker_container,
            container_base_dir=args.docker_path,
            local_tmp_dir=args.docker_tmp,
            versioned=False,
            layout="flat",
            validate_container=not args.docker_skip_validate,
            create_metadata_dir=False,
            create_summary_dir=False,
            create_log_dir=False,
        )
    else:
        storage = LocalStorage(base_dir=output_dir, versioned=False, layout="flat")
    export = ExportOptions(formats=tuple(args.format), json_indent=2)
    engine_config = EngineConfig(
        output_dir=str(output_dir),
        write_manifest=False,
        write_engine_log=False,
    )

    result = run_engine(
        req,
        datasets_root=datasets_root,
        storage=storage,
        export=export,
        orchestrator_config=engine_config,
    )

    print("Run complete.")
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


if __name__ == "__main__":
    raise SystemExit(main())
