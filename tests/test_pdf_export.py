from pathlib import Path
import subprocess

from dataorchestra.cli import run_approval, run_export_pdf, run_full_run
from dataorchestra.pdf import build_print_command
from test_analysis import write_analysis_client


def test_build_print_command_uses_file_uri_and_pdf_output(tmp_path: Path):
    browser = tmp_path / "browser.exe"
    html = tmp_path / "report.html"
    pdf = tmp_path / "report.pdf"
    html.write_text("<html></html>", encoding="utf-8")

    command = build_print_command(browser, html, pdf)

    assert str(browser) == command[0]
    assert "--headless=new" in command
    assert f"--print-to-pdf={pdf.resolve()}" in command
    assert html.resolve().as_uri() == command[-1]


def test_export_pdf_creates_approved_pdf_and_archives_it(tmp_path: Path, monkeypatch):
    client_dir = tmp_path / "cliente_pdf"
    browser = tmp_path / "msedge.exe"
    browser.write_text("fake browser", encoding="utf-8")
    write_analysis_client(client_dir)
    assert run_full_run(client_dir)["status"] == "analysis_done"
    assert run_approval(
        client_dir,
        reviewer="Responsable",
        notes="Revision humana completada.",
        confirm_human_review=True,
    )["status"] == "approved_for_delivery"

    def fake_run(command, capture_output, text, timeout, check):
        output_arg = next(item for item in command if item.startswith("--print-to-pdf="))
        Path(output_arg.split("=", 1)[1]).write_bytes(b"%PDF-1.4\n")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("dataorchestra.pdf.subprocess.run", fake_run)

    result = run_export_pdf(client_dir, browser_path=browser)

    assert result["status"] == "pdf_exported"
    assert result["can_deliver"] is True
    assert Path(result["pdf_report"]).exists()
    assert Path(result["archived_pdf"]).exists()


def test_export_approved_pdf_blocks_without_approval(tmp_path: Path, monkeypatch):
    client_dir = tmp_path / "cliente_pdf_blocked"
    browser = tmp_path / "msedge.exe"
    browser.write_text("fake browser", encoding="utf-8")
    write_analysis_client(client_dir)
    assert run_full_run(client_dir)["status"] == "analysis_done"

    result = run_export_pdf(client_dir, browser_path=browser)

    assert result["status"] == "html_report_missing"
    assert result["can_deliver"] is False
