from pathlib import Path

from dataorchestra.cli import run_preflight, run_readiness
from dataorchestra.clients import create_client_workspace
from dataorchestra.readiness import CRITICAL_DOCS


def write_required_docs(repo_root: Path) -> None:
    for relative in CRITICAL_DOCS:
        path = repo_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Documento requerido\n", encoding="utf-8")


def write_ready_raw(client_dir: Path) -> None:
    raw_dir = client_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria 1,2,100,80\n",
        encoding="utf-8",
    )
    (raw_dir / "productos.csv").write_text(
        "producto,categoria,precio_unitario,costo_unitario\n"
        "Producto A,Categoria 1,100,80\n",
        encoding="utf-8",
    )
    (raw_dir / "stock.csv").write_text(
        "producto,stock_actual,stock_minimo,ventas_ultimos_30_dias\n"
        "Producto A,20,5,3\n",
        encoding="utf-8",
    )


def check_ids(result: dict) -> set[str]:
    return {check["id"] for check in result["checks"]}


def test_readiness_passes_ready_preflight_with_warnings_for_later_stages(tmp_path: Path):
    repo_root = tmp_path / "repo"
    write_required_docs(repo_root)
    runtime_clients = tmp_path / "runtime" / "clients"
    workspace = create_client_workspace(runtime_clients, "cliente_ready")
    client_dir = Path(workspace["client_dir"])
    write_ready_raw(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"

    result = run_readiness(client_dir, repo_root=repo_root)

    assert result["can_continue"] is True
    assert result["overall_status"] == "ready_with_warnings"
    assert "preflight_ready" in check_ids(result)
    assert "client_outside_repo" in check_ids(result)
    assert "approval_missing" in check_ids(result)
    assert result["failure_count"] == 0


def test_readiness_blocks_incomplete_workspace(tmp_path: Path):
    repo_root = tmp_path / "repo"
    write_required_docs(repo_root)
    client_dir = tmp_path / "cliente_incompleto"
    (client_dir / "raw").mkdir(parents=True)
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_incompleto\n", encoding="utf-8")

    result = run_readiness(client_dir, repo_root=repo_root)

    ids = check_ids(result)
    assert result["can_continue"] is False
    assert result["overall_status"] == "blocked"
    assert "processed_dir_missing" in ids
    assert "raw_files_missing" in ids
    assert "preflight_missing" in ids


def test_readiness_blocks_when_critical_docs_are_missing(tmp_path: Path):
    workspace = create_client_workspace(tmp_path / "runtime" / "clients", "cliente_docs")
    client_dir = Path(workspace["client_dir"])
    write_ready_raw(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"

    result = run_readiness(client_dir, repo_root=tmp_path / "repo_sin_docs")

    assert result["can_continue"] is False
    assert any(check["id"].endswith("_missing") and check["category"] == "documentation" for check in result["checks"])
