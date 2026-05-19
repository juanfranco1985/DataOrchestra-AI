from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def run_stage_dir(client_dir: str | Path, run_id: str, stage: str) -> Path:
    target = Path(client_dir) / "runs" / run_id / stage
    target.mkdir(parents=True, exist_ok=True)
    return target


def archive_file(client_dir: str | Path, run_id: str, stage: str, source: str | Path) -> str:
    source_path = Path(source)
    target = run_stage_dir(client_dir, run_id, stage) / source_path.name
    shutil.copy2(source_path, target)
    return str(target)
