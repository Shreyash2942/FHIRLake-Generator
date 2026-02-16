from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional

from cli.parsing.config import CliConfig
from cli.commands.interactive import run_interactive


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="FHIRLake Generator CLI (interactive)"
    )
    parser.add_argument(
        "--datasets-root",
        default=None,
        help="Path to Datasets root (default: project/Datasets).",
    )
    parser.add_argument(
        "--output",
        default="output",
        help="Output directory (default: output).",
    )
    parser.add_argument(
        "--cli-config",
        default=None,
        help="Path to CLI config JSON (default: cli/config/cli.config.json).",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    project_root = Path(__file__).resolve().parents[2]
    datasets_root = Path(args.datasets_root) if args.datasets_root else project_root / "Datasets"
    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir

    config_path = (
        Path(args.cli_config)
        if args.cli_config
        else project_root / "cli" / "config" / "cli.config.json"
    )
    cli_config = CliConfig.load(config_path)

    return run_interactive(datasets_root, output_dir, config=cli_config)
