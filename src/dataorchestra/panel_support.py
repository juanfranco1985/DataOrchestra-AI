from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


EXPECTED_UPLOADS = ("ventas.csv", "productos.csv", "stock.csv")


def list_client_dirs(clients_root: str | Path) -> list[Path]:
    root = Path(clients_root)
    if not root.exists():
        return []
    return sorted(
        [path for path in root.iterdir() if path.is_dir() and (path / "client.yaml").exists()],
        key=lambda item: item.name.lower(),
    )


def client_label(client_dir: str | Path) -> str:
    path = Path(client_dir)
    config = read_client_config(path)
    display_name = str(config.get("client", {}).get("display_name") or path.name)
    client_id = str(config.get("client", {}).get("id") or path.name)
    return f"{display_name} ({client_id})"


def read_client_config(client_dir: str | Path) -> dict[str, Any]:
    path = Path(client_dir) / "client.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def raw_file_table(client_dir: str | Path) -> list[dict[str, Any]]:
    raw_dir = Path(client_dir) / "raw"
    rows = []
    for name in EXPECTED_UPLOADS:
        path = raw_dir / name
        rows.append(
            {
                "archivo": name,
                "estado": "presente" if path.exists() else "faltante",
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    return rows


def read_text_preview(path: str | Path, max_chars: int = 6000) -> str:
    target = Path(path)
    if not target.exists():
        return ""
    text = target.read_text(encoding="utf-8")
    return text[:max_chars]
