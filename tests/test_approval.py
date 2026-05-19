import json
from pathlib import Path

from dataorchestra.cli import run_analysis, run_approval, run_preflight
from test_analysis import write_analysis_client


def test_approval_creates_approved_delivery_artifacts(tmp_path: Path):
    client_dir = tmp_path / "cliente_approval"
    write_analysis_client(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"
    assert run_analysis(client_dir)["status"] == "analysis_done"

    result = run_approval(
        client_dir,
        reviewer="Responsable Comercial",
        notes="Metricas, alertas y privacidad revisadas contra el JSON tecnico.",
        confirm_human_review=True,
    )

    assert result["status"] == "approved_for_delivery"
    assert result["run_id"]
    assert result["can_deliver"] is True

    approval_record = json.loads((client_dir / "diagnostics" / "review" / "approval_record.json").read_text(encoding="utf-8"))
    assert approval_record["reviewer"] == "Responsable Comercial"
    assert approval_record["human_review_confirmed"] is True

    approved_json = json.loads((client_dir / "reports" / "diagnostico_aprobado.json").read_text(encoding="utf-8"))
    assert approved_json["report_status"] == "approved_for_delivery"
    assert approved_json["approval"]["status"] == "approved_for_delivery"
    assert Path(approved_json["outputs"]["archived_approval"]["approved_markdown"]).exists()

    approved_markdown = (client_dir / "reports" / "diagnostico_aprobado.md").read_text(encoding="utf-8")
    assert "# Aprobacion de entrega" in approved_markdown
    assert "**Estado:** approved_for_delivery" in approved_markdown
    assert "Responsable Comercial" in approved_markdown

    approved_html = (client_dir / "reports" / "diagnostico_aprobado.html").read_text(encoding="utf-8")
    assert "Diagnostico ejecutivo aprobado" in approved_html
    assert "approved_for_delivery" in approved_html
    assert "Responsable Comercial" in approved_html
    assert Path(approved_json["outputs"]["archived_approval"]["approved_html"]).exists()


def test_approval_blocks_without_explicit_human_review_confirmation(tmp_path: Path):
    client_dir = tmp_path / "cliente_approval"
    write_analysis_client(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"
    assert run_analysis(client_dir)["status"] == "analysis_done"

    result = run_approval(client_dir, reviewer="Responsable Comercial", notes="Revisado.", confirm_human_review=False)

    assert result["status"] == "human_review_confirmation_required"
    assert result["can_deliver"] is False
    assert (client_dir / "diagnostics" / "review" / "approval_blocked.json").exists()
    assert not (client_dir / "reports" / "diagnostico_aprobado.md").exists()


def test_approval_blocks_without_analysis_draft(tmp_path: Path):
    client_dir = tmp_path / "cliente_approval"
    client_dir.mkdir()

    result = run_approval(client_dir, reviewer="Responsable Comercial", notes="Revisado.", confirm_human_review=True)

    assert result["status"] == "analysis_required"
    assert result["can_deliver"] is False
