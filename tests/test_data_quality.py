from pathlib import Path

from dataorchestra.cli import run_data_quality
from dataorchestra.data_quality import assess_data_quality


def write_quality_client(client_dir: Path) -> None:
    raw_dir = client_dir / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70\n"
        "2026-01-04,Producto B,Categoria 1,2,80,40\n"
        "2026-01-08,Producto C,Categoria 2,1,120,60\n"
        "2026-01-12,Producto A,Categoria 1,3,100,70\n"
        "2026-01-16,Producto B,Categoria 1,1,80,40\n"
        "2026-01-20,Producto C,Categoria 2,2,120,60\n"
        "2026-01-24,Producto A,Categoria 1,1,100,70\n"
        "2026-01-28,Producto B,Categoria 1,2,80,40\n"
        "2026-02-01,Producto C,Categoria 2,1,120,60\n"
        "2026-02-05,Producto A,Categoria 1,1,100,70\n"
        "2026-02-08,Producto B,Categoria 1,1,80,40\n"
        "2026-02-10,Producto C,Categoria 2,1,120,60\n",
        encoding="utf-8",
    )
    (raw_dir / "productos.csv").write_text(
        "producto,categoria,precio_unitario,costo_unitario\n"
        "Producto A,Categoria 1,100,70\n"
        "Producto B,Categoria 1,80,40\n"
        "Producto C,Categoria 2,120,60\n",
        encoding="utf-8",
    )
    (raw_dir / "stock.csv").write_text(
        "producto,stock_actual,stock_minimo,ventas_ultimos_30_dias\n"
        "Producto A,10,2,8\n"
        "Producto B,8,2,7\n"
        "Producto C,6,2,5\n",
        encoding="utf-8",
    )


def test_data_quality_scores_clean_dataset_as_high_quality(tmp_path: Path):
    client_dir = tmp_path / "cliente_quality"
    write_quality_client(client_dir)

    result = assess_data_quality(client_dir)

    assert result["score"] == 100
    assert result["level"] == "alta"
    assert result["can_support_diagnostic"] is True
    assert result["findings"] == []
    assert result["coverage"]["sold_products_in_catalog_ratio"] == 1
    assert result["coverage"]["sold_products_in_stock_ratio"] == 1


def test_data_quality_cli_writes_report_and_audit_event(tmp_path: Path):
    client_dir = tmp_path / "cliente_quality"
    write_quality_client(client_dir)
    (client_dir / "client.yaml").write_text("client:\n  id: cliente_quality\n", encoding="utf-8")

    result = run_data_quality(client_dir)

    assert result["status"] == "data_quality_assessed"
    assert result["outputs"]["current_report"].endswith("data_quality_report.json")
    assert Path(result["outputs"]["archived_report"]).exists()
    assert (client_dir / "logs" / "audit.jsonl").read_text(encoding="utf-8").splitlines()


def test_data_quality_uses_configured_target_score(tmp_path: Path):
    client_dir = tmp_path / "cliente_quality"
    write_quality_client(client_dir)
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_quality\n"
        "data_quality:\n"
        "  target_score: 95\n",
        encoding="utf-8",
    )

    result = assess_data_quality(client_dir)

    assert result["target_score"] == 95
    assert result["can_support_diagnostic"] is True


def test_data_quality_penalizes_missing_coverage_zero_costs_and_duplicates(tmp_path: Path):
    client_dir = tmp_path / "cliente_quality"
    write_quality_client(client_dir)
    (client_dir / "raw" / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto X,Categoria 1,1,100,0\n"
        "2026-01-01,Producto X,Categoria 1,1,100,0\n"
        "2026-01-02,Producto A,Categoria 1,1,100,70\n",
        encoding="utf-8",
    )

    result = assess_data_quality(client_dir)
    finding_ids = {item["id"] for item in result["findings"]}

    assert result["score"] < 70
    assert result["can_support_diagnostic"] is False
    assert "sold_products_missing_from_catalog" in finding_ids
    assert "sold_products_missing_from_stock" in finding_ids
    assert "cost_values_zero" in finding_ids
    assert "duplicate_sales_rows" in finding_ids
