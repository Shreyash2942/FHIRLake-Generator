from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict


def make_engine_logger(log_path: Path) -> logging.Logger:
    """
    File logger: outputs/<run>/metadata/engine.log
    """
    logger = logging.getLogger(f"fhirlake.engine.{log_path.parent.as_posix()}")
    logger.setLevel(logging.INFO)

    # prevent duplicate handlers across repeated runs in same process
    for h in list(logger.handlers):
        if isinstance(h, logging.FileHandler):
            try:
                if Path(h.baseFilename) == log_path:
                    return logger
            except Exception:
                pass

    log_path.parent.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("[ENGINE] %(message)s"))
    logger.addHandler(fh)
    return logger


def log_plan(logger: logging.Logger, summary: Dict[str, Any]) -> None:
    plan = summary.get("plan", {}) if isinstance(summary, dict) else {}
    logger.info("Planning: build_plan()")
    logger.info(f"Selected: {plan.get('selected')}")
    logger.info(f"Expanded: {plan.get('expanded')}")
    logger.info(f"Order: {plan.get('order')}")
    logger.info(f"Expected counts: {plan.get('counts')}")
