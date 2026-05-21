from __future__ import annotations

from collections import defaultdict
import csv
import json
from pathlib import Path
from typing import Any

from dataorchestra.data_quality import assess_data_quality
from dataorchestra.integrity import fingerprint_files
from dataorchestra.periods import compare_sales_periods
from dataorchestra.reporting import render_html_report, render_markdown_report
from dataorchestra.runs import archive_file, new_run_id, run_stage_dir
from dataorchestra.states import DiagnosticStatus
from dataorchestra.thresholds import resolve_thresholds
from dataorchestra.validation import normalize_name


def run_client_analysis(client_dir: str | Path, thresholds: dict[str, float] | None = None) -> dict:
    client_path = Path(client_dir)
    run_id = new_run_id()
    diagnostics_dir = client_path / "diagnostics" / "analysis"
    reports_dir = client_path / "reports"
    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    threshold_config = resolve_thresholds(client_path, runtime_overrides=thresholds)
    active_thresholds = threshold_config["thresholds"]
    gate = _check_preflight_gate(client_path)
    if not gate["can_continue"]:
        result = {
            "client_id": gate["client_id"],
            "status": gate["status"],
            "can_continue": False,
            "reason": gate["reason"],
            "preflight_report": gate.get("preflight_report"),
        }
        _write_json(diagnostics_dir / "analysis_blocked.json", result)
        return result

    raw_dir = client_path / "raw"
    sales_rows = _load_sales(raw_dir / "ventas.csv")
    products = _load_products(raw_dir / "productos.csv")
    stock_rows = _load_stock(raw_dir / "stock.csv", products)

    sales_metrics = _sales_metrics(sales_rows)
    product_metrics = _product_metrics(sales_rows)
    category_metrics = _category_metrics(sales_rows)
    monthly_metrics = _monthly_metrics(sales_rows)
    stock_metrics, low_stock, excess_stock = _stock_metrics(stock_rows, active_thresholds)
    concentration = _revenue_concentration(product_metrics, active_thresholds)
    low_margin = _low_margin_products(product_metrics, active_thresholds)
    data_quality = assess_data_quality(client_path)
    period_comparison = compare_sales_periods(sales_rows)

    metrics = {
        "sales": sales_metrics,
        "profitability": {
            "costo_total": _round_money(sales_metrics["costo_total"]),
            "margen_bruto": _round_money(sales_metrics["margen_bruto"]),
            "margen_porcentaje": _round_ratio(sales_metrics["margen_porcentaje"]),
        },
        "stock": stock_metrics,
        "concentration": concentration,
        "top_products_by_revenue": product_metrics[:10],
        "sales_by_category": category_metrics,
        "sales_by_month": monthly_metrics,
        "period_comparison": {
            "available": period_comparison["available"],
            "comparison_count": period_comparison["comparison_count"],
        },
        "data_quality": {
            "score": data_quality["score"],
            "level": data_quality["level"],
            "can_support_diagnostic": data_quality["can_support_diagnostic"],
        },
    }
    alerts = _build_alerts(concentration, low_margin, low_stock, excess_stock, active_thresholds)
    recommendations = _build_recommendations(alerts)
    raw_fingerprints = fingerprint_files(raw_dir.glob("*.csv"))
    draft_json_path = reports_dir / "diagnostico_borrador.json"
    draft_markdown_path = reports_dir / "diagnostico_borrador.md"
    draft_html_path = reports_dir / "diagnostico_borrador.html"
    metrics_path = diagnostics_dir / "metrics_summary.json"
    alerts_path = diagnostics_dir / "alerts.json"
    recommendations_path = diagnostics_dir / "recommendations.json"
    data_quality_path = diagnostics_dir / "data_quality.json"
    period_comparison_path = diagnostics_dir / "period_comparison.json"
    threshold_config_path = diagnostics_dir / "threshold_config.json"
    analysis_summary_path = diagnostics_dir / "analysis_summary.json"
    archive_dir = run_stage_dir(client_path, run_id, "analysis")

    result = {
        "client_id": gate["client_id"],
        "run_id": run_id,
        "preflight_run_id": gate.get("preflight_run_id"),
        "status": DiagnosticStatus.ANALYSIS_DONE.value,
        "report_status": DiagnosticStatus.PENDING_HUMAN_REVIEW.value,
        "can_continue": True,
        "metrics": metrics,
        "data_quality": data_quality,
        "period_comparison": period_comparison,
        "threshold_config": threshold_config,
        "alerts": alerts,
        "recommendations": recommendations,
        "evidence": {
            "preflight_report": gate["preflight_report"],
            "raw_fingerprints": raw_fingerprints,
            "thresholds": active_thresholds,
            "threshold_profile": threshold_config["profile"],
        },
        "outputs": {
            "draft_json": str(draft_json_path),
            "draft_markdown": str(draft_markdown_path),
            "draft_html": str(draft_html_path),
            "data_quality": str(data_quality_path),
            "period_comparison": str(period_comparison_path),
            "threshold_config": str(threshold_config_path),
            "analysis_summary": str(analysis_summary_path),
            "archive_dir": str(archive_dir),
            "archived": {
                "metrics_summary": str(archive_dir / metrics_path.name),
                "alerts": str(archive_dir / alerts_path.name),
                "recommendations": str(archive_dir / recommendations_path.name),
                "data_quality": str(archive_dir / data_quality_path.name),
                "period_comparison": str(archive_dir / period_comparison_path.name),
                "threshold_config": str(archive_dir / threshold_config_path.name),
                "analysis_summary": str(archive_dir / analysis_summary_path.name),
                "draft_json": str(archive_dir / draft_json_path.name),
                "draft_markdown": str(archive_dir / draft_markdown_path.name),
                "draft_html": str(archive_dir / draft_html_path.name),
            },
        },
    }
    _write_json(metrics_path, metrics)
    _write_json(alerts_path, alerts)
    _write_json(recommendations_path, recommendations)
    _write_json(data_quality_path, data_quality)
    _write_json(period_comparison_path, period_comparison)
    _write_json(threshold_config_path, threshold_config)
    _write_json(analysis_summary_path, result)
    _write_json(draft_json_path, result)
    draft_markdown_path.write_text(render_markdown_report(result), encoding="utf-8")
    draft_html_path.write_text(render_html_report(result), encoding="utf-8")
    for path in (
        metrics_path,
        alerts_path,
        recommendations_path,
        data_quality_path,
        period_comparison_path,
        threshold_config_path,
        analysis_summary_path,
        draft_json_path,
        draft_markdown_path,
        draft_html_path,
    ):
        archive_file(client_path, run_id, "analysis", path)
    return result


def _check_preflight_gate(client_path: Path) -> dict:
    report_path = client_path / "diagnostics" / "preflight" / "preflight_report.json"
    if not report_path.exists():
        return {
            "client_id": _read_client_id_from_config(client_path),
            "status": "preflight_required",
            "can_continue": False,
            "reason": "No preflight report found.",
        }

    report = json.loads(report_path.read_text(encoding="utf-8"))
    client_id = str(report.get("client_id") or _read_client_id_from_config(client_path))
    if report.get("status") != DiagnosticStatus.READY_FOR_ANALYSIS.value:
        return {
            "client_id": client_id,
            "status": "preflight_not_ready",
            "can_continue": False,
            "reason": f"Preflight status is {report.get('status')}.",
            "preflight_report": str(report_path),
        }

    expected = report.get("raw_files", {}).get("fingerprints", [])
    current = fingerprint_files((client_path / "raw").glob("*.csv"))
    if expected != current:
        return {
            "client_id": client_id,
            "status": "raw_files_changed_after_preflight",
            "can_continue": False,
            "reason": "Raw CSV fingerprints differ from the approved preflight report.",
            "preflight_report": str(report_path),
        }

    return {
        "client_id": client_id,
        "preflight_run_id": report.get("run_id"),
        "status": DiagnosticStatus.READY_FOR_ANALYSIS.value,
        "can_continue": True,
        "reason": "",
        "preflight_report": str(report_path),
    }


def _load_sales(path: Path) -> list[dict]:
    rows = []
    for row in _read_csv(path):
        quantity = _number(row["cantidad"])
        unit_price = _number(row["precio_unitario"])
        unit_cost = _number(row["costo_unitario"])
        total_sale = quantity * unit_price
        total_cost = quantity * unit_cost
        rows.append(
            {
                "fecha": row["fecha"],
                "mes": row["fecha"][:7],
                "producto": row["producto"],
                "categoria": row["categoria"],
                "cantidad": quantity,
                "precio_unitario": unit_price,
                "costo_unitario": unit_cost,
                "total_venta": total_sale,
                "total_costo": total_cost,
                "margen_bruto": total_sale - total_cost,
            }
        )
    return rows


def _load_products(path: Path) -> dict[str, dict]:
    products = {}
    for row in _read_csv(path):
        products[row["producto"]] = {
            "categoria": row.get("categoria", ""),
            "precio_unitario": _number(row.get("precio_unitario", 0)),
            "costo_unitario": _number(row.get("costo_unitario", 0)),
        }
    return products


def _load_stock(path: Path, products: dict[str, dict]) -> list[dict]:
    rows = []
    for row in _read_csv(path):
        product = row["producto"]
        stock = _number(row["stock_actual"])
        recent_sales = _number(row["ventas_ultimos_30_dias"])
        unit_cost = _number(row.get("costo_unitario") or products.get(product, {}).get("costo_unitario", 0))
        rows.append(
            {
                "producto": product,
                "stock_actual": stock,
                "stock_minimo": _number(row["stock_minimo"]),
                "ventas_ultimos_30_dias": recent_sales,
                "valor_stock": stock * unit_cost,
                "rotacion": recent_sales / stock if stock else 0,
            }
        )
    return rows


def _sales_metrics(rows: list[dict]) -> dict:
    total_sales = sum(row["total_venta"] for row in rows)
    total_cost = sum(row["total_costo"] for row in rows)
    gross_margin = total_sales - total_cost
    dates = sorted(row["fecha"] for row in rows if row.get("fecha"))
    tickets = len(rows)
    return {
        "ventas_totales": _round_money(total_sales),
        "costo_total": _round_money(total_cost),
        "margen_bruto": _round_money(gross_margin),
        "margen_porcentaje": _round_ratio(gross_margin / total_sales if total_sales else 0),
        "unidades_vendidas": _round_quantity(sum(row["cantidad"] for row in rows)),
        "tickets": tickets,
        "ticket_promedio": _round_money(total_sales / tickets if tickets else 0),
        "periodo_inicio": dates[0] if dates else None,
        "periodo_fin": dates[-1] if dates else None,
    }


def _product_metrics(rows: list[dict]) -> list[dict]:
    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: {"producto": "", "facturacion": 0, "costo": 0, "margen": 0, "unidades": 0})
    for row in rows:
        product = row["producto"]
        item = grouped[product]
        item["producto"] = product
        item["facturacion"] += row["total_venta"]
        item["costo"] += row["total_costo"]
        item["margen"] += row["margen_bruto"]
        item["unidades"] += row["cantidad"]

    metrics = []
    for item in grouped.values():
        revenue = item["facturacion"]
        metrics.append(
            {
                "producto": item["producto"],
                "facturacion": _round_money(revenue),
                "costo": _round_money(item["costo"]),
                "margen": _round_money(item["margen"]),
                "margen_porcentaje": _round_ratio(item["margen"] / revenue if revenue else 0),
                "unidades": _round_quantity(item["unidades"]),
            }
        )
    return sorted(metrics, key=lambda item: item["facturacion"], reverse=True)


def _category_metrics(rows: list[dict]) -> list[dict]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row["categoria"]] += row["total_venta"]
    return [{"categoria": key, "facturacion": _round_money(value)} for key, value in sorted(grouped.items(), key=lambda item: item[1], reverse=True)]


def _monthly_metrics(rows: list[dict]) -> list[dict]:
    grouped: dict[str, float] = defaultdict(float)
    for row in rows:
        grouped[row["mes"]] += row["total_venta"]
    return [{"mes": key, "facturacion": _round_money(value)} for key, value in sorted(grouped.items())]


def _stock_metrics(rows: list[dict], thresholds: dict[str, float]) -> tuple[dict, list[dict], list[dict]]:
    low_stock = [row for row in rows if row["stock_actual"] < row["stock_minimo"]]
    excess_stock = [row for row in rows if row["stock_actual"] > row["ventas_ultimos_30_dias"] * thresholds["excess_stock_ratio"]]
    low_stock = sorted(low_stock, key=lambda item: item["ventas_ultimos_30_dias"], reverse=True)
    excess_stock = sorted(excess_stock, key=lambda item: item["valor_stock"], reverse=True)
    metrics = {
        "valor_stock_total": _round_money(sum(row["valor_stock"] for row in rows)),
        "productos_stock_bajo": len(low_stock),
        "productos_exceso": len(excess_stock),
    }
    return metrics, [_format_stock_item(row) for row in low_stock], [_format_stock_item(row) for row in excess_stock]


def _revenue_concentration(product_metrics: list[dict], thresholds: dict[str, float]) -> dict:
    top_n = int(thresholds["revenue_concentration_top_n"])
    total = sum(item["facturacion"] for item in product_metrics)
    top_total = sum(item["facturacion"] for item in product_metrics[:top_n])
    return {
        "top_n": top_n,
        "ratio": _round_ratio(top_total / total if total else 0),
        "facturacion_top_n": _round_money(top_total),
        "facturacion_total": _round_money(total),
    }


def _low_margin_products(product_metrics: list[dict], thresholds: dict[str, float]) -> list[dict]:
    return [item for item in product_metrics if item["margen_porcentaje"] < thresholds["low_margin"]]


def _build_alerts(concentration: dict, low_margin: list[dict], low_stock: list[dict], excess_stock: list[dict], thresholds: dict[str, float]) -> list[dict]:
    alerts = []
    if concentration["ratio"] > thresholds["revenue_concentration_warning"]:
        alerts.append(
            {
                "id": "alert_concentration_top_products",
                "priority": "Media",
                "type": "Concentracion",
                "item": "Top productos",
                "description": f"Los principales productos concentran {concentration['ratio']:.1%} de la facturacion.",
                "suggested_action": "Monitorear stock, precio y costo de productos criticos.",
                "evidence": {"metric": "concentration.ratio", "value": concentration["ratio"], "threshold": thresholds["revenue_concentration_warning"]},
            }
        )

    for index, item in enumerate(low_margin[:5], start=1):
        alerts.append(
            {
                "id": f"alert_low_margin_{index}",
                "priority": "Alta" if item["margen_porcentaje"] < thresholds["critical_margin"] else "Media",
                "type": "Bajo margen",
                "item": item["producto"],
                "description": f"Margen estimado de {item['margen_porcentaje']:.1%}.",
                "suggested_action": "Revisar precio, costo o estrategia comercial.",
                "evidence": {"metric": "margen_porcentaje", "value": item["margen_porcentaje"], "threshold": thresholds["low_margin"], "source": "ventas.csv"},
            }
        )

    for index, item in enumerate(low_stock[:5], start=1):
        alerts.append(
            {
                "id": f"alert_low_stock_{index}",
                "priority": "Alta",
                "type": "Stock bajo",
                "item": item["producto"],
                "description": f"Stock actual {item['stock_actual']} contra minimo {item['stock_minimo']}.",
                "suggested_action": "Evaluar reposicion prioritaria.",
                "evidence": {"metric": "stock_actual_vs_minimo", "value": item["stock_actual"], "threshold": item["stock_minimo"], "source": "stock.csv"},
            }
        )

    for index, item in enumerate(excess_stock[:5], start=1):
        alerts.append(
            {
                "id": f"alert_excess_stock_{index}",
                "priority": "Media",
                "type": "Exceso de stock",
                "item": item["producto"],
                "description": f"Stock actual {item['stock_actual']} con rotacion baja.",
                "suggested_action": "Evaluar promocion o reduccion de compras.",
                "evidence": {"metric": "stock_vs_ventas_30_dias", "value": item["stock_actual"], "threshold": item["ventas_ultimos_30_dias"] * thresholds["excess_stock_ratio"], "source": "stock.csv"},
            }
        )
    return alerts


def _build_recommendations(alerts: list[dict]) -> list[dict]:
    rules = {
        "Bajo margen": ("Alta", "Revisar productos de bajo margen", "Evaluar ajuste de precios, negociacion de costos o combos con productos de mayor rentabilidad."),
        "Stock bajo": ("Alta", "Reponer productos criticos", "Priorizar productos con alta rotacion y stock bajo para evitar perdida de ventas."),
        "Exceso de stock": ("Media", "Reducir capital inmovilizado", "Crear promociones o ajustar compras de productos con stock alto y baja rotacion."),
        "Concentracion": ("Media", "Monitorear productos que sostienen la facturacion", "Revisar semanalmente precio, costo y stock de los productos criticos."),
    }
    recommendations = []
    for alert_type, (priority, title, detail) in rules.items():
        evidence_ids = [alert["id"] for alert in alerts if alert["type"] == alert_type]
        if evidence_ids:
            recommendations.append(
                {
                    "id": f"rec_{alert_type.lower().replace(' ', '_')}",
                    "priority": priority,
                    "title": title,
                    "detail": detail,
                    "evidence_alert_ids": evidence_ids,
                }
            )
    if not recommendations:
        recommendations.append(
            {
                "id": "rec_continue_monitoring",
                "priority": "Media",
                "title": "Continuar monitoreo mensual",
                "detail": "Repetir el analisis para detectar tendencias y medir el impacto de decisiones.",
                "evidence_alert_ids": [],
            }
        )
    return recommendations


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{normalize_name(key): str(value or "").strip() for key, value in row.items()} for row in reader]


def _read_client_id_from_config(client_path: Path) -> str:
    config_path = client_path / "client.yaml"
    if not config_path.exists():
        return client_path.name
    for line in config_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("id:"):
            return line.split(":", 1)[1].strip().strip('"')
    return client_path.name


def _format_stock_item(row: dict) -> dict:
    return {
        "producto": row["producto"],
        "stock_actual": _round_quantity(row["stock_actual"]),
        "stock_minimo": _round_quantity(row["stock_minimo"]),
        "ventas_ultimos_30_dias": _round_quantity(row["ventas_ultimos_30_dias"]),
        "valor_stock": _round_money(row["valor_stock"]),
        "rotacion": _round_ratio(row["rotacion"]),
    }


def _number(value: Any) -> float:
    text = str(value or "").strip().replace(",", ".")
    return float(text) if text else 0.0


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_ratio(value: float) -> float:
    return round(float(value), 4)


def _round_quantity(value: float) -> int | float:
    number = float(value)
    return int(number) if number.is_integer() else round(number, 2)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
