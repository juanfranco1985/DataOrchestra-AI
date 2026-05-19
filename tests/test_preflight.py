import json
from pathlib import Path

from dataorchestra.cli import run_preflight


def write_valid_client(client_dir: Path) -> None:
    raw_dir = client_dir / "raw"
    raw_dir.mkdir(parents=True)
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_test\n",
        encoding="utf-8",
    )
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70\n",
        encoding="utf-8",
    )
    (raw_dir / "productos.csv").write_text(
        "producto,categoria,precio_unitario,costo_unitario\n"
        "Producto A,Categoria 1,100,70\n",
        encoding="utf-8",
    )
    (raw_dir / "stock.csv").write_text(
        "producto,stock_actual,stock_minimo,ventas_ultimos_30_dias\n"
        "Producto A,10,2,4\n",
        encoding="utf-8",
    )


def test_preflight_ready_report_includes_raw_fingerprints_and_audit_log(tmp_path: Path):
    client_dir = tmp_path / "cliente_test"
    write_valid_client(client_dir)

    report = run_preflight(client_dir)

    assert report["client_id"] == "cliente_test"
    assert report["status"] == "ready_for_analysis"
    assert report["run_id"]
    assert report["raw_files_were_modified"] is False
    assert report["raw_files"]["count"] == 3
    assert {item["name"] for item in report["raw_files"]["fingerprints"]} == {
        "productos.csv",
        "stock.csv",
        "ventas.csv",
    }
    assert all(item["sha256"] for item in report["raw_files"]["fingerprints"])

    report_path = client_dir / "diagnostics" / "preflight" / "preflight_report.json"
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
    assert Path(report["outputs"]["archived_report"]).exists()

    audit_lines = (client_dir / "logs" / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(audit_lines) == 1
    assert json.loads(audit_lines[0])["event"] == "preflight"
    assert json.loads(audit_lines[0])["details"]["run_id"] == report["run_id"]


def test_preflight_privacy_finding_blocks_before_data_fix_status(tmp_path: Path):
    client_dir = tmp_path / "cliente_test"
    write_valid_client(client_dir)
    (client_dir / "raw" / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario,email_cliente\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70,persona@example.com\n",
        encoding="utf-8",
    )

    report = run_preflight(client_dir)

    assert report["status"] == "privacy_review_required"
    assert report["privacy"]["safe_to_continue"] is False
