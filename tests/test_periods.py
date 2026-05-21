from dataorchestra.periods import compare_sales_periods


def test_compare_sales_periods_returns_monthly_and_rolling_comparisons():
    rows = [
        _sale("2026-01-01", 50, 30, 1),
        _sale("2026-01-15", 50, 30, 1),
        _sale("2026-02-01", 120, 60, 1),
        _sale("2026-02-15", 180, 90, 1),
    ]

    result = compare_sales_periods(rows)
    monthly = next(item for item in result["comparisons"] if item["id"] == "latest_month_vs_previous_month")
    rolling = next(item for item in result["comparisons"] if item["id"] == "rolling_30_days_vs_previous_30_days")

    assert result["available"] is True
    assert result["comparison_count"] == 2
    assert monthly["status"] == "available"
    assert monthly["current_period"]["label"] == "2026-02"
    assert monthly["previous_period"]["label"] == "2026-01"
    assert monthly["metrics"]["ventas_totales"]["current"] == 300
    assert monthly["metrics"]["ventas_totales"]["previous"] == 100
    assert monthly["metrics"]["ventas_totales"]["percent_change"] == 2
    assert rolling["status"] == "available"
    assert result["highlights"]


def test_compare_sales_periods_reports_insufficient_data():
    result = compare_sales_periods([_sale("2026-01-01", 100, 70, 1)])

    assert result["available"] is False
    assert all(item["status"] == "insufficient_data" for item in result["comparisons"])


def _sale(fecha: str, total_sale: float, total_cost: float, quantity: float) -> dict:
    return {
        "fecha": fecha,
        "mes": fecha[:7],
        "producto": "Producto A",
        "categoria": "Categoria 1",
        "cantidad": quantity,
        "precio_unitario": total_sale / quantity,
        "costo_unitario": total_cost / quantity,
        "total_venta": total_sale,
        "total_costo": total_cost,
        "margen_bruto": total_sale - total_cost,
    }
