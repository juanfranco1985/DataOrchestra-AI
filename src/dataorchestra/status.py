from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from dataorchestra.incidents import summarize_incidents
from dataorchestra.recommendations import summarize_recommendations
from dataorchestra.states import DiagnosticStatus


EXPECTED_RAW_FILES = ("ventas.csv", "productos.csv", "stock.csv")


def inspect_client_status(client_dir: str | Path) -> dict[str, Any]:
    client_path = Path(client_dir)
    raw_dir = client_path / "raw"
    preflight = _read_json(client_path / "diagnostics" / "preflight" / "preflight_report.json")
    analysis = _read_json(client_path / "reports" / "diagnostico_borrador.json")
    approval = _read_json(client_path / "diagnostics" / "review" / "approval_record.json")
    delivery = _read_json(client_path / "diagnostics" / "delivery" / "delivery_record.json")
    closure = _read_json(client_path / "diagnostics" / "closure" / "closure_record.json")
    retention = _read_json(client_path / "diagnostics" / "closure" / "retention_record.json")
    data_quality = _read_json(client_path / "diagnostics" / "analysis" / "data_quality.json") or _read_json(client_path / "diagnostics" / "data_quality" / "data_quality_report.json")
    config = _read_yaml(client_path / "client.yaml")
    raw_files = _raw_files_status(raw_dir)
    current_stage = _current_stage(raw_files, preflight, analysis, approval, delivery, closure, config)
    incidents = summarize_incidents(client_path)
    recommendations = summarize_recommendations(client_path)

    return {
        "client_id": _client_id(client_path, config),
        "client_dir": str(client_path),
        "current_stage": current_stage,
        "next_action": _incident_next_action(incidents) or _next_action(current_stage),
        "raw_files": raw_files,
        "preflight": _preflight_status(preflight),
        "analysis": _analysis_status(analysis),
        "approval": _approval_status(approval),
        "delivery": _delivery_status(delivery),
        "closure": _closure_status(closure),
        "retention": _retention_status(retention),
        "data_quality": _data_quality_status(data_quality),
        "recommendations": recommendations,
        "incidents": incidents,
        "last_audit_event": _last_audit_event(client_path / "logs" / "audit.jsonl"),
    }


def _current_stage(
    raw_files: dict[str, Any],
    preflight: dict | None,
    analysis: dict | None,
    approval: dict | None,
    delivery: dict | None,
    closure: dict | None,
    config: dict,
) -> str:
    if closure and closure.get("status") == DiagnosticStatus.PILOT_CLOSED.value:
        return DiagnosticStatus.PILOT_CLOSED.value
    if config.get("client", {}).get("status") == DiagnosticStatus.PILOT_CLOSED.value:
        return DiagnosticStatus.PILOT_CLOSED.value
    if delivery and delivery.get("status") == DiagnosticStatus.DELIVERED.value:
        return DiagnosticStatus.DELIVERED.value
    if config.get("client", {}).get("status") == DiagnosticStatus.DELIVERED.value:
        return DiagnosticStatus.DELIVERED.value
    if approval and approval.get("status") == DiagnosticStatus.APPROVED_FOR_DELIVERY.value:
        return DiagnosticStatus.APPROVED_FOR_DELIVERY.value
    if analysis and analysis.get("report_status") == DiagnosticStatus.PENDING_HUMAN_REVIEW.value:
        return DiagnosticStatus.PENDING_HUMAN_REVIEW.value
    if preflight:
        status = str(preflight.get("status") or "")
        if status:
            return status
    if raw_files["missing"]:
        return DiagnosticStatus.INTAKE_PENDING.value
    return "preflight_required"


def _next_action(stage: str) -> str:
    actions = {
        DiagnosticStatus.INTAKE_PENDING.value: "Cargar ventas.csv, productos.csv y stock.csv anonimizados en raw/.",
        DiagnosticStatus.PRIVACY_REVIEW_REQUIRED.value: "Detener proceso y revisar datos sensibles antes de continuar.",
        DiagnosticStatus.DATA_FIX_REQUIRED.value: "Pedir correccion de archivos y ejecutar preflight nuevamente.",
        DiagnosticStatus.READY_FOR_ANALYSIS.value: "Ejecutar analyze para generar borradores internos.",
        DiagnosticStatus.PENDING_HUMAN_REVIEW.value: "Revisar el borrador y aprobar solo con confirmacion humana.",
        DiagnosticStatus.APPROVED_FOR_DELIVERY.value: "Entregar solo el informe aprobado y registrar entrega con mark-delivered.",
        DiagnosticStatus.DELIVERED.value: "Cerrar piloto con close-pilot y registrar retencion o borrado.",
        DiagnosticStatus.PILOT_CLOSED.value: "No procesar mas datos. Revisar retencion o borrado segun politica.",
        "preflight_required": "Ejecutar preflight antes de analizar.",
    }
    return actions.get(stage, "Revisar el estado operativo del cliente.")


def _incident_next_action(incidents: dict[str, Any]) -> str | None:
    if incidents.get("blocking_open_count", 0) > 0:
        return "Resolver incidentes abiertos antes de continuar el flujo del cliente."
    return None


def _raw_files_status(raw_dir: Path) -> dict[str, Any]:
    present = sorted(path.name for path in raw_dir.glob("*.csv")) if raw_dir.exists() else []
    missing = [name for name in EXPECTED_RAW_FILES if name not in present]
    return {
        "expected": list(EXPECTED_RAW_FILES),
        "present": present,
        "missing": missing,
        "ready": not missing,
    }


def _preflight_status(preflight: dict | None) -> dict[str, Any]:
    if not preflight:
        return {"exists": False}
    return {
        "exists": True,
        "status": preflight.get("status"),
        "run_id": preflight.get("run_id"),
        "raw_file_count": preflight.get("raw_files", {}).get("count"),
    }


def _analysis_status(analysis: dict | None) -> dict[str, Any]:
    if not analysis:
        return {"exists": False}
    return {
        "exists": True,
        "status": analysis.get("status"),
        "report_status": analysis.get("report_status"),
        "run_id": analysis.get("run_id"),
        "draft_markdown": analysis.get("outputs", {}).get("draft_markdown"),
        "draft_html": analysis.get("outputs", {}).get("draft_html"),
    }


def _approval_status(approval: dict | None) -> dict[str, Any]:
    if not approval:
        return {"exists": False}
    return {
        "exists": True,
        "status": approval.get("status"),
        "run_id": approval.get("run_id"),
        "reviewer": approval.get("reviewer"),
        "approved_at": approval.get("approved_at"),
    }


def _delivery_status(delivery: dict | None) -> dict[str, Any]:
    if not delivery:
        return {"exists": False}
    return {
        "exists": True,
        "status": delivery.get("status"),
        "run_id": delivery.get("run_id"),
        "recipient": delivery.get("recipient"),
        "method": delivery.get("method"),
        "delivered_at": delivery.get("delivered_at"),
    }


def _closure_status(closure: dict | None) -> dict[str, Any]:
    if not closure:
        return {"exists": False}
    return {
        "exists": True,
        "status": closure.get("status"),
        "outcome": closure.get("outcome"),
        "reviewer": closure.get("reviewer"),
        "closed_at": closure.get("closed_at"),
        "data_retention_action_required": closure.get("data_retention_action_required"),
        "retention_action": closure.get("retention_action"),
        "retention_reviewed_at": closure.get("retention_reviewed_at"),
    }


def _retention_status(retention: dict | None) -> dict[str, Any]:
    if not retention:
        return {"exists": False}
    return {
        "exists": True,
        "status": retention.get("status"),
        "action": retention.get("action"),
        "responsible": retention.get("responsible"),
        "reviewed_at": retention.get("reviewed_at"),
    }


def _data_quality_status(data_quality: dict | None) -> dict[str, Any]:
    if not data_quality:
        return {"exists": False}
    return {
        "exists": True,
        "status": data_quality.get("status") or "data_quality_assessed",
        "score": data_quality.get("score"),
        "level": data_quality.get("level"),
        "target_score": data_quality.get("target_score"),
        "can_support_diagnostic": data_quality.get("can_support_diagnostic"),
        "finding_count": len(data_quality.get("findings") or []),
    }


def _client_id(client_path: Path, config: dict) -> str:
    return str(config.get("client", {}).get("id") or client_path.name)


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _last_audit_event(path: Path) -> dict | None:
    if not path.exists():
        return None
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])
