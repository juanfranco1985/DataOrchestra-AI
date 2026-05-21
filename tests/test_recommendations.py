import json
from pathlib import Path

from dataorchestra.cli import run_approval, run_full_run, run_recommendations, run_status, run_update_recommendation
from test_analysis import write_analysis_client


def test_analysis_creates_recommendation_tracking(tmp_path: Path):
    client_dir = tmp_path / "cliente_recommendations"
    write_analysis_client(client_dir)

    result = run_full_run(client_dir)
    tracking = run_recommendations(client_dir)
    draft = json.loads((client_dir / "reports" / "diagnostico_borrador.json").read_text(encoding="utf-8"))

    assert result["status"] == "analysis_done"
    assert tracking["status"] == "recommendations_tracked"
    assert tracking["summary"]["active"] == len(result["analysis"]["recommendations"])
    assert tracking["summary"]["pending_review"] == tracking["summary"]["active"]
    assert all(item["status"] == "pending_review" for item in tracking["recommendations"] if item["active"])
    assert all(item["review_status"] == "pending_review" for item in draft["recommendations"])
    assert Path(result["analysis"]["outputs"]["recommendation_tracking"]).exists()
    assert Path(result["analysis"]["outputs"]["archived"]["recommendation_tracking"]).exists()


def test_update_recommendation_records_review_status_and_audit(tmp_path: Path):
    client_dir = tmp_path / "cliente_update_recommendation"
    write_analysis_client(client_dir)
    assert run_full_run(client_dir)["status"] == "analysis_done"
    recommendation_id = run_recommendations(client_dir)["recommendations"][0]["id"]

    update = run_update_recommendation(
        client_dir,
        recommendation_id=recommendation_id,
        status="accepted",
        reviewer="Responsable",
        notes="Validada para la devolucion controlada.",
        owner="Responsable comercial",
        due_date="2026-06-01",
        confirm_no_sensitive_values=True,
    )
    tracking = run_recommendations(client_dir)
    status = run_status(client_dir)
    updated_item = next(item for item in tracking["recommendations"] if item["id"] == recommendation_id)

    assert update["status"] == "recommendation_updated"
    assert update["previous_status"] == "pending_review"
    assert tracking["summary"]["accepted"] == 1
    assert updated_item["status"] == "accepted"
    assert updated_item["owner"] == "Responsable comercial"
    assert updated_item["history"]
    assert status["recommendations"]["accepted"] == 1
    assert status["last_audit_event"]["event"] == "recommendation_updated"


def test_update_recommendation_requires_sensitive_value_confirmation(tmp_path: Path):
    client_dir = tmp_path / "cliente_blocked_recommendation"
    write_analysis_client(client_dir)
    assert run_full_run(client_dir)["status"] == "analysis_done"
    recommendation_id = run_recommendations(client_dir)["recommendations"][0]["id"]

    result = run_update_recommendation(
        client_dir,
        recommendation_id=recommendation_id,
        status="accepted",
        reviewer="Responsable",
    )

    assert result["status"] == "sensitive_values_confirmation_required"
    assert result["can_update"] is False


def test_approval_includes_updated_recommendation_tracking(tmp_path: Path):
    client_dir = tmp_path / "cliente_approval_recommendation"
    write_analysis_client(client_dir)
    assert run_full_run(client_dir)["status"] == "analysis_done"
    recommendation_id = run_recommendations(client_dir)["recommendations"][0]["id"]
    assert run_update_recommendation(
        client_dir,
        recommendation_id=recommendation_id,
        status="converted_to_action",
        reviewer="Responsable",
        notes="Se convierte en accion posterior al diagnostico.",
        owner="Responsable comercial",
        due_date="2026-06-01",
        confirm_no_sensitive_values=True,
    )["status"] == "recommendation_updated"

    approval = run_approval(
        client_dir,
        reviewer="Responsable",
        notes="Revision humana completada.",
        confirm_human_review=True,
    )
    approved = json.loads(Path(approval["approved_json"]).read_text(encoding="utf-8"))
    approved_markdown = Path(approval["approved_markdown"]).read_text(encoding="utf-8")

    assert approval["status"] == "approved_for_delivery"
    assert approved["recommendation_tracking"]["summary"]["converted_to_action"] == 1
    assert "Seguimiento: converted_to_action" in approved_markdown
