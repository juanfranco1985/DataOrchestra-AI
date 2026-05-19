from dataorchestra.reporting import render_html_report, render_markdown_report


def test_markdown_report_keeps_delivery_block_and_evidence_visible():
    report = render_markdown_report(_sample_analysis())

    assert "pending_human_review" in report
    assert "no entregar al cliente sin revision humana" in report
    assert "alert_low_stock_1" in report
    assert "sha256 `abc123`" in report


def test_html_report_is_print_ready_and_escapes_content():
    analysis = _sample_analysis()
    analysis["client_id"] = "cliente_<test>"
    report = render_html_report(analysis)

    assert "<!doctype html>" in report
    assert "Diagnostico ejecutivo borrador" in report
    assert "pending_human_review" in report
    assert "cliente_&lt;test&gt;" in report
    assert "sha256 abc123" in report
    assert "@media print" in report


def _sample_analysis() -> dict:
    return {
            "client_id": "cliente_test",
            "metrics": {
                "sales": {
                    "periodo_inicio": "2026-01-01",
                    "periodo_fin": "2026-01-31",
                    "ventas_totales": 1000,
                    "unidades_vendidas": 10,
                    "ticket_promedio": 100,
                },
                "profitability": {"margen_bruto": 250, "margen_porcentaje": 0.25},
                "stock": {"valor_stock_total": 500, "productos_stock_bajo": 1, "productos_exceso": 0},
                "concentration": {"top_n": 5, "ratio": 0.75},
            },
            "alerts": [
                {
                    "id": "alert_low_stock_1",
                    "priority": "Alta",
                    "type": "Stock bajo",
                    "item": "Producto A",
                    "description": "Stock actual 0 contra minimo 2.",
                    "suggested_action": "Evaluar reposicion prioritaria.",
                    "evidence": {"source": "stock.csv", "metric": "stock_actual_vs_minimo", "value": 0, "threshold": 2},
                }
            ],
            "recommendations": [
                {
                    "priority": "Alta",
                    "title": "Reponer productos criticos",
                    "detail": "Priorizar productos con alta rotacion.",
                    "evidence_alert_ids": ["alert_low_stock_1"],
                }
            ],
            "evidence": {
                "preflight_report": "diagnostics/preflight/preflight_report.json",
                "raw_fingerprints": [{"name": "stock.csv", "sha256": "abc123", "size_bytes": 10}],
            },
        }
