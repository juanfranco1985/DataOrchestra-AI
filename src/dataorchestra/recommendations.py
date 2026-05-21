from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from dataorchestra.audit import now_iso
from dataorchestra.runs import archive_file, new_run_id


RECOMMENDATION_STATUSES = {
    "pending_review",
    "accepted",
    "rejected",
    "needs_client_context",
    "converted_to_action",
    "completed",
    "superseded",
}
UPDATEABLE_RECOMMENDATION_STATUSES = RECOMMENDATION_STATUSES - {"superseded"}
TRACKING_RELATIVE_PATH = Path("diagnostics") / "recommendations" / "recommendation_tracking.json"
_SENSITIVE_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"\b\d{2}-?\d{8}-?\d\b"),
    re.compile(r"\b\d{7,}\b"),
    re.compile(r"\+?\d[\d\s().-]{8,}\d"),
)


def sync_recommendation_tracking(
    client_dir: str | Path,
    recommendations: list[dict[str, Any]],
    analysis_run_id: str,
    client_id: str,
) -> dict[str, Any]:
    client_path = Path(client_dir)
    tracking_path = _tracking_path(client_path)
    tracking_path.parent.mkdir(parents=True, exist_ok=True)

    previous = load_recommendation_tracking(client_path) or {}
    previous_by_id = {item["id"]: item for item in previous.get("recommendations", []) if item.get("id")}
    generated_at = now_iso()
    active_ids = set()
    records: list[dict[str, Any]] = []

    for recommendation in recommendations:
        recommendation_id = _recommendation_id(recommendation)
        active_ids.add(recommendation_id)
        prior = previous_by_id.get(recommendation_id, {})
        records.append(_tracked_record(recommendation_id, recommendation, prior, analysis_run_id, generated_at))

    for recommendation_id, prior in previous_by_id.items():
        if recommendation_id in active_ids:
            continue
        records.append(_superseded_record(prior, generated_at, analysis_run_id))

    payload = _tracking_payload(
        client_id=client_id,
        analysis_run_id=analysis_run_id,
        recommendations=records,
        generated_at=generated_at,
        current_path=tracking_path,
    )
    _write_json(tracking_path, payload)
    archived = archive_file(client_path, analysis_run_id, "analysis", tracking_path)
    payload["outputs"]["archived_tracking"] = archived
    _write_json(tracking_path, payload)
    return payload


def load_recommendation_tracking(client_dir: str | Path) -> dict[str, Any] | None:
    path = _tracking_path(Path(client_dir))
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_recommendations(client_dir: str | Path) -> dict[str, Any]:
    tracking = load_recommendation_tracking(client_dir)
    if not tracking:
        return {"exists": False}
    summary = tracking.get("summary") or _summary(tracking.get("recommendations") or [])
    return {
        "exists": True,
        "status": tracking.get("status"),
        "tracking_path": tracking.get("outputs", {}).get("current_tracking") or str(_tracking_path(Path(client_dir))),
        "analysis_run_id": tracking.get("analysis_run_id"),
        **summary,
    }


def update_recommendation_status(
    client_dir: str | Path,
    recommendation_id: str,
    status: str,
    reviewer: str,
    notes: str = "",
    owner: str = "",
    due_date: str = "",
    confirm_no_sensitive_values: bool = False,
) -> dict[str, Any]:
    client_path = Path(client_dir)
    tracking_path = _tracking_path(client_path)
    recommendation_id = recommendation_id.strip()
    status = status.strip().lower()
    reviewer = reviewer.strip()
    notes = notes.strip()
    owner = owner.strip()
    due_date = due_date.strip()

    blocker = _update_blocker(
        client_path=client_path,
        tracking_path=tracking_path,
        recommendation_id=recommendation_id,
        status=status,
        reviewer=reviewer,
        notes=notes,
        owner=owner,
        due_date=due_date,
        confirm_no_sensitive_values=confirm_no_sensitive_values,
    )
    if blocker:
        tracking_path.parent.mkdir(parents=True, exist_ok=True)
        _write_json(tracking_path.parent / "recommendation_update_blocked.json", blocker)
        return blocker

    tracking = json.loads(tracking_path.read_text(encoding="utf-8"))
    updated_at = now_iso()
    update_run_id = new_run_id()
    target = _find_recommendation(tracking["recommendations"], recommendation_id)
    previous_status = str(target.get("status") or "pending_review")

    target["status"] = status
    target["reviewer"] = reviewer
    target["notes"] = notes
    target["owner"] = owner
    target["due_date"] = due_date
    target["updated_at"] = updated_at
    target["last_update_run_id"] = update_run_id
    target.setdefault("history", []).append(
        {
            "run_id": update_run_id,
            "updated_at": updated_at,
            "previous_status": previous_status,
            "status": status,
            "reviewer": reviewer,
            "notes": notes,
            "owner": owner,
            "due_date": due_date,
        }
    )

    tracking["status"] = "recommendations_tracked"
    tracking["updated_at"] = updated_at
    tracking["last_update_run_id"] = update_run_id
    tracking["summary"] = _summary(tracking["recommendations"])
    _write_json(tracking_path, tracking)
    archived = archive_file(client_path, update_run_id, "recommendations", tracking_path)

    return {
        "client_id": tracking.get("client_id") or _read_client_id(client_path),
        "status": "recommendation_updated",
        "recommendation_id": recommendation_id,
        "previous_status": previous_status,
        "review_status": status,
        "reviewer": reviewer,
        "tracking_path": str(tracking_path),
        "archived_tracking": archived,
        "summary": tracking["summary"],
        "recommended_next_action": _recommended_next_action(status),
    }


def apply_tracking_to_recommendations(recommendations: list[dict[str, Any]], tracking: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not tracking:
        return recommendations
    tracked = {item["id"]: item for item in tracking.get("recommendations", []) if item.get("id")}
    output = []
    for recommendation in recommendations:
        recommendation_id = _recommendation_id(recommendation)
        tracked_item = tracked.get(recommendation_id)
        merged = dict(recommendation)
        if tracked_item:
            merged.update(_tracking_fields(tracked_item))
        output.append(merged)
    return output


def apply_tracking_to_analysis(analysis: dict[str, Any], tracking: dict[str, Any] | None) -> dict[str, Any]:
    if not tracking:
        return analysis
    payload = dict(analysis)
    payload["recommendations"] = apply_tracking_to_recommendations(list(analysis.get("recommendations") or []), tracking)
    payload["recommendation_tracking"] = {
        "status": tracking.get("status"),
        "analysis_run_id": tracking.get("analysis_run_id"),
        "summary": tracking.get("summary"),
        "tracking_path": tracking.get("outputs", {}).get("current_tracking"),
    }
    return payload


def _tracked_record(
    recommendation_id: str,
    recommendation: dict[str, Any],
    prior: dict[str, Any],
    analysis_run_id: str,
    generated_at: str,
) -> dict[str, Any]:
    status = prior.get("status") if prior.get("status") in UPDATEABLE_RECOMMENDATION_STATUSES else "pending_review"
    return {
        "id": recommendation_id,
        "priority": recommendation.get("priority"),
        "title": recommendation.get("title"),
        "detail": recommendation.get("detail"),
        "evidence_alert_ids": recommendation.get("evidence_alert_ids") or [],
        "status": status,
        "active": True,
        "reviewer": prior.get("reviewer", ""),
        "notes": prior.get("notes", ""),
        "owner": prior.get("owner", ""),
        "due_date": prior.get("due_date", ""),
        "created_at": prior.get("created_at") or generated_at,
        "updated_at": prior.get("updated_at") or generated_at,
        "created_from_analysis_run_id": prior.get("created_from_analysis_run_id") or analysis_run_id,
        "last_seen_analysis_run_id": analysis_run_id,
        "history": list(prior.get("history") or []),
    }


def _superseded_record(prior: dict[str, Any], generated_at: str, analysis_run_id: str) -> dict[str, Any]:
    record = dict(prior)
    record["active"] = False
    record["last_seen_analysis_run_id"] = prior.get("last_seen_analysis_run_id")
    if record.get("status") == "pending_review":
        record["status"] = "superseded"
        record.setdefault("history", []).append(
            {
                "run_id": analysis_run_id,
                "updated_at": generated_at,
                "previous_status": "pending_review",
                "status": "superseded",
                "reviewer": "system",
                "notes": "La recomendacion ya no aparece en el analisis vigente.",
                "owner": "",
                "due_date": "",
            }
        )
    record["updated_at"] = generated_at
    return record


def _tracking_payload(
    client_id: str,
    analysis_run_id: str,
    recommendations: list[dict[str, Any]],
    generated_at: str,
    current_path: Path,
) -> dict[str, Any]:
    return {
        "client_id": client_id,
        "status": "recommendations_tracked",
        "analysis_run_id": analysis_run_id,
        "generated_at": generated_at,
        "updated_at": generated_at,
        "summary": _summary(recommendations),
        "recommendations": recommendations,
        "outputs": {
            "current_tracking": str(current_path),
        },
    }


def _summary(recommendations: list[dict[str, Any]]) -> dict[str, int]:
    active = [item for item in recommendations if item.get("active") is not False]
    counts = {status: 0 for status in sorted(RECOMMENDATION_STATUSES)}
    for item in active:
        status = str(item.get("status") or "pending_review")
        counts[status] = counts.get(status, 0) + 1
    reviewed = len([item for item in active if item.get("status") not in {"pending_review", "superseded"}])
    return {
        "total": len(recommendations),
        "active": len(active),
        "reviewed": reviewed,
        **counts,
    }


def _tracking_fields(tracked_item: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_status": tracked_item.get("status"),
        "reviewer": tracked_item.get("reviewer"),
        "review_notes": tracked_item.get("notes"),
        "owner": tracked_item.get("owner"),
        "due_date": tracked_item.get("due_date"),
        "review_updated_at": tracked_item.get("updated_at"),
    }


def _update_blocker(
    client_path: Path,
    tracking_path: Path,
    recommendation_id: str,
    status: str,
    reviewer: str,
    notes: str,
    owner: str,
    due_date: str,
    confirm_no_sensitive_values: bool,
) -> dict[str, Any] | None:
    if not (client_path / "client.yaml").exists():
        return _blocked("client_config_missing", "client.yaml is required to update recommendations.")
    if not tracking_path.exists():
        return _blocked("recommendation_tracking_required", "Run analysis before updating recommendation tracking.")
    if not recommendation_id:
        return _blocked("recommendation_id_required", "Recommendation id is required.")
    if status not in UPDATEABLE_RECOMMENDATION_STATUSES:
        return _blocked("invalid_recommendation_status", f"status must be one of: {', '.join(sorted(UPDATEABLE_RECOMMENDATION_STATUSES))}.")
    if not reviewer:
        return _blocked("reviewer_required", "Reviewer name is required.")
    if not confirm_no_sensitive_values:
        return _blocked("sensitive_values_confirmation_required", "Confirm that recommendation tracking fields do not contain sensitive values.")
    if any(_contains_sensitive_value(value) for value in (reviewer, notes, owner)):
        return _blocked("sensitive_value_detected", "Do not store emails, phone numbers, document numbers or other sensitive values in recommendation tracking.")

    tracking = json.loads(tracking_path.read_text(encoding="utf-8"))
    target = _find_recommendation(tracking.get("recommendations") or [], recommendation_id)
    if not target:
        return _blocked("recommendation_not_found", "Recommendation id was not found in tracking.")
    if target.get("active") is False:
        return _blocked("recommendation_not_active", "Recommendation is no longer active in the current analysis.")
    return None


def _find_recommendation(recommendations: list[dict[str, Any]], recommendation_id: str) -> dict[str, Any] | None:
    for recommendation in recommendations:
        if recommendation.get("id") == recommendation_id:
            return recommendation
    return None


def _recommendation_id(recommendation: dict[str, Any]) -> str:
    return str(recommendation.get("id") or recommendation.get("title") or "recommendation").strip()


def _recommended_next_action(status: str) -> str:
    actions = {
        "accepted": "Mantener la recomendacion en el informe si la revision humana la valida.",
        "rejected": "Excluir o explicar la recomendacion antes de aprobar entrega.",
        "needs_client_context": "Pedir contexto adicional al cliente antes de decidir.",
        "converted_to_action": "Registrar responsable y proximo paso operativo fuera del informe.",
        "completed": "Conservar trazabilidad de cierre para seguimiento posterior.",
        "pending_review": "Revisar la recomendacion antes de aprobar entrega.",
    }
    return actions.get(status, "Revisar el seguimiento de recomendaciones.")


def _tracking_path(client_path: Path) -> Path:
    return client_path / TRACKING_RELATIVE_PATH


def _contains_sensitive_value(value: str) -> bool:
    return any(pattern.search(value) for pattern in _SENSITIVE_PATTERNS)


def _read_client_id(client_path: Path) -> str:
    config_path = client_path / "client.yaml"
    if not config_path.exists():
        return client_path.name
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return str(config.get("client", {}).get("id") or client_path.name)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _blocked(status: str, reason: str) -> dict[str, Any]:
    return {
        "status": status,
        "can_update": False,
        "reason": reason,
    }
