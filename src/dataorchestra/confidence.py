from __future__ import annotations

from collections import defaultdict
from typing import Any


def apply_alert_confidence(
    alerts: list[dict[str, Any]],
    sales_rows: list[dict[str, Any]],
    products: dict[str, dict[str, Any]],
    stock_rows: list[dict[str, Any]],
    data_quality: dict[str, Any],
) -> list[dict[str, Any]]:
    context = _build_context(sales_rows, products, stock_rows, data_quality)
    scored_alerts = []
    for alert in alerts:
        scored = dict(alert)
        scored["confidence"] = _confidence_for_alert(alert, context)
        scored_alerts.append(scored)
    return scored_alerts


def _build_context(
    sales_rows: list[dict[str, Any]],
    products: dict[str, dict[str, Any]],
    stock_rows: list[dict[str, Any]],
    data_quality: dict[str, Any],
) -> dict[str, Any]:
    sales_by_product: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sales_rows:
        sales_by_product[str(row.get("producto") or "")].append(row)

    return {
        "sales_rows": sales_rows,
        "sales_by_product": dict(sales_by_product),
        "products": products,
        "stock_by_product": {str(row.get("producto") or ""): row for row in stock_rows},
        "data_quality": data_quality or {},
        "sold_products": {str(row.get("producto") or "") for row in sales_rows if row.get("producto")},
    }


def _confidence_for_alert(alert: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    score, reasons, limitations = _base_from_quality(context["data_quality"])

    evidence = alert.get("evidence") or {}
    if evidence:
        score += 4
        reasons.append("La alerta conserva evidencia estructurada con metrica, valor y umbral.")
    else:
        score -= 22
        limitations.append("La alerta no conserva evidencia estructurada suficiente.")

    alert_type = alert.get("type")
    if alert_type == "Bajo margen":
        score = _score_low_margin(alert, context, score, reasons, limitations)
    elif alert_type in {"Stock bajo", "Exceso de stock"}:
        score = _score_stock_alert(alert, context, score, reasons, limitations)
    elif alert_type == "Concentracion":
        score = _score_concentration(alert, context, score, reasons, limitations)
    else:
        score -= 8
        limitations.append("Tipo de alerta sin regla especifica de confianza.")

    score = _clamp_score(_apply_confidence_caps(score, context["data_quality"], evidence, limitations))
    return {
        "level": _level(score),
        "score": score,
        "reasons": _dedupe(reasons)[:4],
        "limitations": _dedupe(limitations)[:4],
    }


def _base_from_quality(data_quality: dict[str, Any]) -> tuple[int, list[str], list[str]]:
    score = _as_int(data_quality.get("score"), 50)
    level = str(data_quality.get("level") or "sin_nivel")
    reasons = [f"Calidad general de datos: {score}/100 ({level})."]
    limitations: list[str] = []

    target = _as_int(data_quality.get("target_score"), 70)
    if score < target:
        limitations.append("El score de calidad esta por debajo del minimo objetivo para aprobar entrega sin correcciones.")

    row_counts = data_quality.get("row_counts") or {}
    sales_count = _as_int(row_counts.get("ventas"), 0)
    if sales_count and sales_count < 10:
        limitations.append("La muestra de ventas es reducida; conviene revisar representatividad antes de entregar.")

    return score, reasons, limitations


def _score_low_margin(
    alert: dict[str, Any],
    context: dict[str, Any],
    score: int,
    reasons: list[str],
    limitations: list[str],
) -> int:
    product = str(alert.get("item") or "")
    rows = context["sales_by_product"].get(product, [])
    catalog = context["products"].get(product)

    revenue = sum(_as_float(row.get("total_venta")) for row in rows)
    costs_available = any(_as_float(row.get("costo_unitario")) > 0 for row in rows)
    prices_available = any(_as_float(row.get("precio_unitario")) > 0 for row in rows)

    if rows:
        score += 5
        reasons.append(f"El producto tiene {len(rows)} fila(s) de venta asociadas.")
    else:
        score -= 18
        limitations.append("No se encontraron ventas asociadas al producto alertado.")

    if catalog:
        score += 5
        reasons.append("El producto alertado existe en productos.csv.")
    else:
        score -= 12
        limitations.append("El producto alertado no aparece en el catalogo de productos.")

    if revenue > 0 and costs_available and prices_available:
        score += 6
        reasons.append("El margen se apoya en ventas, precios y costos positivos.")
    else:
        score -= 18
        limitations.append("Faltan ventas, precios o costos positivos para respaldar plenamente el margen.")

    if 0 < len(rows) < 3:
        score -= 6
        limitations.append("La alerta de margen se basa en pocas operaciones del producto.")

    return score


def _score_stock_alert(
    alert: dict[str, Any],
    context: dict[str, Any],
    score: int,
    reasons: list[str],
    limitations: list[str],
) -> int:
    product = str(alert.get("item") or "")
    stock = context["stock_by_product"].get(product)

    if stock:
        score += 8
        reasons.append("El producto alertado existe en stock.csv.")
        current_stock = _as_float(stock.get("stock_actual"))
        minimum_stock = _as_float(stock.get("stock_minimo"))
        recent_sales = _as_float(stock.get("ventas_ultimos_30_dias"))
        if current_stock >= 0 and minimum_stock >= 0:
            score += 5
            reasons.append("La alerta se apoya en stock actual y stock minimo validos.")
        else:
            score -= 16
            limitations.append("El stock actual o minimo no es valido para interpretar la alerta.")
        if recent_sales > 0:
            score += 4
            reasons.append("stock.csv aporta ventas recientes para interpretar rotacion.")
        else:
            score -= 6
            limitations.append("No hay ventas recientes positivas para interpretar rotacion de stock.")
    else:
        score -= 24
        limitations.append("No se encontro el producto alertado en stock.csv.")

    if product in context["products"]:
        score += 3
        reasons.append("El producto tambien existe en productos.csv.")
    else:
        score -= 6
        limitations.append("El producto no aparece en productos.csv; revisar consistencia con catalogo.")

    return score


def _score_concentration(
    alert: dict[str, Any],
    context: dict[str, Any],
    score: int,
    reasons: list[str],
    limitations: list[str],
) -> int:
    rows = context["sales_rows"]
    sold_products = context["sold_products"]
    evidence = alert.get("evidence") or {}
    ratio = _as_float(evidence.get("value"))
    top_n = _as_int(evidence.get("top_n"), 0)
    total_revenue = sum(_as_float(row.get("total_venta")) for row in rows)

    if total_revenue > 0:
        score += 6
        reasons.append("La concentracion se calcula sobre facturacion positiva.")
    else:
        score -= 22
        limitations.append("No hay facturacion positiva suficiente para interpretar concentracion.")

    if len(rows) >= 10:
        score += 5
        reasons.append("La muestra de ventas tiene volumen minimo para interpretar concentracion.")
    else:
        score -= 8
        limitations.append("La muestra de ventas es chica para evaluar concentracion con alta seguridad.")

    if top_n and len(sold_products) <= top_n:
        score -= 8
        limitations.append("La cantidad de productos vendidos es menor o igual al top analizado; la concentracion puede ser esperable.")
    elif sold_products:
        score += 3
        reasons.append("Existen multiples productos vendidos para comparar peso relativo.")

    if ratio <= 0:
        score -= 12
        limitations.append("El ratio de concentracion informado no aporta una senal positiva.")

    return score


def _level(score: int) -> str:
    if score >= 80:
        return "alta"
    if score >= 60:
        return "media"
    return "baja"


def _apply_confidence_caps(score: int, data_quality: dict[str, Any], evidence: dict[str, Any], limitations: list[str]) -> int:
    capped_score = score
    quality_score = _as_int(data_quality.get("score"), 50)
    target = _as_int(data_quality.get("target_score"), 70)
    if not evidence:
        capped_score = min(capped_score, 55)
    if quality_score < target:
        capped_score = min(capped_score, 59)
    if len(limitations) >= 2:
        capped_score = min(capped_score, 79)
    return capped_score


def _clamp_score(score: int | float) -> int:
    return int(max(0, min(100, round(float(score)))))


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _dedupe(items: list[str]) -> list[str]:
    output = []
    seen = set()
    for item in items:
        if item not in seen:
            output.append(item)
            seen.add(item)
    return output
