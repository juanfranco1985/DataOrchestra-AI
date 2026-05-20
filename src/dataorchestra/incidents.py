from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from dataorchestra.audit import now_iso
from dataorchestra.runs import new_run_id
from dataorchestra.states import DiagnosticStatus


INCIDENT_TYPES = {
    "sensitive_data_detected",
    "invalid_files",
    "post_preflight_change",
    "analysis_export_error",
    "accidental_sensitive_submission",
    "process_deviation",
    "other",
}

SEVERITIES = {"alta", "media", "baja"}
_SENSITIVE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"\b\d{2}-?\d{8}-?\d\b"),
    re.compile(r"\b\d{7,}\b"),
    re.compile(r"\+?\d[\d\s().-]{8,}\d"),
)


def register_incident(
    client_dir: str | Path,
    incident_type: str,
    severity: str,
    responsible: str,
    action_taken: str,
    notes: str = "",
    flow_stage: str | None = None,
    requires_data_deletion: bool = False,
    confirm_no_sensitive_values: bool = False,
) -> dict[str, Any]:
    client_path = Path(client_dir)
    incidents_dir = client_path / "diagnostics" / "incidents"
    incidents_dir.mkdir(parents=True, exist_ok=True)

    incident_type = incident_type.strip()
    severity = severity.strip().lower()
    responsible = responsible.strip()
    action_taken = action_taken.strip()
    notes = notes.strip()
    flow_stage = flow_stage.strip() if flow_stage else _current_flow_stage(client_path)

    blocker = _registration_blocker(
        client_path=client_path,
        incident_type=incident_type,
        severity=severity,
        responsible=responsible,
        action_taken=action_taken,
        notes=notes,
        confirm_no_sensitive_values=confirm_no_sensitive_values,
    )
    if blocker:
        _write_json(incidents_dir / "registration_blocked.json", blocker)
        return blocker

    config = _read_yaml(client_path / "client.yaml")
    client_id = str(config.get("client", {}).get("id") or client_path.name)
    registered_at = now_iso()
    incident_id = f"incident_{new_run_id()}"
    record_path = incidents_dir / f"{incident_id}.json"
    record = {
        "client_id": client_id,
        "incident_id": incident_id,
        "status": "incident_registered",
        "incident_status": "open",
        "incident_type": incident_type,
        "severity": severity,
        "flow_stage": flow_stage,
        "responsible": responsible,
        "action_taken": action_taken,
        "notes": notes,
        "requires_data_deletion": requires_data_deletion,
        "flow_blocked": severity in {"alta", "media"},
        "registered_at": registered_at,
        "recommended_next_action": _recommended_next_action(incident_type, severity),
    }

    _write_json(record_path, record)
    _write_incident_index(incidents_dir)

    return {
        "client_id": client_id,
        "status": "incident_registered",
        "incident_id": incident_id,
        "incident_record": str(record_path),
        "severity": severity,
        "incident_type": incident_type,
        "flow_blocked": record["flow_blocked"],
        "requires_data_deletion": requires_data_deletion,
        "recommended_next_action": record["recommended_next_action"],
    }


def resolve_incident(
    client_dir: str | Path,
    incident_id: str,
    responsible: str,
    resolution: str,
    confirm_no_sensitive_values: bool = False,
) -> dict[str, Any]:
    client_path = Path(client_dir)
    incidents_dir = client_path / "diagnostics" / "incidents"
    incidents_dir.mkdir(parents=True, exist_ok=True)

    incident_id = incident_id.strip()
    responsible = responsible.strip()
    resolution = resolution.strip()
    blocker = _resolution_blocker(
        client_path=client_path,
        incident_id=incident_id,
        responsible=responsible,
        resolution=resolution,
        confirm_no_sensitive_values=confirm_no_sensitive_values,
    )
    if blocker:
        _write_json(incidents_dir / "resolution_blocked.json", blocker)
        return blocker

    record_path = incidents_dir / f"{incident_id}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    resolved_at = now_iso()
    record["incident_status"] = "closed"
    record["resolved_by"] = responsible
    record["resolution"] = resolution
    record["resolved_at"] = resolved_at
    _write_json(record_path, record)
    _write_incident_index(incidents_dir)

    return {
        "client_id": record.get("client_id") or _read_client_id(client_path),
        "status": "incident_resolved",
        "incident_id": incident_id,
        "incident_record": str(record_path),
        "severity": record.get("severity"),
        "incident_type": record.get("incident_type"),
        "resolved_at": resolved_at,
        "flow_blocked": False,
        "recommended_next_action": "Ejecutar readiness antes de retomar el flujo del cliente.",
    }


def summarize_incidents(client_dir: str | Path) -> dict[str, Any]:
    incidents_dir = Path(client_dir) / "diagnostics" / "incidents"
    records = _incident_records(incidents_dir)
    open_records = [item for item in records if item.get("incident_status") == "open"]
    blocking_records = [item for item in open_records if item.get("flow_blocked") is True]
    latest = records[-1] if records else None

    return {
        "exists": bool(records),
        "count": len(records),
        "open_count": len(open_records),
        "blocking_open_count": len(blocking_records),
        "latest": _public_incident_summary(latest),
    }


def _registration_blocker(
    client_path: Path,
    incident_type: str,
    severity: str,
    responsible: str,
    action_taken: str,
    notes: str,
    confirm_no_sensitive_values: bool,
) -> dict[str, Any] | None:
    if not (client_path / "client.yaml").exists():
        return _blocked("client_config_missing", "client.yaml is required to register an incident.")
    if incident_type not in INCIDENT_TYPES:
        return _blocked("invalid_incident_type", f"incident_type must be one of: {', '.join(sorted(INCIDENT_TYPES))}.")
    if severity not in SEVERITIES:
        return _blocked("invalid_severity", f"severity must be one of: {', '.join(sorted(SEVERITIES))}.")
    if not responsible:
        return _blocked("responsible_required", "Responsible name is required.")
    if not action_taken:
        return _blocked("action_taken_required", "Action taken is required.")
    if not confirm_no_sensitive_values:
        return _blocked("sensitive_values_confirmation_required", "Confirm that notes and action_taken do not contain sensitive values.")
    if _contains_sensitive_value(action_taken) or _contains_sensitive_value(notes):
        return _blocked("sensitive_value_detected", "Do not store emails, phone numbers, document numbers or other sensitive values in incident records.")
    return None


def _resolution_blocker(
    client_path: Path,
    incident_id: str,
    responsible: str,
    resolution: str,
    confirm_no_sensitive_values: bool,
) -> dict[str, Any] | None:
    if not (client_path / "client.yaml").exists():
        return _blocked("client_config_missing", "client.yaml is required to resolve an incident.")
    if not re.fullmatch(r"incident_[A-Za-z0-9]+", incident_id):
        return _blocked("invalid_incident_id", "incident_id is invalid.")
    record_path = client_path / "diagnostics" / "incidents" / f"{incident_id}.json"
    if not record_path.exists():
        return _blocked("incident_not_found", "Incident record was not found.")
    if not responsible:
        return _blocked("responsible_required", "Responsible name is required.")
    if not resolution:
        return _blocked("resolution_required", "Resolution is required.")
    if not confirm_no_sensitive_values:
        return _blocked("sensitive_values_confirmation_required", "Confirm that resolution does not contain sensitive values.")
    if _contains_sensitive_value(resolution):
        return _blocked("sensitive_value_detected", "Do not store emails, phone numbers, document numbers or other sensitive values in incident records.")
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if record.get("incident_status") == "closed":
        return _blocked("incident_already_closed", "Incident is already closed.")
    return None


def _current_flow_stage(client_path: Path) -> str:
    try:
        closure = _read_json(client_path / "diagnostics" / "closure" / "closure_record.json")
        approval = _read_json(client_path / "diagnostics" / "review" / "approval_record.json")
        analysis = _read_json(client_path / "reports" / "diagnostico_borrador.json")
        preflight = _read_json(client_path / "diagnostics" / "preflight" / "preflight_report.json")
        config = _read_yaml(client_path / "client.yaml")
        if closure and closure.get("status") == DiagnosticStatus.PILOT_CLOSED.value:
            return DiagnosticStatus.PILOT_CLOSED.value
        if config.get("client", {}).get("status") == DiagnosticStatus.PILOT_CLOSED.value:
            return DiagnosticStatus.PILOT_CLOSED.value
        if approval and approval.get("status") == DiagnosticStatus.APPROVED_FOR_DELIVERY.value:
            return DiagnosticStatus.APPROVED_FOR_DELIVERY.value
        if analysis and analysis.get("report_status") == DiagnosticStatus.PENDING_HUMAN_REVIEW.value:
            return DiagnosticStatus.PENDING_HUMAN_REVIEW.value
        if preflight and preflight.get("status"):
            return str(preflight["status"])
        return "preflight_required"
    except (FileNotFoundError, json.JSONDecodeError, yaml.YAMLError):
        return "unknown"


def _recommended_next_action(incident_type: str, severity: str) -> str:
    actions = {
        "sensitive_data_detected": "Detener el flujo, no analizar y pedir una version anonimizada corregida.",
        "invalid_files": "Pedir correccion de archivos y ejecutar preflight nuevamente.",
        "post_preflight_change": "Descartar el preflight anterior y ejecutar uno nuevo antes de analizar.",
        "analysis_export_error": "No entregar borradores incompletos; corregir causa y regenerar artefactos.",
        "accidental_sensitive_submission": "No copiar el dato sensible, solicitar reenvio anonimizado y aplicar politica de borrado.",
        "process_deviation": "Revisar runbook, documentar decision y validar readiness antes de continuar.",
        "other": "Revisar el incidente y documentar decision antes de continuar.",
    }
    base = actions[incident_type]
    if severity == "alta":
        return f"{base} Requiere revision responsable antes de retomar el flujo."
    return base


def _write_incident_index(incidents_dir: Path) -> None:
    records = _incident_records(incidents_dir)
    payload = {
        "count": len(records),
        "open_count": len([item for item in records if item.get("incident_status") == "open"]),
        "blocking_open_count": len([item for item in records if item.get("incident_status") == "open" and item.get("flow_blocked") is True]),
        "incidents": [_public_incident_summary(item) for item in records],
    }
    _write_json(incidents_dir / "incidents_index.json", payload)


def _incident_records(incidents_dir: Path) -> list[dict[str, Any]]:
    if not incidents_dir.exists():
        return []
    records = []
    for path in sorted(incidents_dir.glob("incident_*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records


def _public_incident_summary(record: dict[str, Any] | None) -> dict[str, Any] | None:
    if not record:
        return None
    return {
        "incident_id": record.get("incident_id"),
        "incident_status": record.get("incident_status"),
        "incident_type": record.get("incident_type"),
        "severity": record.get("severity"),
        "flow_blocked": record.get("flow_blocked"),
        "registered_at": record.get("registered_at"),
    }


def _contains_sensitive_value(value: str) -> bool:
    return any(pattern.search(value) for pattern in _SENSITIVE_PATTERNS)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _read_client_id(client_path: Path) -> str:
    config = _read_yaml(client_path / "client.yaml")
    return str(config.get("client", {}).get("id") or client_path.name)


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _blocked(status: str, reason: str) -> dict[str, Any]:
    return {
        "status": status,
        "can_register": False,
        "reason": reason,
    }
