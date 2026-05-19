from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

from dataorchestra.runs import archive_file


REPORT_SOURCES = {
    "approved": ("diagnostico_aprobado.html", "diagnostico_aprobado.pdf", "diagnostico_aprobado.json"),
    "draft": ("diagnostico_borrador.html", "diagnostico_borrador.pdf", "diagnostico_borrador.json"),
}


def export_report_pdf(
    client_dir: str | Path,
    source: str = "approved",
    output: str | Path | None = None,
    browser_path: str | Path | None = None,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    if source not in REPORT_SOURCES:
        return _blocked("invalid_source", f"Unknown source '{source}'. Use approved or draft.")

    client_path = Path(client_dir)
    html_name, pdf_name, json_name = REPORT_SOURCES[source]
    html_path = client_path / "reports" / html_name
    metadata_path = client_path / "reports" / json_name
    pdf_path = Path(output) if output else client_path / "reports" / pdf_name
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    if not html_path.exists():
        return _blocked("html_report_missing", f"HTML report not found: {html_path}")
    if source == "approved" and not metadata_path.exists():
        return _blocked("approved_metadata_missing", f"Approved report metadata not found: {metadata_path}")
    if source == "approved":
        approval_check = _check_approved_metadata(metadata_path)
        if approval_check:
            return approval_check

    browser = Path(browser_path) if browser_path else find_chromium_browser()
    if not browser or not browser.exists():
        return _blocked(
            "browser_not_found",
            "No Chromium-based browser found. Install Microsoft Edge or Google Chrome, or pass --browser-path.",
        )

    command = build_print_command(browser, html_path, pdf_path)
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds, check=False)
    except subprocess.TimeoutExpired:
        return _blocked("pdf_export_timeout", f"PDF export exceeded {timeout_seconds} seconds.")

    if completed.returncode != 0:
        return {
            "status": "pdf_export_failed",
            "can_deliver": False,
            "reason": "Browser print command failed.",
            "returncode": completed.returncode,
            "stderr": completed.stderr.strip(),
            "stdout": completed.stdout.strip(),
            "command": command,
        }
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        return _blocked("pdf_not_created", f"PDF output was not created: {pdf_path}")

    run_id = _read_run_id(metadata_path)
    archived_pdf = archive_file(client_path, run_id, "pdf", pdf_path) if run_id else None
    return {
        "status": "pdf_exported",
        "can_deliver": source == "approved",
        "source": source,
        "html_report": str(html_path),
        "pdf_report": str(pdf_path),
        "browser": str(browser),
        "run_id": run_id,
        "archived_pdf": archived_pdf,
    }


def find_chromium_browser() -> Path | None:
    env_path = os.environ.get("DATAORCHESTRA_BROWSER_PATH")
    if env_path:
        candidate = Path(env_path)
        if candidate.exists():
            return candidate

    candidates = [
        shutil.which("msedge"),
        shutil.which("microsoft-edge"),
        shutil.which("google-chrome"),
        shutil.which("chrome"),
        shutil.which("chromium"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    return None


def build_print_command(browser: str | Path, html_path: str | Path, pdf_path: str | Path) -> list[str]:
    return [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={Path(pdf_path).resolve()}",
        Path(html_path).resolve().as_uri(),
    ]


def _read_run_id(path: Path) -> str | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str(payload.get("run_id") or "") or None


def _check_approved_metadata(path: Path) -> dict[str, Any] | None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("report_status") != "approved_for_delivery":
        return _blocked("report_not_approved", f"Report status is {payload.get('report_status')}.")
    approval = payload.get("approval") or {}
    if approval.get("status") != "approved_for_delivery" or approval.get("human_review_confirmed") is not True:
        return _blocked("approval_record_invalid", "Approved metadata does not include confirmed human review.")
    return None


def _blocked(status: str, reason: str) -> dict[str, Any]:
    return {
        "status": status,
        "can_deliver": False,
        "reason": reason,
    }
