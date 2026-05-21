from __future__ import annotations

from pathlib import Path
import re
from typing import Any

import yaml

from dataorchestra.states import DiagnosticStatus


CLIENT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
CLIENT_SUBDIRS = ("raw", "processed", "diagnostics", "reports", "logs", "runs")


def create_client_workspace(
    clients_root: str | Path,
    client_id: str,
    display_name: str | None = None,
    business_type: str = "Pendiente",
    currency: str = "ARS",
) -> dict[str, Any]:
    normalized_id = normalize_client_id(client_id)
    root = Path(clients_root)
    client_path = root / normalized_id

    if client_path.exists():
        return {
            "status": "client_already_exists",
            "can_continue": False,
            "client_id": normalized_id,
            "client_dir": str(client_path),
            "reason": "Client workspace already exists.",
        }

    for subdir in CLIENT_SUBDIRS:
        target = client_path / subdir
        target.mkdir(parents=True, exist_ok=True)
        (target / ".gitkeep").write_text("\n", encoding="utf-8")

    config = {
        "client": {
            "id": normalized_id,
            "display_name": display_name or normalized_id,
            "business_type": business_type,
            "status": DiagnosticStatus.INTAKE_PENDING.value,
            "currency": currency,
        },
        "privacy": {
            "anonymized": False,
            "authorization_received": False,
            "sensitive_data_checked": False,
        },
        "pilot": {
            "scope": "Diagnostico inicial controlado",
            "report_status": DiagnosticStatus.PENDING_HUMAN_REVIEW.value,
            "delivery_allowed": False,
        },
        "analytics": {
            "threshold_profile": "auto",
            "thresholds": {},
        },
        "data_quality": {
            "target_score": 70,
        },
    }
    config_path = client_path / "client.yaml"
    config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")

    return {
        "status": "client_workspace_created",
        "can_continue": True,
        "client_id": normalized_id,
        "client_dir": str(client_path),
        "config": str(config_path),
        "required_raw_files": ["ventas.csv", "productos.csv", "stock.csv"],
    }


def normalize_client_id(value: str) -> str:
    client_id = value.strip()
    if not client_id:
        raise ValueError("client_id is required.")
    if not CLIENT_ID_PATTERN.fullmatch(client_id):
        raise ValueError("client_id may only contain letters, numbers, hyphen and underscore.")
    return client_id
