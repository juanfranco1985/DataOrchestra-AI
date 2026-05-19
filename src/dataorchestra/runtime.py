from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import os

import yaml

from dataorchestra.audit import now_iso
from dataorchestra.states import DiagnosticStatus


RUNTIME_DIRS = ("clients", "intake", "exports", "archive", "logs", "policies", "deletion_requests")
OUTCOMES = {"completed", "not_viable", "needs_follow_up", "converted_to_service"}


def default_runtime_dir() -> Path:
    configured = os.environ.get("DATAORCHESTRA_RUNTIME_DIR")
    if configured:
        return Path(configured)
    return Path.home() / "DataOrchestra_Runtime"


def prepare_runtime(runtime_dir: str | Path | None = None) -> dict[str, Any]:
    root = Path(runtime_dir) if runtime_dir else default_runtime_dir()
    root.mkdir(parents=True, exist_ok=True)

    paths = {}
    for name in RUNTIME_DIRS:
        target = root / name
        target.mkdir(parents=True, exist_ok=True)
        paths[name] = str(target)

    readme = root / "README_RUNTIME.md"
    if not readme.exists():
        readme.write_text(_runtime_readme(), encoding="utf-8")

    gitignore = root / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n!.gitignore\n!README_RUNTIME.md\n!runtime_policy.yaml\n", encoding="utf-8")

    policy = root / "runtime_policy.yaml"
    if not policy.exists():
        policy.write_text(yaml.safe_dump(_runtime_policy(), allow_unicode=True, sort_keys=False), encoding="utf-8")

    return {
        "status": "runtime_ready",
        "runtime_dir": str(root),
        "paths": paths,
        "readme": str(readme),
        "policy": str(policy),
        "gitignore": str(gitignore),
        "recommended_clients_root": str(root / "clients"),
    }


def close_pilot(
    client_dir: str | Path,
    reviewer: str,
    notes: str,
    outcome: str,
    confirm_close: bool = False,
) -> dict[str, Any]:
    client_path = Path(client_dir)
    reviewer = reviewer.strip()
    notes = notes.strip()
    outcome = outcome.strip()
    closure_dir = client_path / "diagnostics" / "closure"
    closure_dir.mkdir(parents=True, exist_ok=True)

    blocker = _closure_blocker(client_path, reviewer, notes, outcome, confirm_close)
    if blocker:
        _write_json(closure_dir / "closure_blocked.json", blocker)
        return blocker

    config_path = client_path / "client.yaml"
    config = _read_yaml(config_path)
    client_id = str(config.get("client", {}).get("id") or client_path.name)
    closed_at = now_iso()
    record = {
        "client_id": client_id,
        "status": DiagnosticStatus.PILOT_CLOSED.value,
        "outcome": outcome,
        "reviewer": reviewer,
        "notes": notes,
        "closed_at": closed_at,
        "data_retention_action_required": True,
        "recommended_next_step": _recommended_next_step(outcome),
    }

    config.setdefault("client", {})["status"] = DiagnosticStatus.PILOT_CLOSED.value
    config.setdefault("pilot", {})["closed_at"] = closed_at
    config.setdefault("pilot", {})["closure_outcome"] = outcome
    config["pilot"]["delivery_allowed"] = False
    config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")
    record_path = closure_dir / "closure_record.json"
    _write_json(record_path, record)

    return {
        "client_id": client_id,
        "status": DiagnosticStatus.PILOT_CLOSED.value,
        "outcome": outcome,
        "closure_record": str(record_path),
        "data_retention_action_required": True,
        "recommended_next_step": record["recommended_next_step"],
    }


def _closure_blocker(client_path: Path, reviewer: str, notes: str, outcome: str, confirm_close: bool) -> dict[str, Any] | None:
    if not confirm_close:
        return _blocked("closure_confirmation_required", "Use explicit close confirmation before closing pilot.")
    if not reviewer:
        return _blocked("reviewer_required", "Reviewer name is required.")
    if not notes:
        return _blocked("closure_notes_required", "Closure notes are required.")
    if outcome not in OUTCOMES:
        return _blocked("invalid_outcome", f"Outcome must be one of: {', '.join(sorted(OUTCOMES))}.")
    if not (client_path / "client.yaml").exists():
        return _blocked("client_config_missing", "client.yaml is required to close a pilot.")
    return None


def _recommended_next_step(outcome: str) -> str:
    return {
        "completed": "Registrar feedback final y ejecutar politica de retencion o borrado de datos.",
        "not_viable": "Documentar causa de no viabilidad y ejecutar borrado segun politica.",
        "needs_follow_up": "Agendar seguimiento y mantener datos solo durante el plazo acordado.",
        "converted_to_service": "Crear nuevo alcance comercial y revisar contrato antes de continuar.",
    }[outcome]


def _runtime_readme() -> str:
    return """# DataOrchestra Runtime

Carpeta operativa local para datos reales de clientes.

No subir esta carpeta a GitHub.
No guardar aqui datos personales innecesarios.
Usar una subcarpeta por cliente dentro de `clients/`.
Aplicar politica de retencion y borrado al cerrar cada piloto.
"""


def _runtime_policy() -> dict[str, Any]:
    return {
        "purpose": "runtime local para pilotos controlados",
        "store_real_client_data": True,
        "git_tracking_allowed": False,
        "raw_files_mutable_after_preflight": False,
        "human_review_required": True,
        "retention_review_required_on_close": True,
        "accepted_files": ["ventas.csv", "productos.csv", "stock.csv"],
        "forbidden_data": [
            "datos personales innecesarios",
            "datos bancarios",
            "datos medicos",
            "datos legales sensibles",
            "datos fiscales personales",
        ],
    }


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _blocked(status: str, reason: str) -> dict[str, Any]:
    return {
        "status": status,
        "can_close": False,
        "reason": reason,
    }
