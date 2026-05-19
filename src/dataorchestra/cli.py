from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from dataorchestra.analytics import run_client_analysis
from dataorchestra.approval import approve_for_delivery
from dataorchestra.audit import append_audit_event
from dataorchestra.clients import create_client_workspace
from dataorchestra.integrity import fingerprint_files
from dataorchestra.privacy import scan_csv_files
from dataorchestra.runs import archive_file, new_run_id, run_stage_dir
from dataorchestra.states import DiagnosticStatus
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

    preflight = sub.add_parser("preflight", help="Run privacy and raw data validation checks")
    preflight.add_argument("--client-dir", required=True)

    analyze = sub.add_parser("analyze", help="Run deterministic pilot analytics after approved preflight")
    analyze.add_argument("--client-dir", required=True)

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
    if args.command == "preflight":
        report = run_preflight(args.client_dir)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["status"] == DiagnosticStatus.READY_FOR_ANALYSIS.value else 2
    if args.command == "analyze":
        result = run_analysis(args.client_dir)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == DiagnosticStatus.ANALYSIS_DONE.value else 2
    if args.command == "approve":
        result = run_approval(args.client_dir, args.reviewer, args.notes, args.confirm_human_review)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result["status"] == DiagnosticStatus.APPROVED_FOR_DELIVERY.value else 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
