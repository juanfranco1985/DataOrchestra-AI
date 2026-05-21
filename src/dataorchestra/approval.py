from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dataorchestra.audit import now_iso
from dataorchestra.recommendations import apply_tracking_to_analysis, load_recommendation_tracking
from dataorchestra.reporting import render_html_report, render_markdown_report
from dataorchestra.runs import archive_file, new_run_id, run_stage_dir
from dataorchestra.states import DiagnosticStatus


def approve_for_delivery(client_dir: str | Path, reviewer: str, notes: str, confirm_human_review: bool = False) -> dict:
    client_path = Path(client_dir)
    reports_dir = client_path / "reports"
    review_dir = client_path / "diagnostics" / "review"
    review_dir.mkdir(parents=True, exist_ok=True)

    reviewer = reviewer.strip()
    notes = notes.strip()
    draft_json_path = reports_dir / "diagnostico_borrador.json"
    draft_markdown_path = reports_dir / "diagnostico_borrador.md"

    blocked = _approval_blocker(draft_json_path, draft_markdown_path, reviewer, notes, confirm_human_review)
    if blocked:
        _write_json(review_dir / "approval_blocked.json", blocked)
        return blocked

    analysis = json.loads(draft_json_path.read_text(encoding="utf-8"))
    analysis = apply_tracking_to_analysis(analysis, load_recommendation_tracking(client_path))
    run_id = str(analysis.get("run_id") or new_run_id())
    archive_dir = run_stage_dir(client_path, run_id, "approval")
    approval = {
        "client_id": analysis["client_id"],
        "run_id": run_id,
        "status": DiagnosticStatus.APPROVED_FOR_DELIVERY.value,
        "reviewer": reviewer,
        "notes": notes,
        "approved_at": now_iso(),
        "source_draft_json": str(draft_json_path),
        "source_draft_markdown": str(draft_markdown_path),
        "human_review_confirmed": True,
    }
    approved_json_path = reports_dir / "diagnostico_aprobado.json"
    approved_markdown_path = reports_dir / "diagnostico_aprobado.md"
    approved_html_path = reports_dir / "diagnostico_aprobado.html"
    approved_payload = {
        **analysis,
        "report_status": DiagnosticStatus.APPROVED_FOR_DELIVERY.value,
        "approval": approval,
        "outputs": {
            **analysis.get("outputs", {}),
            "approved_json": str(approved_json_path),
            "approved_markdown": str(approved_markdown_path),
            "approved_html": str(approved_html_path),
            "approval_record": str(review_dir / "approval_record.json"),
            "approval_archive_dir": str(archive_dir),
            "archived_approval": {
                "approval_record": str(archive_dir / "approval_record.json"),
                "approved_json": str(archive_dir / approved_json_path.name),
                "approved_markdown": str(archive_dir / approved_markdown_path.name),
                "approved_html": str(archive_dir / approved_html_path.name),
            },
        },
    }
    approved_markdown = _render_approved_markdown(render_markdown_report(approved_payload), approval)
    approved_html = render_html_report(approved_payload, approval=approval)

    _write_json(review_dir / "approval_record.json", approval)
    _write_json(approved_json_path, approved_payload)
    approved_markdown_path.write_text(approved_markdown, encoding="utf-8")
    approved_html_path.write_text(approved_html, encoding="utf-8")
    for path in (review_dir / "approval_record.json", approved_json_path, approved_markdown_path, approved_html_path):
        archive_file(client_path, run_id, "approval", path)
    return {
        "client_id": analysis["client_id"],
        "run_id": run_id,
        "status": DiagnosticStatus.APPROVED_FOR_DELIVERY.value,
        "can_deliver": True,
        "approval_record": str(review_dir / "approval_record.json"),
        "approved_json": str(approved_json_path),
        "approved_markdown": str(approved_markdown_path),
        "approved_html": str(approved_html_path),
    }


def _approval_blocker(draft_json_path: Path, draft_markdown_path: Path, reviewer: str, notes: str, confirm_human_review: bool) -> dict | None:
    if not confirm_human_review:
        return _blocked("human_review_confirmation_required", "Use explicit human review confirmation before approving delivery.")
    if not reviewer:
        return _blocked("reviewer_required", "Reviewer name is required.")
    if not notes:
        return _blocked("review_notes_required", "Review notes are required.")
    if not draft_json_path.exists() or not draft_markdown_path.exists():
        return _blocked("analysis_required", "Draft analysis JSON and Markdown must exist before approval.")

    analysis = json.loads(draft_json_path.read_text(encoding="utf-8"))
    if analysis.get("status") != DiagnosticStatus.ANALYSIS_DONE.value:
        return _blocked("analysis_not_done", f"Analysis status is {analysis.get('status')}.")
    if analysis.get("report_status") != DiagnosticStatus.PENDING_HUMAN_REVIEW.value:
        return _blocked("invalid_report_status", f"Report status is {analysis.get('report_status')}.")
    return None


def _blocked(status: str, reason: str) -> dict:
    return {
        "status": status,
        "can_deliver": False,
        "reason": reason,
    }


def _render_approved_markdown(draft_markdown: str, approval: dict[str, Any]) -> str:
    body = draft_markdown.replace("**Estado:** pending_human_review", "**Estado:** approved_for_delivery")
    header = "\n".join(
        [
            "# Aprobacion de entrega",
            "",
            f"- Estado: `approved_for_delivery`",
            f"- Revisor: {approval['reviewer']}",
            f"- Fecha UTC: {approval['approved_at']}",
            f"- Notas: {approval['notes']}",
            "",
            "---",
            "",
        ]
    )
    return header + body


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
