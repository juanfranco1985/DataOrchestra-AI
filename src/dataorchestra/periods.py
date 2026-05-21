from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Any


PERIOD_METRICS = ("ventas_totales", "margen_bruto", "margen_porcentaje", "unidades_vendidas", "tickets", "ticket_promedio")


def compare_sales_periods(sales_rows: list[dict[str, Any]]) -> dict[str, Any]:
    comparisons = [
        _compare_latest_months(sales_rows),
        _compare_rolling_30_days(sales_rows),
    ]
    available = [item for item in comparisons if item["status"] == "available"]
    return {
        "available": bool(available),
        "comparison_count": len(available),
        "comparisons": comparisons,
        "highlights": _build_highlights(available),
    }


def _compare_latest_months(rows: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        month = row.get("mes")
        if month:
            grouped[str(month)].append(row)

    months = sorted(grouped)
    if len(months) < 2:
        return _insufficient("latest_month_vs_previous_month", "Ultimo mes observado vs mes anterior observado", "Se necesitan al menos dos meses con ventas.")

    previous_month, current_month = months[-2], months[-1]
    return _comparison(
        "latest_month_vs_previous_month",
        "Ultimo mes observado vs mes anterior observado",
        _period_from_rows(current_month, grouped[current_month]),
        _period_from_rows(previous_month, grouped[previous_month]),
    )


def _compare_rolling_30_days(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dated_rows = [(parsed, row) for row in rows if (parsed := _parse_date(row.get("fecha")))]
    if not dated_rows:
        return _insufficient("rolling_30_days_vs_previous_30_days", "Ultimos 30 dias vs 30 dias previos", "No hay fechas validas para comparar ventanas moviles.")

    end_current = max(parsed for parsed, _row in dated_rows)
    start_current = end_current - timedelta(days=29)
    end_previous = start_current - timedelta(days=1)
    start_previous = end_previous - timedelta(days=29)
    current_rows = [row for parsed, row in dated_rows if start_current <= parsed <= end_current]
    previous_rows = [row for parsed, row in dated_rows if start_previous <= parsed <= end_previous]

    if not current_rows or not previous_rows:
        return _insufficient(
            "rolling_30_days_vs_previous_30_days",
            "Ultimos 30 dias vs 30 dias previos",
            "Se necesitan ventas en la ventana reciente y en la ventana previa.",
            {
                "current_period": _empty_period(str(start_current), start_current, end_current, len(current_rows)),
                "previous_period": _empty_period(str(start_previous), start_previous, end_previous, len(previous_rows)),
            },
        )

    return _comparison(
        "rolling_30_days_vs_previous_30_days",
        "Ultimos 30 dias vs 30 dias previos",
        _period_from_rows("ultimos_30_dias", current_rows, start_current, end_current),
        _period_from_rows("30_dias_previos", previous_rows, start_previous, end_previous),
    )


def _comparison(comparison_id: str, label: str, current_period: dict[str, Any], previous_period: dict[str, Any]) -> dict[str, Any]:
    metrics = {}
    for metric in PERIOD_METRICS:
        metrics[metric] = _metric_change(current_period["metrics"][metric], previous_period["metrics"][metric])

    return {
        "id": comparison_id,
        "label": label,
        "status": "available",
        "current_period": current_period,
        "previous_period": previous_period,
        "metrics": metrics,
        "summary": _summary(label, metrics),
    }


def _period_from_rows(label: str, rows: list[dict[str, Any]], start: date | None = None, end: date | None = None) -> dict[str, Any]:
    dates = [_parse_date(row.get("fecha")) for row in rows]
    valid_dates = [item for item in dates if item]
    period_start = start if start is not None else min(valid_dates) if valid_dates else None
    period_end = end if end is not None else max(valid_dates) if valid_dates else None
    metrics = _period_metrics(rows)
    return {
        "label": label,
        "start": period_start.isoformat() if period_start else None,
        "end": period_end.isoformat() if period_end else None,
        "row_count": len(rows),
        "metrics": metrics,
    }


def _empty_period(label: str, start: date, end: date, row_count: int) -> dict[str, Any]:
    return {
        "label": label,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "row_count": row_count,
    }


def _period_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_sales = sum(float(row.get("total_venta", 0)) for row in rows)
    total_cost = sum(float(row.get("total_costo", 0)) for row in rows)
    gross_margin = total_sales - total_cost
    units = sum(float(row.get("cantidad", 0)) for row in rows)
    tickets = len(rows)
    return {
        "ventas_totales": _round_money(total_sales),
        "costo_total": _round_money(total_cost),
        "margen_bruto": _round_money(gross_margin),
        "margen_porcentaje": _round_ratio(gross_margin / total_sales if total_sales else 0),
        "unidades_vendidas": _round_quantity(units),
        "tickets": tickets,
        "ticket_promedio": _round_money(total_sales / tickets if tickets else 0),
    }


def _metric_change(current: int | float, previous: int | float) -> dict[str, Any]:
    current_value = float(current)
    previous_value = float(previous)
    absolute = current_value - previous_value
    percent = None if previous_value == 0 else absolute / previous_value
    return {
        "current": _round_number(current_value),
        "previous": _round_number(previous_value),
        "absolute_change": _round_number(absolute),
        "percent_change": None if percent is None else _round_ratio(percent),
        "direction": _direction(absolute),
    }


def _build_highlights(comparisons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    highlights: list[dict[str, Any]] = []
    for comparison in comparisons:
        sales_change = comparison["metrics"]["ventas_totales"]
        margin_change = comparison["metrics"]["margen_porcentaje"]
        if sales_change["percent_change"] is not None and abs(sales_change["percent_change"]) >= 0.10:
            highlights.append(
                {
                    "id": f"{comparison['id']}_sales_change",
                    "comparison_id": comparison["id"],
                    "priority": "Media",
                    "type": "Cambio de ventas",
                    "description": f"Las ventas cambiaron {sales_change['percent_change']:.1%} frente al periodo comparable.",
                    "evidence": {"metric": "ventas_totales", **sales_change},
                }
            )
        if margin_change["absolute_change"] and abs(margin_change["absolute_change"]) >= 0.05:
            highlights.append(
                {
                    "id": f"{comparison['id']}_margin_rate_change",
                    "comparison_id": comparison["id"],
                    "priority": "Media",
                    "type": "Cambio de margen",
                    "description": f"El margen porcentual cambio {margin_change['absolute_change']:.1%} frente al periodo comparable.",
                    "evidence": {"metric": "margen_porcentaje", **margin_change},
                }
            )
    return highlights


def _summary(label: str, metrics: dict[str, dict[str, Any]]) -> str:
    sales = metrics["ventas_totales"]
    margin = metrics["margen_porcentaje"]
    sales_text = _change_text(sales, "ventas")
    margin_text = _change_text(margin, "margen porcentual")
    return f"{label}: {sales_text}; {margin_text}."


def _change_text(metric: dict[str, Any], label: str) -> str:
    if metric["percent_change"] is None:
        return f"{label} sin base previa comparable"
    return f"{label} {metric['percent_change']:.1%}"


def _insufficient(comparison_id: str, label: str, reason: str, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": comparison_id,
        "label": label,
        "status": "insufficient_data",
        "reason": reason,
        "evidence": evidence or {},
    }


def _parse_date(value: object) -> date | None:
    try:
        return date.fromisoformat(str(value or "").strip())
    except ValueError:
        return None


def _direction(value: float) -> str:
    if value > 0:
        return "up"
    if value < 0:
        return "down"
    return "flat"


def _round_money(value: float) -> float:
    return round(float(value), 2)


def _round_ratio(value: float) -> float:
    return round(float(value), 4)


def _round_quantity(value: float) -> int | float:
    number = float(value)
    return int(number) if number.is_integer() else round(number, 2)


def _round_number(value: float) -> int | float:
    number = float(value)
    if number.is_integer():
        return int(number)
    return round(number, 4)
