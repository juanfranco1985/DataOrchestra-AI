from pathlib import Path

from dataorchestra.cli import run_approval, run_close_pilot, run_full_run, run_status
from test_analysis import write_analysis_client


def test_status_reports_intake_pending_when_raw_files_are_missing(tmp_path: Path):
    client_dir = tmp_path / "cliente_status"
    (client_dir / "raw").mkdir(parents=True)
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_status\n", encoding="utf-8")

    result = run_status(client_dir)

    assert result["client_id"] == "cliente_status"
    assert result["current_stage"] == "intake_pending"
    assert result["raw_files"]["missing"] == ["ventas.csv", "productos.csv", "stock.csv"]
    assert "Cargar ventas.csv" in result["next_action"]


def test_full_run_generates_pending_human_review_and_status_tracks_next_action(tmp_path: Path):
    client_dir = tmp_path / "cliente_full_run"
    write_analysis_client(client_dir)

    result = run_full_run(client_dir)
    status = run_status(client_dir)

    assert result["status"] == "analysis_done"
    assert result["analysis"]["report_status"] == "pending_human_review"
    assert status["current_stage"] == "pending_human_review"
    assert status["analysis"]["exists"] is True
    assert status["approval"]["exists"] is False
    assert status["recommendations"]["exists"] is True
    assert status["recommendations"]["pending_review"] == status["recommendations"]["active"]
    assert "aprobar" in status["next_action"].lower()


def test_status_reports_approved_delivery_after_human_approval(tmp_path: Path):
    client_dir = tmp_path / "cliente_status_approved"
    write_analysis_client(client_dir)
    assert run_full_run(client_dir)["status"] == "analysis_done"
    assert run_approval(
        client_dir,
        reviewer="Responsable",
        notes="Revision humana completada.",
        confirm_human_review=True,
    )["status"] == "approved_for_delivery"

    status = run_status(client_dir)

    assert status["current_stage"] == "approved_for_delivery"
    assert status["approval"]["exists"] is True
    assert "Entregar" in status["next_action"]


def test_status_reports_closed_pilot_as_final_operational_stage(tmp_path: Path):
    client_dir = tmp_path / "cliente_status_closed"
    write_analysis_client(client_dir)
    assert run_full_run(client_dir)["status"] == "analysis_done"
    assert run_approval(
        client_dir,
        reviewer="Responsable",
        notes="Revision humana completada.",
        confirm_human_review=True,
    )["status"] == "approved_for_delivery"
    assert run_close_pilot(
        client_dir,
        reviewer="Responsable",
        notes="Cierre operativo registrado.",
        outcome="completed",
        confirm_close=True,
    )["status"] == "pilot_closed"

    status = run_status(client_dir)

    assert status["current_stage"] == "pilot_closed"
    assert status["closure"]["exists"] is True
    assert "No procesar" in status["next_action"]
