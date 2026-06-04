from pathlib import Path
import json
import yaml

from dataorchestra.cli import run_close_pilot, run_mark_delivered, run_record_retention
from dataorchestra.runtime import close_pilot, mark_delivered, prepare_runtime, record_retention_action
from dataorchestra.status import inspect_client_status


def test_prepare_runtime_creates_safe_operational_structure(tmp_path: Path):
    runtime = tmp_path / "DataOrchestra_Runtime"

    result = prepare_runtime(runtime)

    assert result["status"] == "runtime_ready"
    assert (runtime / ".gitignore").read_text(encoding="utf-8").startswith("*")
    assert (runtime / "runtime_policy.yaml").exists()
    for name in ("clients", "intake", "exports", "archive", "logs", "policies", "deletion_requests"):
        assert (runtime / name).is_dir()
    policy = yaml.safe_load((runtime / "runtime_policy.yaml").read_text(encoding="utf-8"))
    assert policy["git_tracking_allowed"] is False
    assert "ventas.csv" in policy["accepted_files"]


def test_close_pilot_writes_closure_record_and_updates_client_config(tmp_path: Path):
    client_dir = tmp_path / "cliente_close"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_close\n"
        "  status: approved_for_delivery\n"
        "pilot:\n"
        "  delivery_allowed: true\n",
        encoding="utf-8",
    )

    result = close_pilot(
        client_dir,
        reviewer="Responsable",
        notes="Piloto cerrado con feedback registrado.",
        outcome="completed",
        confirm_close=True,
    )

    assert result["status"] == "pilot_closed"
    assert result["data_retention_action_required"] is True
    record = json.loads((client_dir / "diagnostics" / "closure" / "closure_record.json").read_text(encoding="utf-8"))
    assert record["outcome"] == "completed"
    config = yaml.safe_load((client_dir / "client.yaml").read_text(encoding="utf-8"))
    assert config["client"]["status"] == "pilot_closed"
    assert config["pilot"]["delivery_allowed"] is False


def test_close_pilot_blocks_without_explicit_confirmation(tmp_path: Path):
    client_dir = tmp_path / "cliente_close"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_close\n", encoding="utf-8")

    result = run_close_pilot(
        client_dir,
        reviewer="Responsable",
        notes="Notas.",
        outcome="completed",
        confirm_close=False,
    )

    assert result["status"] == "closure_confirmation_required"
    assert result["can_close"] is False
    assert (client_dir / "diagnostics" / "closure" / "closure_blocked.json").exists()


def test_mark_delivered_requires_approved_report_and_updates_status(tmp_path: Path):
    client_dir = tmp_path / "cliente_delivery"
    (client_dir / "diagnostics" / "review").mkdir(parents=True)
    (client_dir / "reports").mkdir()
    (client_dir / "logs").mkdir()
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_delivery\n"
        "  status: approved_for_delivery\n"
        "pilot:\n"
        "  delivery_allowed: true\n",
        encoding="utf-8",
    )
    (client_dir / "diagnostics" / "review" / "approval_record.json").write_text(
        json.dumps(
            {
                "client_id": "cliente_delivery",
                "run_id": "run_1",
                "status": "approved_for_delivery",
                "human_review_confirmed": True,
            }
        ),
        encoding="utf-8",
    )
    (client_dir / "reports" / "diagnostico_aprobado.json").write_text(
        json.dumps({"report_status": "approved_for_delivery"}),
        encoding="utf-8",
    )

    result = mark_delivered(
        client_dir,
        recipient="Responsable cliente",
        method="email",
        notes="Informe aprobado enviado.",
        confirm_delivery=True,
    )

    assert result["status"] == "delivered"
    assert Path(result["delivery_record"]).exists()
    assert inspect_client_status(client_dir)["current_stage"] == "delivered"
    config = yaml.safe_load((client_dir / "client.yaml").read_text(encoding="utf-8"))
    assert config["client"]["status"] == "delivered"
    assert config["pilot"]["delivery_allowed"] is False


def test_mark_delivered_blocks_without_explicit_confirmation(tmp_path: Path):
    client_dir = tmp_path / "cliente_delivery"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_delivery\n", encoding="utf-8")

    result = run_mark_delivered(
        client_dir,
        recipient="Responsable cliente",
        method="email",
        notes="Notas.",
        confirm_delivery=False,
    )

    assert result["status"] == "delivery_confirmation_required"
    assert result["can_close"] is False
    assert (client_dir / "diagnostics" / "delivery" / "delivery_blocked.json").exists()


def test_record_retention_action_updates_closure_record(tmp_path: Path):
    client_dir = tmp_path / "cliente_retention"
    (client_dir / "diagnostics" / "closure").mkdir(parents=True)
    (client_dir / "logs").mkdir()
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_retention\npilot: {}\n", encoding="utf-8")
    (client_dir / "diagnostics" / "closure" / "closure_record.json").write_text(
        json.dumps(
            {
                "client_id": "cliente_retention",
                "status": "pilot_closed",
                "outcome": "completed",
                "data_retention_action_required": True,
            }
        ),
        encoding="utf-8",
    )

    result = record_retention_action(
        client_dir,
        responsible="Responsable",
        action="raw_deleted",
        notes="Raw eliminado manualmente segun politica.",
        confirm_retention_review=True,
    )

    assert result["status"] == "retention_recorded"
    closure = json.loads((client_dir / "diagnostics" / "closure" / "closure_record.json").read_text(encoding="utf-8"))
    assert closure["data_retention_action_required"] is False
    assert closure["retention_action"] == "raw_deleted"
    assert inspect_client_status(client_dir)["retention"]["action"] == "raw_deleted"


def test_record_retention_blocks_without_explicit_confirmation(tmp_path: Path):
    client_dir = tmp_path / "cliente_retention"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_retention\n", encoding="utf-8")

    result = run_record_retention(
        client_dir,
        responsible="Responsable",
        action="raw_deleted",
        notes="Notas.",
        confirm_retention_review=False,
    )

    assert result["status"] == "retention_review_confirmation_required"
    assert result["can_close"] is False
    assert (client_dir / "diagnostics" / "closure" / "retention_blocked.json").exists()


def test_record_retention_requires_closed_pilot(tmp_path: Path):
    client_dir = tmp_path / "cliente_retention"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_retention\n", encoding="utf-8")

    result = record_retention_action(
        client_dir,
        responsible="Responsable",
        action="raw_deleted",
        notes="Raw eliminado manualmente segun politica.",
        confirm_retention_review=True,
    )

    assert result["status"] == "closure_required"
    assert result["can_close"] is False
    assert (client_dir / "diagnostics" / "closure" / "retention_blocked.json").exists()
