from dataorchestra.confidence import apply_alert_confidence


def test_confidence_marks_clean_low_margin_alert_as_high():
    alerts = [
        {
            "id": "alert_low_margin_1",
            "priority": "Alta",
            "type": "Bajo margen",
            "item": "Producto A",
            "description": "Margen estimado de 5.0%.",
            "suggested_action": "Revisar precio, costo o estrategia comercial.",
            "evidence": {"source": "ventas.csv", "metric": "margen_porcentaje", "value": 0.05, "threshold": 0.15},
        }
    ]
    sales_rows = [
        _sale("Producto A", 100, 95),
        _sale("Producto A", 120, 114),
        _sale("Producto A", 80, 76),
    ]
    products = {"Producto A": {"precio_unitario": 100, "costo_unitario": 95}}
    data_quality = {"score": 92, "level": "alta", "target_score": 70, "row_counts": {"ventas": 25}}

    scored = apply_alert_confidence(alerts, sales_rows, products, [], data_quality)

    confidence = scored[0]["confidence"]
    assert confidence["level"] == "alta"
    assert confidence["score"] >= 80
    assert confidence["reasons"]


def test_confidence_drops_when_stock_evidence_is_missing():
    alerts = [
        {
            "id": "alert_low_stock_1",
            "priority": "Alta",
            "type": "Stock bajo",
            "item": "Producto X",
            "description": "Stock actual 0 contra minimo 2.",
            "suggested_action": "Evaluar reposicion prioritaria.",
            "evidence": {"source": "stock.csv", "metric": "stock_actual_vs_minimo", "value": 0, "threshold": 2},
        }
    ]
    data_quality = {"score": 45, "level": "critica", "target_score": 70, "row_counts": {"ventas": 2}}

    scored = apply_alert_confidence(alerts, [], {}, [], data_quality)

    confidence = scored[0]["confidence"]
    assert confidence["level"] == "baja"
    assert confidence["score"] < 60
    assert confidence["limitations"]


def _sale(product: str, price: float, cost: float) -> dict:
    return {
        "producto": product,
        "precio_unitario": price,
        "costo_unitario": cost,
        "total_venta": price,
        "total_costo": cost,
        "margen_bruto": price - cost,
    }
