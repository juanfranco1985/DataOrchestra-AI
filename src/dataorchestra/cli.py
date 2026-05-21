from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from dataorchestra.analytics import run_client_analysis
from dataorchestra.approval import approve_for_delivery
from dataorchestra.audit import append_audit_event
from dataorchestra.clients import create_client_workspace
from dataorchestra.data_quality import assess_data_quality
from dataorchestra.incidents import INCIDENT_TYPES, SEVERITIES, register_incident, resolve_incident
from dataorchestra.integrity import fingerprint_files
from dataorchestra.pdf import export_report_pdf
from dataorchestra.privacy import scan_csv_files
from dataorchestra.readiness import inspect_readiness
from dataorchestra.runs import archive_file, new_run_id, run_stage_dir
from dataorchestra.runtime import close_pilot, default_runtime_dir, prepare_runtime
from dataorchestra.states import DiagnosticStatus
from dataorchestra.status import inspect_client_status
from dataorchestra.thresholds import resolve_thresholds
from dataorchestra.validation import validate_client_raw


def run_init_client(
    clients_root: str | Path,
    client_id: str,
    display_name: str | None = None,
    business_type: str = "Pendiente",
    currency: str = "ARS",
) -> dict:
    return create_client_workspace(
        clients_root,
        client_id=client_id,
        display_name=display_name,
        business_type=business_type,
        currency=currency,
    )


def run_preflight(client_dir: str | Path) -> dict:
    client_path = Path(client_dir)
    run_id = new_run_id()
    raw_dir = client_path / "raw"
    diagnostics_dir = client_path / "diagnostics" / "preflight"
    diagnostics_dir.mkdir(parents=True, exist_ok=True)

    client_id = _read_client_id(client_path)
    csv_files = sorted(raw_dir.glob("*.csv"))
    raw_fingerprints_before = fingerprint_files(csv_files)
    privacy = scan_csv_files(csv_files)
    validation = validate_client_raw(raw_dir)
    raw_fingerprints_after = fingerprint_files(sorted(raw_dir.glob("*.csv")))

    if not privacy.safe_to_continue:
        status = DiagnosticStatus.PRIVACY_REVIEW_REQUIRED.value
    elif not validation.can_continue:
        status = DiagnosticStatus.DATA_FIX_REQUIRED.value
    else:
        status = DiagnosticStatus.READY_FOR_ANALYSIS.value

    report = {
        "client_id": client_id,
        "run_id": run_id,
        "status": status,
        "privacy": privacy.to_dict(),
        "validation": validation.to_dict(),
        "raw_files": {
            "count": len(raw_fingerprints_after),
            "fingerprints": raw_fingerprints_after,
        },
        "raw_files_were_modified": raw_fingerprints_before != raw_fingerprints_after,
    }
    report_path = diagnostics_dir / "preflight_report.json"
    archived_report = str(run_stage_dir(client_path, run_id, "preflight") / report_path.name)
    report["outputs"] = {
        "current_report": str(report_path),
        "archived_report": archived_report,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    archive_file(client_path, run_id, "preflight", report_path)
    append_audit_event(
        client_path / "logs" / "audit.jsonl",
        "preflight",
        client_id,
        status,
        {"run_id": run_id, "report": str(report_path), "archived_report": archived_report},
    )
    return report


def run_analysis(client_dir: str | Path) -> dict:
    client_path = Path(client_dir)
    result = run_client_analysis(client_path)
    append_audit_event(
        client_path / "logs" / "audit.jsonl",
        "analysis",
        str(result.get("client_id") or _read_client_id(client_path)),
        str(result.get("status")),
        {"run_id": result.get("run_id"), "can_continue": bool(result.get("can_continue"))},
    )
    return result


def run_approval(client_dir: str | Path, reviewer: str, notes: str, confirm_human_review: bool) -> dict:
    client_path = Path(client_dir)
    result = approve_for_delivery(client_path, reviewer, notes, confirm_human_review=confirm_human_review)
    append_audit_event(
        client_path / "logs" / "audit.jsonl",
        "approval",
        str(result.get("client_id") or _read_client_id(client_path)),
        str(result.get("status")),
        {"run_id": result.get("run_id"), "can_deliver": bool(result.get("can_deliver")), "reviewer": reviewer},
    )
    return result


def run_status(client_dir: str | Path) -> dict:
    return inspect_client_status(client_dir)


def run_readiness(client_dir: str | Path, repo_root: str | Path | None = ".") -> dict:
    return inspect_readiness(client_dir, repo_root=repo_root)


def run_data_quality(client_dir: str | Path) -> dict:
    client_path = Path(client_dir)
    run_id = new_run_id()
    result = assess_data_quality(client_path)
    result["run_id"] = run_id
    result["status"] = "data_quality_assessed"
    report_path = client_path / "diagnostics" / "data_quality" / "data_quality_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    archived_report = str(run_stage_dir(client_path, run_id, "data_quality") / report_path.name)
    result["outputs"] = {
        "current_report": str(report_path),
        "archived_report": archived_report,
    }
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    archive_file(client_path, run_id, "data_quality", report_path)
    append_audit_event(
        client_path / "logs" / "audit.jsonl",
        "data_quality",
        _read_client_id(client_path),
        str(result.get("level")),
        {"run_id": run_id, "score": result.get("score"), "can_support_diagnostic": bool(result.get("can_support_diagnostic"))},
    )
    return result


def run_thresholds(client_dir: str | Path) -> dict:
    result = resolve_thresholds(client_dir)
    return {
        "status": "thresholds_resolved",
        "client_dir": str(Path(client_dir)),
        **result,
    }


def run_full_run(client_dir: str | Path) -> dict:
    preflight = run_preflight(client_dir)
    if preflight["status"] != DiagnosticStatus.READY_FOR_ANALYSIS.value:
        return {
            "client_id": preflight["client_id"],
            "status": preflight["status"],
            "can_continue": False,
            "preflight": preflight,
            "analysis": None,
            "next_action": inspect_client_status(client_dir)["next_action"],
        }

    analysis = run_analysis(client_dir)
    return {
        "client_id": analysis["client_id"],
        "status": analysis["status"],
        "can_continue": analysis["status"] == DiagnosticStatus.ANALYSIS_DONE.value,
        "preflight": preflight,
        "analysis": analysis,
        "next_action": "Revisar diagnostico_borrador.* y aprobar con confirmacion humana si corresponde.",
    }


def run_export_pdf(
    client_dir: str | Path,
    source: str = "approved",
    output: str | Path | None = None,
    browser_path: str | Path | None = None,
) -> dict:
    client_path = Path(client_dir)
    result = export_report_pdf(client_path, source=source, output=output, browser_path=browser_path)
    append_audit_event(
        client_path / "logs" / "audit.jsonl",
        "export_pdf",
        str(result.get("client_id") or _read_client_id(client_path)),
        str(result.get("status")),
        {
            "source": source,
            "pdf_report": result.get("pdf_report"),
            "can_deliver": bool(result.get("can_deliver")),
            "run_id": result.get("run_id"),
        },
    )
    return result


def run_prepare_runtime(runtime_dir: str | Path | None = None) -> dict:
    return prepare_runtime(runtime_dir)


def run_close_pilot(client_dir: str | Path, reviewer: str, notes: str, outcome: str, confirm_close: bool) -> dict:
    client_path = Path(client_dir)
    result = close_pilot(client_path, reviewer=reviewer, notes=notes, outcome=outcome, confirm_close=confirm_close)
    append_audit_event(
        client_path / "logs" / "audit.jsonl",
        "close_pilot",
        str(result.get("client_id") or _read_client_id(client_path)),
        str(result.get("status")),
        {
            "outcome": result.get("outcome"),
            "closure_record": result.get("closure_record"),
            "data_retention_action_required": bool(result.get("data_retention_action_required")),
        },
    )
    return result


def run_incident(
    client_dir: str | Path,
    incident_type: str,
    severity: str,
    responsible: str,
    action_taken: str,
    notes: str = "",
    flow_stage: str | None = None,
    requires_data_deletion: bool = False,
    confirm_no_sensitive_values: bool = False,
) -> dict:
    client_path = Path(client_dir)
    result = register_incident(
        client_path,
        incident_type=incident_type,
        severity=severity,
        responsible=responsible,
        action_taken=action_taken,
        notes=notes,
        flow_stage=flow_stage,
        requires_data_deletion=requires_data_deletion,
        confirm_no_sensitive_values=confirm_no_sensitive_values,
    )
    if result.get("status") == "incident_registered":
        append_audit_event(
            client_path / "logs" / "audit.jsonl",
            "incident_registered",
            str(result.get("client_id") or _read_client_id(client_path)),
            str(result.get("severity")),
            {
                "incident_id": result.get("incident_id"),
                "incident_type": result.get("incident_type"),
                "flow_blocked": bool(result.get("flow_blocked")),
                "requires_data_deletion": bool(result.get("requires_data_deletion")),
            },
        )
    return result


def run_resolve_incident(
    client_dir: str | Path,
    incident_id: str,
    responsible: str,
    resolution: str,
    confirm_no_sensitive_values: bool = False,
) -> dict:
    client_path = Path(client_dir)
    result = resolve_incident(
        client_path,
        incident_id=incident_id,
        responsible=responsible,
        resolution=resolution,
        confirm_no_sensitive_values=confirm_no_sensitive_values,
    )
    if result.get("status") == "incident_resolved":
        append_audit_event(
            client_path / "logs" / "audit.jsonl",
            "incident_resolved",
            str(result.get("client_id") or _read_client_id(client_path)),
            str(result.get("severity")),
            {
                "incident_id": result.get("incident_id"),
                "incident_type": result.get("incident_type"),
                "flow_blocked": False,
            },
        )
    return result


def _read_client_id(client_path: Path) -> str:
    config_path = client_path / "client.yaml"
    if not config_path.exists():
        return client_path.name
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return str(data.get("client", {}).get("id") or client_path.name)


def main() -> int:
    parser = argparse.ArgumentParser(description="DataOrchestra AI v2.0 pilot tools")
    sub = parser.add_subparsers(dest="command", required=True)

    init_client = sub.add_parser("init-client", help="Create a new controlled pilot client workspace")
    init_client.add_argument("--clients-root", default="clients")
    init_client.add_argument("--client-id", required=True)
    init_client.add_argument("--display-name")
    init_client.add_argument("--business-type", default="Pendiente")
    init_client.add_argument("--currency", default="ARS")

    prepare_runtime_parser = sub.add_parser("prepare-runtime", help="Create a local runtime directory for real client data")
    prepare_runtime_parser.add_argument("--runtime-dir", default=str(default_runtime_dir()))

    preflight = sub.add_parser("preflight", help="Run privacy and raw data validation checks")
    preflight.add_argument("--client-dir", required=True)

    analyze = sub.add_parser("analyze", help="Run deterministic pilot analytics after approved preflight")
    analyze.add_argument("--client-dir", required=True)

    status = sub.add_parser("status", help="Inspect client operational state and next action")
    status.add_argument("--client-dir", required=True)

    readiness = sub.add_parser("readiness", help="Run technical readiness checks for a controlled pilot")
    readiness.add_argument("--client-dir", required=True)
    readiness.add_argument("--repo-root", default=".")

    data_quality = sub.add_parser("data-quality", help="Assess raw data quality before interpreting a diagnosis")
    data_quality.add_argument("--client-dir", required=True)

    thresholds = sub.add_parser("thresholds", help="Show the active analytics thresholds for a client")
    thresholds.add_argument("--client-dir", required=True)

    full_run = sub.add_parser("full-run", help="Run preflight and analysis without approval")
    full_run.add_argument("--client-dir", required=True)

    export_pdf = sub.add_parser("export-pdf", help="Export an HTML report to PDF using Edge or Chrome")
    export_pdf.add_argument("--client-dir", required=True)
    export_pdf.add_argument("--source", choices=["approved", "draft"], default="approved")
    export_pdf.add_argument("--output")
    export_pdf.add_argument("--browser-path")

    close = sub.add_parser("close-pilot", help="Close a controlled pilot with an auditable record")
    close.add_argument("--client-dir", required=True)
    close.add_argument("--reviewer", required=True)
    close.add_argument("--notes", required=True)
    close.add_argument("--outcome", choices=["completed", "not_viable", "needs_follow_up", "converted_to_service"], required=True)
    close.add_argument("--confirm-close", action="store_true")

    incident = sub.add_parser("incident", help="Register an operational incident without storing sensitive values")
    incident.add_argument("--client-dir", required=True)
    incident.add_argument("--type", choices=sorted(INCIDENT_TYPES), required=True)
    incident.add_argument("--severity", choices=sorted(SEVERITIES), required=True)
    incident.add_argument("--responsible", required=True)
    incident.add_argument("--action-taken", required=True)
    incident.add_argument("--notes", default="")
    incident.add_argument("--flow-stage")
    incident.add_argument("--requires-data-deletion", action="store_true")
    incident.add_argument("--confirm-no-sensitive-values", action="store_true")

    resolve = sub.add_parser("resolve-incident", help="Resolve an open operational incident after mitigation")
    resolve.add_argument("--client-dir", required=True)
    resolve.add_argument("--incident-id", required=True)
    resolve.add_argument("--responsible", required=True)
    resolve.add_argument("--resolution", required=True)
    resolve.add_argument("--confirm-no-sensitive-values", action="store_true")

    approve = sub.add_parser("approve", help="Approve a reviewed draft for controlled delivery")
    approve.add_argument("--client-dir", required=True)
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--notes", required=True)
    approve.add_argument("--confirm-human-review", action="store_true")

    args = parser.parse_args()
    if args.command == "init-client":
        result = run_init_client(
            args.clients_root,
            client_id=args.client_id,
            display_name=args.display_name,
            business_type=args.business_type,
            currency=args.currency,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["can_continue"] else 2
    if args.command == "prepare-runtime":
        result = run_prepare_runtime(args.runtime_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "preflight":
        report = run_preflight(args.client_dir)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["status"] == DiagnosticStatus.READY_FOR_ANALYSIS.value else 2
    if args.command == "analyze":
        result = run_analysis(args.client_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == DiagnosticStatus.ANALYSIS_DONE.value else 2
    if args.command == "status":
        result = run_status(args.client_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "readiness":
        result = run_readiness(args.client_dir, repo_root=args.repo_root)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["can_continue"] else 2
    if args.command == "data-quality":
        result = run_data_quality(args.client_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["can_support_diagnostic"] else 2
    if args.command == "thresholds":
        result = run_thresholds(args.client_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if args.command == "full-run":
        result = run_full_run(args.client_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == DiagnosticStatus.ANALYSIS_DONE.value else 2
    if args.command == "export-pdf":
        result = run_export_pdf(args.client_dir, source=args.source, output=args.output, browser_path=args.browser_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "pdf_exported" else 2
    if args.command == "close-pilot":
        result = run_close_pilot(args.client_dir, reviewer=args.reviewer, notes=args.notes, outcome=args.outcome, confirm_close=args.confirm_close)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == DiagnosticStatus.PILOT_CLOSED.value else 2
    if args.command == "incident":
        result = run_incident(
            args.client_dir,
            incident_type=args.type,
            severity=args.severity,
            responsible=args.responsible,
            action_taken=args.action_taken,
            notes=args.notes,
            flow_stage=args.flow_stage,
            requires_data_deletion=args.requires_data_deletion,
            confirm_no_sensitive_values=args.confirm_no_sensitive_values,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "incident_registered" else 2
    if args.command == "resolve-incident":
        result = run_resolve_incident(
            args.client_dir,
            incident_id=args.incident_id,
            responsible=args.responsible,
            resolution=args.resolution,
            confirm_no_sensitive_values=args.confirm_no_sensitive_values,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == "incident_resolved" else 2
    if args.command == "approve":
        result = run_approval(args.client_dir, args.reviewer, args.notes, args.confirm_human_review)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == DiagnosticStatus.APPROVED_FOR_DELIVERY.value else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
