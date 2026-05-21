from __future__ import annotations

from collections import Counter
import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any

import yaml

from dataorchestra.audit import now_iso
from dataorchestra.validation import normalize_name


EXPECTED_FILES = ("ventas.csv", "productos.csv", "stock.csv")
QUALITY_TARGET_SCORE = 70


def assess_data_quality(client_dir: str | Path) -> dict[str, Any]:
    client_path = Path(client_dir)
    raw_dir = client_path / "raw"
    target_score = _quality_target_score(client_path)
    sales_rows = _read_csv(raw_dir / "ventas.csv")
    product_rows = _read_csv(raw_dir / "productos.csv")
    stock_rows = _read_csv(raw_dir / "stock.csv")

    findings: list[dict[str, Any]] = []
    _check_missing_files(raw_dir, findings)
    _check_sales_volume_and_period(sales_rows, findings)
    _check_dataset_coverage(sales_rows, product_rows, stock_rows, findings)
    _check_zero_values(sales_rows, product_rows, stock_rows, findings)
    _check_duplicate_sales(sales_rows, findings)
    _check_catalog_consistency(sales_rows, product_rows, findings)

    score = max(0, min(100, 100 - sum(int(item["penalty"]) for item in findings)))
    level = _quality_level(score)
    row_counts = {
        "ventas": len(sales_rows),
        "productos": len(product_rows),
        "stock": len(stock_rows),
    }

    return {
        "generated_at": now_iso(),
        "score": score,
        "level": level,
        "target_score": target_score,
        "can_support_diagnostic": score >= target_score,
        "summary": _summary(score, level, findings),
        "row_counts": row_counts,
        "coverage": _coverage_summary(sales_rows, product_rows, stock_rows),
        "findings": findings,
        "recommended_action": _recommended_action(score, findings, target_score),
    }


def _check_missing_files(raw_dir: Path, findings: list[dict[str, Any]]) -> None:
    missing = [name for name in EXPECTED_FILES if not (raw_dir / name).exists()]
    if missing:
        findings.append(_finding("missing_required_files", "high", 40, "Faltan archivos obligatorios.", {"missing_count": len(missing)}))


def _check_sales_volume_and_period(sales_rows: list[dict[str, str]], findings: list[dict[str, Any]]) -> None:
    count = len(sales_rows)
    if count == 0:
        findings.append(_finding("sales_empty", "high", 35, "ventas.csv no contiene operaciones.", {"sales_rows": count}))
        return
    if count < 10:
        findings.append(_finding("sales_low_row_count", "medium", 8, "La muestra de ventas es chica; los hallazgos pueden ser menos representativos.", {"sales_rows": count}))

    parsed_dates = [_parse_date(row.get("fecha", "")) for row in sales_rows]
    valid_dates = [item for item in parsed_dates if item is not None]
    if not valid_dates:
        findings.append(_finding("sales_dates_unavailable", "high", 15, "No hay fechas validas para estimar periodo.", {"valid_dates": 0}))
        return
    period_days = (max(valid_dates) - min(valid_dates)).days + 1
    if period_days < 14:
        findings.append(_finding("short_analysis_period", "medium", 8, "El periodo analizado es corto para detectar patrones comerciales.", {"period_days": period_days}))


def _check_dataset_coverage(sales_rows: list[dict[str, str]], product_rows: list[dict[str, str]], stock_rows: list[dict[str, str]], findings: list[dict[str, Any]]) -> None:
    sales_products = _product_set(sales_rows)
    catalog_products = _product_set(product_rows)
    stock_products = _product_set(stock_rows)

    sold_without_catalog = sales_products - catalog_products
    sold_without_stock = sales_products - stock_products
    stock_without_catalog = stock_products - catalog_products

    if sold_without_catalog:
        findings.append(
            _finding(
                "sold_products_missing_from_catalog",
                "high",
                18,
                "Hay productos vendidos que no aparecen en productos.csv.",
                {"count": len(sold_without_catalog), "sold_products": len(sales_products), "catalog_products": len(catalog_products)},
            )
        )
    if sold_without_stock:
        findings.append(
            _finding(
                "sold_products_missing_from_stock",
                "medium",
                10,
                "Hay productos vendidos que no aparecen en stock.csv.",
                {"count": len(sold_without_stock), "sold_products": len(sales_products), "stock_products": len(stock_products)},
            )
        )
    if stock_without_catalog:
        findings.append(
            _finding(
                "stock_products_missing_from_catalog",
                "medium",
                6,
                "Hay productos en stock.csv que no aparecen en productos.csv.",
                {"count": len(stock_without_catalog), "stock_products": len(stock_products), "catalog_products": len(catalog_products)},
            )
        )


def _check_zero_values(sales_rows: list[dict[str, str]], product_rows: list[dict[str, str]], stock_rows: list[dict[str, str]], findings: list[dict[str, Any]]) -> None:
    sales_zero_quantity = sum(1 for row in sales_rows if _number(row.get("cantidad")) == 0)
    sales_zero_price = sum(1 for row in sales_rows if _number(row.get("precio_unitario")) == 0)
    sales_zero_cost = sum(1 for row in sales_rows if _number(row.get("costo_unitario")) == 0)
    catalog_zero_cost = sum(1 for row in product_rows if _number(row.get("costo_unitario")) == 0)
    stock_without_rotation = sum(1 for row in stock_rows if _number(row.get("ventas_ultimos_30_dias")) == 0)

    if sales_zero_quantity or sales_zero_price:
        findings.append(
            _finding(
                "sales_zero_commercial_values",
                "high",
                15,
                "Hay ventas con cantidad o precio igual a cero.",
                {"zero_quantity_rows": sales_zero_quantity, "zero_price_rows": sales_zero_price},
            )
        )
    if sales_zero_cost or catalog_zero_cost:
        findings.append(
            _finding(
                "cost_values_zero",
                "medium",
                10,
                "Hay costos en cero; el margen puede estar sobreestimado.",
                {"sales_zero_cost_rows": sales_zero_cost, "catalog_zero_cost_rows": catalog_zero_cost},
            )
        )
    if stock_rows and stock_without_rotation == len(stock_rows):
        findings.append(
            _finding(
                "stock_rotation_unavailable",
                "medium",
                8,
                "stock.csv no aporta ventas_ultimos_30_dias utiles para estimar rotacion.",
                {"stock_rows": len(stock_rows), "zero_rotation_rows": stock_without_rotation},
            )
        )


def _check_duplicate_sales(sales_rows: list[dict[str, str]], findings: list[dict[str, Any]]) -> None:
    if not sales_rows:
        return
    row_keys = [json.dumps(row, sort_keys=True, ensure_ascii=False) for row in sales_rows]
    duplicated_rows = sum(count - 1 for count in Counter(row_keys).values() if count > 1)
    duplicate_ratio = duplicated_rows / len(sales_rows)
    if duplicate_ratio > 0.05:
        findings.append(
            _finding(
                "duplicate_sales_rows",
                "medium",
                7,
                "Hay filas de ventas repetidas que podrian duplicar facturacion.",
                {"duplicated_rows": duplicated_rows, "sales_rows": len(sales_rows), "duplicate_ratio": round(duplicate_ratio, 4)},
            )
        )


def _check_catalog_consistency(sales_rows: list[dict[str, str]], product_rows: list[dict[str, str]], findings: list[dict[str, Any]]) -> None:
    if not sales_rows or not product_rows:
        return
    catalog = {row.get("producto", ""): row for row in product_rows if row.get("producto")}
    checked = 0
    cost_mismatches = 0
    for row in sales_rows:
        product = row.get("producto", "")
        if product not in catalog:
            continue
        checked += 1
        sale_cost = _number(row.get("costo_unitario"))
        catalog_cost = _number(catalog[product].get("costo_unitario"))
        if catalog_cost and abs(sale_cost - catalog_cost) / catalog_cost > 0.05:
            cost_mismatches += 1
    if checked and cost_mismatches / checked > 0.25:
        findings.append(
            _finding(
                "catalog_cost_mismatch",
                "medium",
                6,
                "Los costos de ventas.csv difieren del catalogo en una parte relevante de las filas.",
                {"checked_rows": checked, "mismatch_rows": cost_mismatches, "mismatch_ratio": round(cost_mismatches / checked, 4)},
            )
        )


def _coverage_summary(sales_rows: list[dict[str, str]], product_rows: list[dict[str, str]], stock_rows: list[dict[str, str]]) -> dict[str, Any]:
    sales_products = _product_set(sales_rows)
    catalog_products = _product_set(product_rows)
    stock_products = _product_set(stock_rows)
    return {
        "sold_products": len(sales_products),
        "catalog_products": len(catalog_products),
        "stock_products": len(stock_products),
        "sold_products_in_catalog_ratio": _ratio(len(sales_products & catalog_products), len(sales_products)),
        "sold_products_in_stock_ratio": _ratio(len(sales_products & stock_products), len(sales_products)),
    }


def _summary(score: int, level: str, findings: list[dict[str, Any]]) -> str:
    if not findings:
        return f"Calidad {level}: los archivos no presentan observaciones relevantes para el diagnostico."
    return f"Calidad {level}: score {score}/100 con {len(findings)} observacion(es) que deben considerarse al interpretar el informe."


def _recommended_action(score: int, findings: list[dict[str, Any]], target_score: int) -> str:
    if score >= 85:
        return "Continuar con analisis y revision humana normal."
    if score >= target_score:
        return "Continuar, dejando visibles las observaciones de calidad en la revision humana."
    high_findings = [item for item in findings if item["severity"] == "high"]
    if high_findings:
        return "Pedir correccion de datos antes de usar el diagnostico comercial como entregable."
    return "Revisar calidad con el cliente antes de aprobar entrega."


def _quality_level(score: int) -> str:
    if score >= 85:
        return "alta"
    if score >= 70:
        return "media"
    if score >= 50:
        return "baja"
    return "critica"


def _finding(finding_id: str, severity: str, penalty: int, message: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": finding_id,
        "severity": severity,
        "penalty": penalty,
        "message": message,
        "evidence": evidence,
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{normalize_name(key): str(value or "").strip() for key, value in row.items()} for row in reader]


def _quality_target_score(client_path: Path) -> int:
    config_path = client_path / "client.yaml"
    if not config_path.exists():
        return QUALITY_TARGET_SCORE
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    data_quality = config.get("data_quality", {}) if isinstance(config.get("data_quality"), dict) else {}
    try:
        score = int(data_quality.get("target_score", QUALITY_TARGET_SCORE))
    except (TypeError, ValueError):
        return QUALITY_TARGET_SCORE
    return max(0, min(100, score))


def _product_set(rows: list[dict[str, str]]) -> set[str]:
    return {row.get("producto", "") for row in rows if row.get("producto")}


def _parse_date(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value or "").strip())
    except ValueError:
        return None


def _number(value: object) -> float:
    text = str(value or "").strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return 0.0


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0
