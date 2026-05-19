from pathlib import Path
import json
import yaml

from dataorchestra.cli import run_close_pilot
from dataorchestra.runtime import close_pilot, prepare_runtime


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
