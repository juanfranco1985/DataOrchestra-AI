from pathlib import Path

import pytest
import yaml

from dataorchestra.cli import run_init_client
from dataorchestra.clients import create_client_workspace


def test_create_client_workspace_builds_required_operational_structure(tmp_path: Path):
    result = create_client_workspace(
        tmp_path / "clients",
        "cliente_002",
        display_name="Cliente Piloto 002",
        business_type="Retail",
        currency="ARS",
    )

    client_dir = Path(result["client_dir"])

    assert result["status"] == "client_workspace_created"
    assert result["required_raw_files"] == ["ventas.csv", "productos.csv", "stock.csv"]
    assert (client_dir / "client.yaml").exists()
    for subdir in ("raw", "processed", "diagnostics", "reports", "logs", "runs"):
        assert (client_dir / subdir / ".gitkeep").exists()

    config = yaml.safe_load((client_dir / "client.yaml").read_text(encoding="utf-8"))
    assert config["client"]["id"] == "cliente_002"
    assert config["client"]["status"] == "intake_pending"
    assert config["pilot"]["report_status"] == "pending_human_review"
    assert config["pilot"]["delivery_allowed"] is False


def test_create_client_workspace_refuses_existing_client(tmp_path: Path):
    clients_root = tmp_path / "clients"
    assert create_client_workspace(clients_root, "cliente_002")["can_continue"] is True

    result = create_client_workspace(clients_root, "cliente_002")

    assert result["status"] == "client_already_exists"
    assert result["can_continue"] is False


def test_create_client_workspace_rejects_unsafe_client_id(tmp_path: Path):
    with pytest.raises(ValueError):
        create_client_workspace(tmp_path / "clients", "../cliente")


def test_run_init_client_exposes_cli_operation(tmp_path: Path):
    result = run_init_client(tmp_path / "clients", "cliente_cli", display_name="Cliente CLI")

    assert result["status"] == "client_workspace_created"
    assert Path(result["client_dir"]).name == "cliente_cli"
