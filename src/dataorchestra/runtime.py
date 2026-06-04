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
DELIVERY_METHODS = {"email", "meeting", "other", "printed", "whatsapp"}
RETENTION_ACTIONS = {
    "approved_report_retained",
    "derived_deleted",
    "not_applicable",
    "raw_deleted",
    "retained_by_agreement",
}


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


def mark_delivered(
    client_dir: str | Path,
    recipient: str,
    method: str,
    notes: str,
    confirm_delivery: bool = False,
) -> dict[str, Any]:
    client_path = Path(client_dir)
    recipient = recipient.strip()
    method = method.strip()
    notes = notes.strip()
    delivery_dir = client_path / "diagnostics" / "delivery"
    delivery_dir.mkdir(parents=True, exist_ok=True)

    blocker = _delivery_blocker(client_path, recipient, method, notes, confirm_delivery)
    if blocker:
        _write_json(delivery_dir / "delivery_blocked.json", blocker)
        return blocker

    config_path = client_path / "client.yaml"
    config = _read_yaml(config_path)
    client_id = str(config.get("client", {}).get("id") or client_path.name)
    approval_path = client_path / "diagnostics" / "review" / "approval_record.json"
    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    delivered_at = now_iso()
    record = {
        "client_id": client_id,
        "status": DiagnosticStatus.DELIVERED.value,
        "run_id": approval.get("run_id"),
        "recipient": recipient,
        "method": method,
        "notes": notes,
        "delivered_at": delivered_at,
        "approved_report_only_confirmed": True,
    }

    config.setdefault("client", {})["status"] = DiagnosticStatus.DELIVERED.value
    config.setdefault("pilot", {})["delivered_at"] = delivered_at
    config["pilot"]["delivery_method"] = method
    config["pilot"]["delivery_allowed"] = False
    config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")

    record_path = delivery_dir / "delivery_record.json"
    _write_json(record_path, record)
    return {
        "client_id": client_id,
        "status": DiagnosticStatus.DELIVERED.value,
        "run_id": approval.get("run_id"),
        "delivery_record": str(record_path),
        "next_action": "Cerrar piloto con close-pilot y registrar retencion o borrado de datos.",
    }


def record_retention_action(
    client_dir: str | Path,
    responsible: str,
    action: str,
    notes: str,
    confirm_retention_review: bool = False,
) -> dict[str, Any]:
    client_path = Path(client_dir)
    responsible = responsible.strip()
    action = action.strip()
    notes = notes.strip()
    closure_dir = client_path / "diagnostics" / "closure"
    closure_dir.mkdir(parents=True, exist_ok=True)

    blocker = _retention_blocker(client_path, responsible, action, notes, confirm_retention_review)
    if blocker:
        _write_json(closure_dir / "retention_blocked.json", blocker)
        return blocker

    config_path = client_path / "client.yaml"
    config = _read_yaml(config_path)
    client_id = str(config.get("client", {}).get("id") or client_path.name)
    reviewed_at = now_iso()
    record = {
        "client_id": client_id,
        "status": "retention_recorded",
        "responsible": responsible,
        "action": action,
        "notes": notes,
        "reviewed_at": reviewed_at,
        "manual_action_confirmed": True,
    }

    record_path = closure_dir / "retention_record.json"
    _write_json(record_path, record)

    closure_path = closure_dir / "closure_record.json"
    if closure_path.exists():
        closure = json.loads(closure_path.read_text(encoding="utf-8"))
        closure["data_retention_action_required"] = False
        closure["retention_record"] = str(record_path)
        closure["retention_action"] = action
        closure["retention_reviewed_at"] = reviewed_at
        _write_json(closure_path, closure)

    config.setdefault("pilot", {})["retention_action"] = action
    config["pilot"]["retention_reviewed_at"] = reviewed_at
    config_path.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False), encoding="utf-8")

    return {
        "client_id": client_id,
        "status": "retention_recorded",
        "retention_record": str(record_path),
        "data_retention_action_required": False,
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


def _delivery_blocker(client_path: Path, recipient: str, method: str, notes: str, confirm_delivery: bool) -> dict[str, Any] | None:
    if not confirm_delivery:
        return _blocked("delivery_confirmation_required", "Use explicit delivery confirmation before marking a report delivered.")
    if not recipient:
        return _blocked("recipient_required", "Recipient is required.")
    if method not in DELIVERY_METHODS:
        return _blocked("invalid_delivery_method", f"Method must be one of: {', '.join(sorted(DELIVERY_METHODS))}.")
    if not notes:
        return _blocked("delivery_notes_required", "Delivery notes are required.")

    approval_path = client_path / "diagnostics" / "review" / "approval_record.json"
    approved_report_path = client_path / "reports" / "diagnostico_aprobado.json"
    if not approval_path.exists() or not approved_report_path.exists():
        return _blocked("approval_required", "Approved report and approval record are required before delivery.")

    approval = json.loads(approval_path.read_text(encoding="utf-8"))
    if approval.get("status") != DiagnosticStatus.APPROVED_FOR_DELIVERY.value or approval.get("human_review_confirmed") is not True:
        return _blocked("approval_not_confirmed", "Approval record must include confirmed human review.")
    return None


def _retention_blocker(
    client_path: Path,
    responsible: str,
    action: str,
    notes: str,
    confirm_retention_review: bool,
) -> dict[str, Any] | None:
    if not confirm_retention_review:
        return _blocked("retention_review_confirmation_required", "Use explicit retention review confirmation.")
    if not responsible:
        return _blocked("responsible_required", "Responsible person is required.")
    if action not in RETENTION_ACTIONS:
        return _blocked("invalid_retention_action", f"Action must be one of: {', '.join(sorted(RETENTION_ACTIONS))}.")
    if not notes:
        return _blocked("retention_notes_required", "Retention notes are required.")
    if not (client_path / "client.yaml").exists():
        return _blocked("client_config_missing", "client.yaml is required to record retention.")
    closure_path = client_path / "diagnostics" / "closure" / "closure_record.json"
    if not closure_path.exists():
        return _blocked("closure_required", "Pilot closure record is required before retention review.")
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    if closure.get("status") != DiagnosticStatus.PILOT_CLOSED.value:
        return _blocked("closure_not_confirmed", "Pilot must be closed before retention review.")
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
