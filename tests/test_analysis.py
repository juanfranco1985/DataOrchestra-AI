import json
from pathlib import Path

from dataorchestra.cli import run_analysis, run_preflight


def write_analysis_client(client_dir: Path) -> None:
    raw_dir = client_dir / "raw"
    raw_dir.mkdir(parents=True)
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_analysis\n",
        encoding="utf-8",
    )
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria 1,2,100,80\n"
        "2026-01-02,Producto B,Categoria 1,1,100,95\n"
        "2026-02-01,Producto C,Categoria 2,1,50,20\n",
        encoding="utf-8",
    )
    (raw_dir / "productos.csv").write_text(
        "producto,categoria,precio_unitario,costo_unitario\n"
        "Producto A,Categoria 1,100,80\n"
        "Producto B,Categoria 1,100,95\n"
        "Producto C,Categoria 2,50,20\n",
        encoding="utf-8",
    )
    (raw_dir / "stock.csv").write_text(
        "producto,stock_actual,stock_minimo,ventas_ultimos_30_dias\n"
        "Producto A,100,5,10\n"
        "Producto B,0,1,10\n"
        "Producto C,5,1,2\n",
        encoding="utf-8",
    )


def test_analysis_generates_metrics_alerts_recommendations_and_draft(tmp_path: Path):
    client_dir = tmp_path / "cliente_analysis"
    write_analysis_client(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"

    result = run_analysis(client_dir)

    assert result["status"] == "analysis_done"
    assert result["run_id"]
    assert result["preflight_run_id"]
    assert result["report_status"] == "pending_human_review"
    assert result["metrics"]["sales"]["ventas_totales"] == 350
    assert result["metrics"]["sales"]["costo_total"] == 275
    assert result["metrics"]["sales"]["margen_porcentaje"] == 0.2143
    assert result["metrics"]["stock"]["valor_stock_total"] == 8100
    assert result["metrics"]["stock"]["productos_stock_bajo"] == 1
    assert result["metrics"]["stock"]["productos_exceso"] == 1
    assert {alert["type"] for alert in result["alerts"]} == {
        "Bajo margen",
        "Concentracion",
        "Exceso de stock",
        "Stock bajo",
    }
    assert all(alert["evidence"] for alert in result["alerts"])
    assert all("evidence_alert_ids" in recommendation for recommendation in result["recommendations"])

    draft_path = client_dir / "reports" / "diagnostico_borrador.json"
    assert json.loads(draft_path.read_text(encoding="utf-8")) == result
    markdown_path = client_dir / "reports" / "diagnostico_borrador.md"
    markdown = markdown_path.read_text(encoding="utf-8")
    assert result["outputs"]["draft_markdown"] == str(markdown_path)
    html_path = client_dir / "reports" / "diagnostico_borrador.html"
    assert result["outputs"]["draft_html"] == str(html_path)
    assert "Diagnostico ejecutivo borrador" in html_path.read_text(encoding="utf-8")
    assert Path(result["outputs"]["archived"]["draft_markdown"]).exists()
    assert Path(result["outputs"]["archived"]["draft_html"]).exists()
    assert Path(result["outputs"]["archived"]["analysis_summary"]).exists()
    assert "**Estado:** pending_human_review" in markdown
    assert "no entregar al cliente sin revision humana" in markdown
    assert "## Alertas" in markdown
    assert "## Recomendaciones" in markdown
    assert "sha256" in markdown


def test_analysis_blocks_if_raw_files_changed_after_preflight(tmp_path: Path):
    client_dir = tmp_path / "cliente_analysis"
    write_analysis_client(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"
    (client_dir / "raw" / "stock.csv").write_text(
        "producto,stock_actual,stock_minimo,ventas_ultimos_30_dias\n"
        "Producto A,1,5,10\n",
        encoding="utf-8",
    )

    result = run_analysis(client_dir)

    assert result["status"] == "raw_files_changed_after_preflight"
    assert result["can_continue"] is False
    assert (client_dir / "diagnostics" / "analysis" / "analysis_blocked.json").exists()
